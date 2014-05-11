#!/usr/bin/env 
# -*- coding: utf-8 -*-

genders = {1 : u"Мальчик", 2 : u"Девочка" }

def get_gender_name(gender_id):
    return genders.get(int(gender_id or 0)) or u""