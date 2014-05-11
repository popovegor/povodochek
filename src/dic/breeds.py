#!/usr/bin/env 
# -*- coding: utf-8 -*-



from dic.pets import (pets, DOG_ID, CAT_ID)
from dic.dogs import dogs
from dic.cats import cats
from helpers import (num)

breeds = {}
breeds.update(dogs)
breeds.update(cats)


def get_breed_by_name(name):
    if name:
        name = name.lower()
        return next((breed for breed in breeds.values() 
            if breed['breed_name'].lower() == name), [])
    return None

def get_breed_id_by_name(name):
    breed = get_breed_by_name
    return breed.get("breed_id") if breed else None

def get_breed_by_id(breed_id):
    if breed_id:
        breed_id = num(breed_id)
        return breeds.get(breed_id)
	return None

def get_breed_name(breed_id):
    breed = breeds.get(int(breed_id or 0))
    return breed.get("breed_name") if breed else u""

def get_breed_dog_name(breed_id):
    breed = dogs.get(int(breed_id or 0))
    return breed.get("breed_name") if breed else u""

def get_breed_cat_name(breed_id):
    breed_id = int(breed_id or 0)
    return cats.get(breed_id) or u""
