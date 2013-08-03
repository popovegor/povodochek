#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient 
from dic.cities import (cities, get_city_region)

def povodochek():
	return MongoClient().povodochek

def aggregate_pets_by_cities():
	db = povodochek()
	db.tmp_pets_by_cities.drop()

	for adv in db.sales.find():
		city = db.cities.find_one({'city_id':adv.get('city_id')})
		city_id = city.get('city_id')
		city_name = city.get('city_name')
		region_name = city.get('region_name')
		breed_id = adv.get('breed_id')
		pet_id = adv.get('pet_id')
		if not city_name:
			raise Exception
		query = {'city_id': city_id, 'pet_id': pet_id}
		db.tmp_pets_by_cities.update(query, {'$inc': {'count': 1}, \
			'$set': {'city_name': city_name, \
			'region_name': region_name},  \
			'$push': {'breeds': {'breed_id' : breed_id}}}, upsert = True)

	db.tmp_pets_by_cities.rename('pets_by_cities', dropTarget=True)
		
			

if __name__ == '__main__':
	aggregate_pets_by_cities()