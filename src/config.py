#!/usr/bin/python
# -*- coding: utf-8 -*-

UPLOADED_PHOTOS_DEST = '/tmp'
SECRET_KEY = "p\xe6\x9b\xf4\xa9\xfd\x10\x1b\xaaE%\xf2LX\x80\xd7\x91\x8e\x81\xa4\x95\n}\xad"

# email server
MAIL_SERVER = u'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEFAULT_SENDER = u'Поводочек <noreply@povodochek.com>'
MAIL_USERNAME = u'noreply@povodochek.com'
MAIL_PASSWORD = u'gd8HUunlVA3D97rz'
MAIL_SUPPRESS_SEND = False
DOMAIN_NAME = 'povodochek.com'
DOMAIN_NAME_CHECK = True
ADMIN_EMAILS = ['egor@povodochek.com', 'vika@povodochek.com', 'admin@povodochek.com', 'popovegor@gmail.com']

MONGODB_URI = "mongodb://127.0.0.1:27017/?replicaSet=repl_povodochek&connectTimeoutMS=5000&readPreference=secondaryPreferred"


ASSETS_DEBUG = False