#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from dic.cities import (get_city)

def povodochek():
	return MongoClient().povodochek

# def aggregate():
# 	db = povodochek()
# 	db.tmp_pets_by_cities.drop()

# 	for adv in db.sales.find():
# 		city = get_city(adv.get('city_id'))
# 		if not city:
# 			continue
# 		city_id = city.get('city_id')
# 		city_name = city.get('city_name')
# 		region_name = city.get('region_name')
# 		breed_id = adv.get('breed_id')
# 		pet_id = adv.get('pet_id')
# 		if not city_name:
# 			raise Exception
# 		query = {'city_id': city_id, 'pet_id': pet_id}
# 		db.tmp_pets_by_cities.update(query, {'$inc': {'count': 1}, \
# 			'$set': {'city_name': city_name, \
# 			'region_name': region_name},  \
# 			'$push': {'breeds': {'breed_id' : breed_id}}}, upsert = True)

# 	db.tmp_pets_by_cities.rename('pets_by_cities', dropTarget=True)
		
			
def aggregate(pet):
	db = povodochek()
	
	advs = db['%s_advs' % pet]
	tmp_pet_by_cities_name = 'tmp_%s_by_cities' % pet
	tmp_pet_by_cities = db[tmp_pet_by_cities_name]
	pet_by_cities_name = '%s_by_cities' % pet
	pet_by_cities = db[pet_by_cities_name]

	tmp_pet_by_cities.drop()

	for adv in advs.find():
		city = get_city(adv.get('city_id'))
		if not city:
			continue
		city_id = city.get('city_id')
		city_name = city.get('city_name')
		region_name = city.get('region_name')
		breed_id = adv.get('breed_id')
		if not city_name:
			continue
		query = {'city_id': city_id}
		tmp_pet_by_cities.update(query, {'$inc': {'count': 1}, \
			'$set': {'city_name': city_name, \
			'region_name': region_name},  \
			'$push': {'breeds': {'breed_id' : breed_id}}}, upsert = True)

	if tmp_pet_by_cities_name in db.collection_names():
		tmp_pet_by_cities.rename(\
			pet_by_cities_name, dropTarget=True)
	else:
		pet_by_cities.drop()

if __name__ == '__main__':
	aggregate("cat")
	aggregate("dog")