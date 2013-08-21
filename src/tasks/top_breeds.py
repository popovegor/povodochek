#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient 

def povodochek():
	return MongoClient().povodochek

def aggregate():
	db = povodochek()
	db.tmp_top_breeds.drop()

	for adv in db.sales.find():
		breed_id = adv.get('breed_id')
		pet_id = adv.get('pet_id')
		query = {'pet_id': pet_id, 'breed_id' : breed_id}
		db.tmp_top_breeds.update(query, {'$inc': {'count': 1}, \
			'$set': {'pet_id': pet_id, \
			'breed_id': breed_id},  }, upsert = True)

	db.tmp_top_breeds.rename('top_breeds', dropTarget=True)
		
import sys
			
if __name__ == '__main__':
    aggregate()