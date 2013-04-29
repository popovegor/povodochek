#!/usr/bin/env 
# -*- coding: utf-8 -*-

ages = [u"Малый", u"Взрослый"]


from pymongo import MongoClient
from bson.objectid import ObjectId

if __name__ == '__main__':
    mongo = MongoClient()
    for age in ages:
        mongo.povodochek.ages.update({'name':age}, {'name':age}, upsert=True)