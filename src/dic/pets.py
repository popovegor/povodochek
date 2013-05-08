#!/usr/bin/env 
# -*- coding: utf-8 -*-

pets = [(u"Собака", 1), (u"Кошка", 2)]

from pymongo import (MongoClient, ASCENDING)

if __name__ == "__main__":
    mongo = MongoClient()
    for (name, id) in pets:
        mongo.povodochek.pets.update({"id":id}, {'$set':{"name": name, "id": id}}, upsert=True)
    for pet in mongo.povodochek.pets.find():
        print(pet)

    mongo.povodochek.pets.ensure_index([("id", ASCENDING)])