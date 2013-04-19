#!/usr/bin/env 
# -*- coding: utf-8 -*-

pets = [u"Собаки", u"Кошки"]

from pymongo import MongoClient

if __name__ == "__main__":
    mongo = MongoClient()
    for pet in pets:
        mongo.povodochek.pets.update({"name":pet}, {'$set':{"name": pet}}, upsert=True)
        print()
    for pet in mongo.povodochek.pets.find():
        print(pet)