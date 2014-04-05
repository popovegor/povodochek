#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient 
from dic.breeds import (dogs, cats)


def povodochek():
	return MongoClient().povodochek

def aggregate(pet):
	db = povodochek()
	breeds = cats if pet == 'cat' else dogs
	advs = db['%s_advs' % pet]
	tmp_top_breeds_name = 'tmp_top_%s_breeds' % pet
	tmp_top_breeds = db[tmp_top_breeds_name]
	top_breeds_name = 'top_%s_breeds' % pet
	top_breeds = db[top_breeds_name]
	tmp_top_breeds.drop()

	for (breed_id, breed_name) in breeds.items():
		count = advs.find({'breed_id':breed_id}).count()	
		tmp_top_breeds.insert({'count': count, 
			'breed_id': breed_id, 'breed_name': breed_name})

	if tmp_top_breeds_name in db.collection_names():
		tmp_top_breeds.rename(\
			top_breeds_name, dropTarget=True)
	else:
		top_breeds.drop()


		
import sys
			
if __name__ == '__main__':
    aggregate('cat')
    aggregate('dog')