"""
This file defines the actions related to index and homepages
possibly should be in the controller as users idk tho
"""
import base64
import pathlib
import uuid

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from pydal.validators import *
from ..common import db, session, T, cache, auth, signed_url
from ..models import Helper



def get_info(users):
    if type(users) is not list:
        return

    for user in users:
        person = db(db.auth_user.id == user.get('user')).select().first()
        user["full_name"] = "%s %s" % \
                            (person.get('first_name'), person.get('last_name')) if person else "Unknown"
        user['tags_list'] = ", ".join(Helper.get_user_tag_by_name(user))
        user['tags_list'] = user['tags_list'][:40]
        user['bio'] = user['bio'][:40]
        user['role'] = user['role'].capitalize()
        user['user_email'] = person.get('email')




@action('admin')
@action.uses('admin.html', signed_url, auth.user)
def admin():
    user = db(db.users.user == Helper.get_user()).select().first()
    if user == None or user['role'] != "admin":
        redirect(URL('index'))



    return dict(
        get_users_url=URL('admin/get_users'),
        get_tags_url=URL('admin/get_tags'),
        get_unapproved_users_url=URL('admin/get_unapproved_users'),
        get_unapproved_tags_url=URL('admin/get_unapproved_tags'),
        set_role_url=URL('admin/set_role', signer=signed_url),
        set_tag_url=URL('admin/set_tag', signer=signed_url),
        user_email=Helper.get_user_email(),
        username=Helper.get_user_title(),
        user=auth.get_user()
    )

@action('admin/get_unapproved_tags')
@action.uses(auth.user)
def get_unapproved_tags():
    tags = db(db.global_tag.approved == False).select().as_list()

    return dict(tags=tags)

@action('admin/get_unapproved_users')
@action.uses(auth.user)
def get_unapproved_users():
    users = db(db.users.role == "unapproved").select().as_list()

    get_info(users)
    return dict(users=users)

@action('admin/get_users')
@action.uses(auth.user)
def get_admin_users():
    users = db(db.users).select().as_list()

    get_info(users)
    return dict(users=users)


@action('admin/get_tags')
@action.uses(auth.user)
def get_admin_tags():
    tags = db(db.global_tag).select().as_list()
    return dict(tags=tags)


@action('admin/set_role', method="POST")
@action.uses(signed_url.verify(), auth.user, db)
def set_role():
    row = db(db.users.id == request.json.get('id')).select().first()

    if row is None:
        return

    row.update_record(role=request.json.get('role').lower())
    return "ok"


@action('admin/set_tag', method="POST")
@action.uses(signed_url.verify(), auth.user, db)
def set_tag():
    tag = db(db.global_tag.id == request.json.get('id')).select().first()

    if tag is None:
        return

    tag.update_record(approved=request.json.get('approved'))
    return "ok"
