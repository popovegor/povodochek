#!/usr/bin/env 
# -*- coding: utf-8 -*-

MALE = 1
FEMALE = 2

genders = {MALE : u"Мальчик", FEMALE : u"Девочка" }

def get_gender_name(gender_id):
    return genders.get(int(gender_id or 0)) or u""