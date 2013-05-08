#!/usr/bin/env 
# -*- coding: utf-8 -*-

ages = [(u"Малыш", 1), (u"Взрослый", 2)]

from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId

if __name__ == '__main__':
    mongo = MongoClient()
    for (name, id)  in ages:
        mongo.povodochek.ages.update({'id':id}, {'name':name, 'id': id}, upsert=True)

    mongo.povodochek.ages.ensure_index([('id', ASCENDING)])