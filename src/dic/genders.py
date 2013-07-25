#!/usr/bin/env 
# -*- coding: utf-8 -*-

genders = {1:u"Мальчик", 2:u"Девочка"}


from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId

if __name__ == '__main__':
    mongo = MongoClient()

    # mongo.povodochek.breeds.drop()
    for (name, id) in genders:
        mongo.povodochek.genders.update({'id':id}, {'name':name, "id": id}, upsert=True)
    for gender in mongo.povodochek.genders.find():
        print(gender)

    mongo.povodochek.genders.ensure_index([("id", ASCENDING)])
