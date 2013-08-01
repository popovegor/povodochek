#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient 
from dic.cities import cities

def povodochek():
	return MongoClient().povodochek

def aggregate_pets_by_cities():
	db = povodochek()
	db.tmp_pets_by_cities.drop()

	for adv in db.sales.find():
		city_id = adv.get('city_id')
		breed_id = adv.get('breed_id')
		pet_id = adv.get('pet_id')
		city_name = next((city[0] for city in cities if city[1] == city_id), "")
		if not city_name:
			raise Exception
		query = {'city_id': city_id, 'pet_id': pet_id}
		db.tmp_pets_by_cities.update(query, {'$inc': {'count': 1}, \
			'$set': {'city_name': city_name},  \
			'$push': {'breeds': {'breed_id' : breed_id}}}, upsert = True)

	db.tmp_pets_by_cities.rename('pets_by_cities', dropTarget=True)
		
			

if __name__ == '__main__':
	aggregate_pets_by_cities()