# users.py - backend code for users page and related functions
# part of Sluggo, a free and open source issue tracker
# Copyright (c) 2020 Slugbotics - see git repository history for individual committers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

"""
This file defines the actions related to index and homepages
possibly should be in the controller as users idk tho
"""
import base64
import pathlib
import uuid
import os
import json

from py4web import action, request, abort, redirect, URL, Field, response
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from pydal.validators import *
from ..common import db, session, T, cache, auth, signed_url
from ..helper import Helper
from ..components import userValidator


@action('users')
@action.uses(userValidator, 'users.html', signed_url, auth.user)
def users():

    user = db(db.users.user == Helper.get_user()).select().first()
    if user == None:
        redirect(URL('create_profile'))
    return dict(

        get_users_url=URL('users/get_users', signer=signed_url),
        get_icons_url=URL('users/get_icons', signer=signed_url),
        edit_user_url=URL('edit_user', signer=signed_url),
        user_email=Helper.get_user_email(),
        username=Helper.get_user_title(),
        user=auth.get_user()
    )


@action('users/<id>')
@action.uses(userValidator, 'specific_user.html', signed_url, auth.user )
def specific_user(id=None):

    return dict(

        show_user_url = URL('users/show_user', signer=signed_url),
        get_icons_url = URL('users/get_icons', signer=signed_url),
        set_icons_url=URL('users/set_icons', signer=signed_url),
        edit_user_url = URL('edit_user', signer=signed_url),
        user_email = Helper.get_user_email(),
        username = Helper.get_user_title(),
        user=auth.get_user(),
        id=id,
    )


@action('create_profile', method=['GET'])
@action.uses('create_profile.html', db, session, auth.user, signed_url)
def create_user():
    user = db(db.users.user == Helper.get_user()).select().first()
    if user != None:
        redirect(URL('index'))

    return dict(
        add_user_url=URL('add_user', signer=signed_url),
        user=auth.get_user(),
        username=Helper.get_user_title(),
        admin=db(db.users).isempty(),
        tags=Helper.get_tags_list_approved(),
    )


@action('add_user', method="POST")
@action.uses(signed_url.verify(), auth.user, db)
def add_user():
    role = "admin" if db(db.users).isempty() else "unapproved"
    u_id = db.users.insert(
        role=role,
        bio=request.json.get('bio'),
        user=Helper.get_user(),
        icon='default.jpg',
    )

    tags = request.json.get('tags')

    for tag in tags:
        # get the tag if it is stored in database
        t_id = db(db.global_tag.tag_name == tag.lower()).select().first()

        if (t_id == None):
            # if tag isn't stored in database, create new tags
            t_id = db.global_tag.insert(tag_name=tag.lower(),approved=(True if role== "admin" else False))

        # now we insert tags in this many to many relationship
        db.user_tag.insert(
            user_id=u_id,
            tag_id=t_id
        )
    return "ok"


def attach_user_information(users):
    if type(users) is not list:
        return

    for user in users:
        person = db(db.auth_user.id == user.get('user')).select().first()
        user["full_name"] = "%s %s" % \
                            (person.get('first_name'), person.get('last_name')) if person else "Unknown"
        user['tags_list'] = Helper.get_user_tag_by_name(user)
        user['user_email'] = person.get('email')
        user['role'] = user['role'].capitalize()


@action('users/get_users')
@action.uses(signed_url.verify(), auth.user, db)
def get_users():
    users = db(db.users).select().as_list()

    attach_user_information(users)
    return dict(users=users, tags=Helper.get_tags_list_approved())


@action('get_users_by_tag_list', method="POST")
@action.uses(auth.user, db)
def get_users_by_tag_list():
    tag_list = request.json.get('tag_list')

    if type(tag_list) is not list:
        return dict(users=list())

    """ annoying ass select statement"""
    tag_users = db(db.user_tag.tag_id in tag_list).select(
        db.users.id, db.users.user, db.users.role, db.users.bio,
        db.auth_user.first_name, db.auth_user.last_name, db.auth_user.email,
        left=(db.users.on(db.users.id == db.user_tag.user_id),
              db.auth_user.on(db.auth_user.id == db.users.user)),
        groupby=db.users.id).as_list()

    tag_users = list(map(lambda x: {**x["users"], **x["auth_user"]}, tag_users))
    print(tag_users)

    for user in tag_users:
        user["full_name"] = "%s %s" % \
                            (user.get('first_name'), user.get('last_name')) if user else "Unknown"
        user['user_email'] = user.get('email')

    return dict(users=tag_users)




@action('users/show_user')
@action.uses(auth.user, db)
def show_user():
    id = request.params.id
    user = db(db.users.id == id).select().as_list()[0]
    person = db(db.auth_user.id == user.get('user')).select().first()

    user["full_name"] = "%s %s" % \
                        (person.get('first_name'), person.get('last_name')) if person else "Unknown"
    user['tags_list'] = Helper.get_user_tag_by_name(user)
    user['user_email'] = person.get('email')
    user['role'] = user['role'].capitalize()
    return dict(user=user,tags=Helper.get_tags_list_approved() )


@action('edit_user', method="POST")
@action.uses(signed_url.verify(), auth.user, db)
def edit_user():
    row = db(db.users.id == request.json.get('id')).select().first()
    user = db(db.auth_user.id == row.get('user')).select().first()

    row.update_record(bio=request.json.get('bio'),
                      role=request.json.get('role').lower())

    names = request.json.get('full_name').split()

    first_name = names[0]
    last_name = " ".join(names[1:])

    tags = request.json.get('tags_list')
    old_tags = Helper.get_user_tag_by_name(row)

    missing = set(old_tags).difference(tags)
    added = set(tags).difference(old_tags)

    # these tags are to be deleted from the user
    for tag in missing:
        # get the tag if it is stored in database
        t_id = db(db.global_tag.tag_name == tag.lower()).select().first()

        if (t_id == None):
            # if tag isn't stored in database, create new tags
            t_id = db.global_tag.insert(tag_name=tag.lower())

        db((db.user_tag.user_id == request.json.get('id')) & (db.user_tag.tag_id == t_id)).delete()

    # these tags are to be added to the user
    for tag in added:
        # get the tag if it is stored in database
        t_id = db(db.global_tag.tag_name == tag.lower()).select().first()

        if (t_id == None):
            # if tag isn't stored in database, create new tags
            t_id = db.global_tag.insert(tag_name=tag.lower(),approved=(True if row["role"] == "admin" else False))

        # now we insert tags in this many to many relationship
        db.user_tag.update_or_insert((db.user_tag.user_id == request.json.get('id')) & (db.user_tag.tag_id == t_id),
                                     user_id=request.json.get('id'),
                                     tag_id=t_id
                                     )

    user.update_record(first_name=first_name, last_name=last_name)
    return "ok"


@action('users/get_icons')
@action.uses(auth.user, db)
def get_usr_icons():
    """Returns a single image, URL encoded."""
    # Reads the image.
    u_id = request.params.id
    row = db(db.users.id == u_id).select().first()
    img_name = "default.jpg"
    if row != None:
        img_name = row["icon"]

    img_file = pathlib.Path(__file__).resolve().parent.parent / 'static' / 'images' / 'profile_pics' / img_name
    if not img_file.exists():
        img_file = pathlib.Path(__file__).resolve().parent.parent / 'static' / 'images' / 'profile_pics' /  "default.jpg"
    with img_file.open(mode='rb') as f:
        img_bytes = f.read()
        b64_image = base64.b64encode(img_bytes).decode('utf-8')
    # Returns the image bytes, base64 encoded, and with the correct prefix.
    return dict(imgbytes="data:image/jpeg;base64," + b64_image)


@action('users/set_icons', method="POST")
@action.uses(signed_url.verify(), auth.user, db)
def set_usr_icons():
    id = request.forms.get('id')
    row = db(db.users.id == id).select().first()

    if row == None:
        return

    Helper.cleanup_icon(id)

    file_name = request.forms.get('name')
    data = request.files.get('file')
    if file_name and data and data.file:
            raw = data.file.read() # This is dangerous for big files
            _, ext = os.path.splitext(data.filename)
            img_name = uuid.uuid4().hex + ext
            path = pathlib.Path(__file__).resolve().parent.parent / 'static' / 'images' / 'profile_pics' / img_name
            path.write_bytes(raw)
            row.update_record(icon=img_name)
    else:
        row.update_record(icon='default.jpg')
    return "ok"
