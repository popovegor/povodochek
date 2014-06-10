#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask_login import (UserMixin, AnonymousUser)
import db

class User(UserMixin):
    def __init__(self, user):
        # self.name = user.get('login')
        self.username = user.get('username')
        self.surname = user.get('surname')
        self.id = str(user.get('_id'))
        self.active = user.get('activated')
        self.email = user.get('email')
        self.new_email = user.get('new_email')
        self.city_id = user.get('city_id')
        self.phone = user.get('phone')
        self.skype = user.get('skype')
        self.kennel_name = user.get('kennel_name')
        self.site_link = user.get('site_link')
        self.dog_advs_cnt = user.get('dog_advs_cnt')
        self.cat_advs_cnt = user.get('cat_advs_cnt')

    def is_signed(self):
        return True

    def is_active(self):
        return True or self.active

    def get_fullname(self):
        fullname = self.username
        if self.surname:
            fullname += " " + self.surname
        return fullname

class Anonymous(AnonymousUser):
    def __init__(self):
        self.name = u"Anonymous"
        self.username = u""
        self.email = u""
        self.active = False

    def is_signed(self):
        return False

    def get_fullname(self):
    	return u"Пользователь"


def get_user(user_id):
	user = db.get_user(user_id)
	if user:
		return User(user)
	else:
		return Anonymous()