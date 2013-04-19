#!/usr/bin/env 
# -*- coding: utf-8 -*-

genders = [u"Мальчик", u"Девочка"]


from pymongo import MongoClient
from bson.objectid import ObjectId

if __name__ == '__main__':
    mongo = MongoClient()

    # mongo.povodochek.breeds.drop()
    for gender in genders:
        mongo.povodochek.genders.update({'name':gender}, {'name':gender}, upsert=True)
    for gender in mongo.povodochek.genders.find():
        print(gender)