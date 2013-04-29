#!/usr/bin/python
# -*- coding: utf-8 -*-

from werkzeug.security import generate_password_hash, \
     check_password_hash

def hash_password(pwd):
    return generate_password_hash(pwd)

def check_password(pwd_hash, pwd):
    return check_password_hash(pwd_hash, pwd)