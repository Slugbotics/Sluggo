# models.py - pyDAL models file for Sluggo
# part of Sluggo, a free and open source issue tracker
# Copyright (c) 2020 Slugbotics - see git repository history for individual committers
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#

"""
This file defines the database models
"""

from .common import db, Field, auth
from .helper import Helper
from pydal.validators import *


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#


# TODO: Do we want separate projects to be included in the db?

db.define_table(
    'users',
    Field('user', 'reference auth_user', default=Helper.get_user()),
    Field('role', 'text'),
    Field('bio', 'text'),
    Field('icon')
)

# db.define_table(
#     'ticket',
#     Field('title'),
#     Field('due_date'), # TODO find date format + serialize
#     Field('description')

#     # Additional properties that must be queried:
#     # Dependenencies -> select all children from ticket_rels
#     # Dependents -> select all parents from ticket_rels
#     # Percentage -> BFS and give proportion (should cache longterm)
# )


db.define_table(
    'tickets',
    Field('user_email', default=Helper.get_user_email),
    Field('assigned_user',  'reference auth_user'),
    Field('ticket_title', 'text'),
    Field('ticket_text', 'text'),
    Field('created', 'datetime', default=Helper.get_time),
    Field('started', 'datetime'),
    Field('completed', 'datetime'),
    Field('due', 'date'),
)

db.define_table(  # credit tdimhcsleumas for design
    'sub_tickets',
    Field('parent_id',  'reference tickets'),
    Field('child_id',  'reference tickets')
)

db.define_table(  #
    'global_tag',
    Field('tag_name', 'text'),
    Field('approved', 'boolean', default=False)
)

db.define_table(
    'ticket_tag',
    Field('ticket_id',  'reference tickets'),
    Field('tag_id',  'reference global_tag')
)

db.define_table(
    'user_tag',
    Field('user_id',  'reference users'),
    Field('tag_id',  'reference global_tag'),
)

# MARK: Homepage / pinning tickets
db.define_table(
    'user_pins',
    Field('auth_user_id',  'reference auth_user'),  # reference the auth not our custom work
    Field('ticket_id',  'reference tickets')
)

db.define_table(
    'comment',
    Field('ticket_id',  'reference tickets'),
    Field('user_id',  'reference auth_user', default=Helper.get_user()),
    Field('content', 'text'),
    Field('created', 'datetime', default=Helper.get_time())
)

db.define_table(
    'events',
    Field('created', 'datetime', default=Helper.get_time()),
    Field('type', 'string'),
    Field('description', 'string'),
    Field('related_ticket', 'reference tickets'),
    Field('action_user', 'reference auth_user', default=Helper.get_user())
)

# TODO tags, roles, other fun things that require relationships

# TODO readables vs not readables (relevant? can we even use default forms?)
# TODO requirements for forms (again, is this even relevant?)

# TODO: We need deletes to cascade for things like events
db.sub_tickets.ondelete = 'NO ACTION'  # We don't want relationships to affect tickets
db.tickets.ondelete = 'NO ACTION'
db.ticket_tag.ondelete = 'NO ACTION'
db.user_tag.ondelete = 'NO ACTION'
db.user_pins.ondelete = 'NO ACTION'
db.comment.ondelete = 'NO ACTION'
db.commit()
