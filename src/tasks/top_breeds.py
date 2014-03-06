#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient 

def povodochek():
	return MongoClient().povodochek

def aggregate(pet):
	db = povodochek()
	advs = db['%s_advs' % pet]
	tmp_top_breeds_name = 'tmp_top_%s_breeds' % pet
	tmp_top_breeds = db[tmp_top_breeds_name]
	top_breeds_name = 'top_%s_breeds' % pet
	top_breeds = db[top_breeds_name]
	tmp_top_breeds.drop()

	for adv in advs.find():
		breed_id = adv.get('breed_id')
		query = {'breed_id' : breed_id}
		tmp_top_breeds.update(query, \
			{'$inc': {'count': 1}, \
			'$set': {'breed_id': breed_id},  }, \
			upsert = True)

	if tmp_top_breeds_name in db.collection_names():
		tmp_top_breeds.rename(\
			top_breeds_name, dropTarget=True)
	else:
		top_breeds.drop()


	

		
import sys
			
if __name__ == '__main__':
    aggregate('cat')
    aggregate('dog')