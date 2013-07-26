#!/usr/bin/env 
# -*- coding: utf-8 -*-

pets = {1: u"Собака", 2: u"Кошка"}

def get_pet_name(pet_id):
    return pets.get(pet_id) or ""