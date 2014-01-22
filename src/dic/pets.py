#!/usr/bin/env 
# -*- coding: utf-8 -*-

DOG_ID = 1
CAT_ID = 2

pets = {DOG_ID: u"Собака", CAT_ID: u"Кошка"}

def get_pet_name(pet_id):
    return pets.get(pet_id) or ""