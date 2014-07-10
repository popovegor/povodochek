#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_login import (UserMixin, AnonymousUserMixin)
import db

class User(UserMixin):
    def __init__(self, user_id):
        self.id = unicode(user_id)

class Anonymous(AnonymousUserMixin):
    def __init__(self):
        pass

def get_user(user_id):
    user = db.get_user(user_id)
    if user and not user.get("banned"):
        u = User(user_id)
        u.username = user.get('username')
        u.surname = user.get('surname')
        u.activated = user.get('activated')
        u.email = user.get('email')
        u.new_email = user.get('new_email')
        u.city_id = user.get('city_id')
        u.phone = user.get('phone')
        u.skype = user.get('skype')
        u.kennel_name = user.get('kennel_name')
        u.site_link = user.get('site_link')
        u.counters = {
            "dog_advs": db.get_dog_advs_by_user(user_id).count(),
            "dog_advs_archived": db.get_dog_advs_archived_by_user(user_id).count(),
            "cat_advs" : db.get_cat_advs_by_user(user_id).count(),
            "cat_advs_archived": db.get_cat_advs_archived_by_user(user_id).count()
            }
        return u
    else:
        return Anonymous()