#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import (MongoClient, ASCENDING, DESCENDING)
from bson.objectid import ObjectId
from bson.son import SON
from gridfs import GridFS
import re
from datetime import datetime
from uuid import (uuid4, uuid1)
import dic.cities
from helpers import (num, str2date)
from dic.pet_docs import (dog_docs, dog_pedigree_docs)
import sys
import os
import time

mongo = MongoClient().povodochek

users = mongo.users
cat_advs = mongo.cat_advs
dog_advs = mongo.dog_advs
pets_by_cities = mongo.pets_by_cities
top_dog_breeds = mongo.top_dog_breeds
top_cat_breeds = mongo.top_cat_breeds
dog_by_cities = mongo.dog_by_cities
cat_by_cities = mongo.cat_by_cities
cities = mongo.cities
photos = mongo.photos
photos_gridfs = GridFS(mongo, "photos")

def get_user(user_id):
	return users.find_one({'_id':ObjectId(user_id)})

def get_user_by_login(login):
	matcher = re.compile("^" + re.escape(login) + "$", re.IGNORECASE)
	return users.find_one({'login': {'$regex':matcher}})

def get_user_by_email(email):
	matcher = re.compile("^" + re.escape(email) + "$", re.IGNORECASE)
	return users.find_one({'email': {'$regex': matcher}})

def set_user_confirm(user_id):
    new_confirm = str(uuid4()) 
    users.update({'_id': user_id}, \
    	{"$set": {"confirm": new_confirm}})
    return new_confirm

def get_user_by_confirm(confirm):
	return users.find_one({'confirm': confirm})

def activate_user(user_id):
	return users.update({'_id': user_id}, \
		{"$set": {"activated": True, \
		"activate_date" : datetime.utcnow(), "confirm" : ''}})

def get_user_by_asign(asign):
	return users.find_one({'asign': asign})

def asign_user(user):
	return users.update({'_id': user["_id"]}, \
	    {"$set": {'asign': '', 'pwd_hash': user['asign_pwd_hash'], \
	    'asign_pwd_hash': ''} })

def change_user_password(user_id, pwd_hash):
	users.find_and_modify({"_id": ObjectId(user_id)}, \
        {"$set": {"pwd_hash": pwd_hash}})

def confirm_user_email(user_id, email):
	return users.update({"_id": ObjectId(user_id)}, \
		{"$set": {'new_email': None, "email": email}})

def change_user_email(user_id, email):
	return users.find_and_modify({"_id": ObjectId(user_id)}, \
        {"$set": {"new_email": email}})

def signup_user(login, email, pwd_hash, username, confirm, ):
	return users.insert({'login': login, \
		'email': email, \
		'pwd_hash': pwd_hash, \
		'username': username, 'confirm': confirm, \
		'activated': False, 'signup_date': datetime.utcnow()})

def reset_user_password(user, pwd_hash, asign):
    return users.find_and_modify(user, \
        {"$set": {'asign_pwd_hash': pwd_hash, \
        'asign': asign}})


def save_user_contact(user_id, username, city_id, phone, skype):
	return users.update({"_id": ObjectId(user_id)}, {"$set":
	    {"username": username, \
	    "city_id": city_id, \
	    "phone": phone, \
	    'skype' : skype, \
	    }})

def get_dog_adv_for_user(adv_id, user_id):
	return dog_advs.find_one(
        {'_id': {'$in':[adv_id, ObjectId(adv_id)]}, 
        'user_id': {'$in': [user_id, str(user_id)]}})

def get_cat_adv_for_user(adv_id, user_id):
    return cat_advs.find_one(
        {'_id': {'$in':[adv_id, ObjectId(adv_id)]}, 
        'user_id': {'$in': [user_id, str(user_id)]}})

def get_dog_adv(adv_id):
    return dog_advs.find_one({'_id': ObjectId(adv_id)})

def get_cat_adv(adv_id):
    return cat_advs.find_one({'_id': ObjectId(adv_id)})    


def save_dog_adv(user_id, adv_id, form, photonames):

    now = datetime.utcnow()
    # print(str2date(form.birthday.data))

    dog_unset = {}
    dog_set = {
        'breed_id': form.breed.breed_id, \
        "gender_id": form.gender.data, \
        'title': form.title.data, \
        'desc': form.desc.data, \
        'photos': photonames, \
        'price' : form.price.data, \
        'price_haggle' : form.price_haggle.data, \
        'price_hp' : form.price_hp.data, \
        'contract' : form.contract.data, \
        'delivery' : form.delivery.data, \
        'birthday' : str2date(form.birthday.data), \
        'vaccination' : form.vaccination.data, \
        'vetpassport' : form.vetpassport.data, \
        'microchip' : form.microchip.data, \
        "city_id": form.city.city_id, \
        'color' : form.color.data, \
        "phone" : form.phone.data, \
        'username' : form.username.data, \
        "skype" : form.skype.data, \
        'user_id' : str(user_id), \
        'update_date' : now
        }
    if form.doc.data in dog_docs:
    	dog_set['doc_id'] = form.doc.data
    	if form.doc.data in dog_pedigree_docs:
    		dog_set['pedigree'] = form.pedigree.data
    	else:
    		dog_unset['pedigree'] = ""
    	dog_set['father_name'] = form.father_name.data
    	dog_set['father_country_id'] = form.father_country.data
    	dog_set['father_misc'] = form.father_misc.data
    	dog_set['father_pedigree'] = form.father_pedigree.data
    	dog_set['mother_name'] = form.mother_name.data
    	dog_set['mother_country_id'] = form.mother_country.data
        dog_set['mother_misc'] = form.mother_misc.data
    	dog_set['mother_pedigree'] = form.mother_pedigree.data
    	dog_set['breeding'] = form.breeding.data
    	dog_set['show'] = form.show.data
    	dog_set['tatoo'] = form.tatoo.data
    	
    else:
    	dog_unset['doc_id'] = ""
    	dog_unset['pedigree'] = ""
    	dog_unset['father_name'] = ""
    	dog_unset['father_country_id'] = ""
    	dog_unset['father_misc'] = ""
    	dog_unset['father_pedigree'] = ""
    	dog_unset['mother_name'] = ""
        dog_unset['mother_country_id'] = ""
        dog_unset['mother_misc'] = ""
    	dog_unset['mother_pedigree'] = ""
    	dog_unset['breeding'] = ""
    	dog_unset['show'] = ""
    	dog_unset['tatoo'] = ""

    dog = dog_advs.update(\
    	{'_id': ObjectId(adv_id), 'user_id' : str(user_id)}, \
    	{'$set': dog_set, \
    	'$unset': dog_unset, \
    	'$setOnInsert' : {"add_date": now}}, upsert = True)

    return dog


def get_dog_advs_by_user(user_id):
	return dog_advs.find(
	    {'user_id': {'$in' : [str(user_id), user_id]} },\
	    sort = [("update_date", DESCENDING), \
        ("add_date", DESCENDING)])

def get_cat_advs_by_user(user_id):
    return cat_advs.find(
        {'user_id': {'$in' : [str(user_id), user_id]} },\
        sort = [("update_date", DESCENDING), \
        ("add_date", DESCENDING)])

def get_top_dog_advs():
	return [adv for adv in top_dog_breeds.find( \
		sort = [('count', DESCENDING)], limit = 15)]

def get_top_cat_advs():
	return [adv for adv in top_cat_breeds.find( \
		sort = [('count', DESCENDING)], limit = 15)]

def get_locations_for_typeahead(query, limit):
	matcher = re.compile("^" + re.escape(query), re.IGNORECASE)
	locations = [ city.get("city_region")  \
	    for city in cities.find(\
	    	{'city_region': {"$regex": matcher}}, \
	    	limit = limit, \
	    	fields = ["city_region", "city_size", "city_name"], \
	    	sort = [('city_size', DESCENDING)] )]
	return locations


def get_near_cities(city = None, distance = None):
    near_cities = []
    if city:
        search_city = cities.find_one(\
        	{'city_id': city.get('city_id')})
        if search_city and distance and search_city.get("location"):
            location = search_city.get("location")
            geoNear = mongo.command(SON([("geoNear",  "cities"), \
            	("near", location), ( "spherical", True ), \
            	("maxDistance", distance * 1000), ("limit", 5000)]))
            near_cities = [(geo["obj"], geo["dis"]) \
            for geo in geoNear.get("results")]
    return near_cities

def find_dog_advs(
	breed_id = None, gender_id = None, city = None, \
    distance = None, photo = False, price_from = None, \
    price_to = None, \
	sort = None, skip = None, limit = None):

    _filter = {}
    extend_filter = lambda k,v: _filter.update({k:v}) if v else None
    if num(gender_id):
        extend_filter('$or', [{'gender_id' : num(gender_id)}, \
        	{'gender_id' : {'$exists': False}}])

    extend_filter("breed_id", num(breed_id))

    price_form = num(price_from)
    price_to = num(price_to)
    if price_from or price_to:
        extend_filter("price", \
            {"$gte" : price_from if price_from > 0 else 0,\
             "$lte" : price_to if price_to else sys.maxint })
    near_cities = []
    if city and distance:
        near_cities = get_near_cities(city, distance)
        extend_filter("city_id", {"$in": [city.get("city_id") \
        	for city, dis in near_cities]})

    if photo:
        extend_filter("photos", {"$nin": [None, []]})
    sortby = [("update_date", -1)]
    if sort == 1:
        sortby = [("price", -1)]
    elif sort == 2:
        sortby = [("price", 1)]
    else:
        sortby = [("update_date", -1)]
    print("filter %s" % _filter)
    print("sort %s" % sortby)
    print(limit)
    total = dog_advs.count()
    query = dog_advs.find(SON(_filter),\
        limit = limit or total,\
        skip = skip or 0,\
        sort = sortby)
    count = query.count()
    advs = [adv for adv in query]

    if near_cities:
        for adv in advs:
            adv_city_id = adv.get("city_id")
            (near_city, dist) = next( ((city, dist) for city, dist in near_cities if city["city_id"] == adv_city_id), (None, None))
            adv["distance"] = int(round(dist / 1000, 0))

    return (advs, count, total)


def find_cat_advs(pet_id = 2, gender_id = None, \
	breed_id = None, city = None, distance = None, \
	photo = False, price_from = None, price_to = None, \
	sort = None, skip = None, limit = None):

    _filter = {}
    extend_filter = lambda k,v: _filter.update({k:v}) if v else None
    extend_filter("pet_id", num(pet_id))
    if num(gender_id):
        extend_filter('$or', [{'gender_id' : num(gender_id)}, \
        	{'gender_id' : {'$exists': False}}])

    extend_filter("breed_id", num(breed_id))

    price_form = num(price_from)
    price_to = num(price_to)
    if price_from or price_to:
        extend_filter("price", \
            {"$gte" : price_from if price_from > 0 else 0,\
             "$lt" : price_to if price_to else sys.maxint })
    near_cities = []
    if city and distance:
        near_cities = get_near_cities(city, distance)
        extend_filter("city_id", {"$in": [city.get("city_id") \
        	for city, dis in near_cities]})

    if photo:
        extend_filter("photos", {"$nin": [None, []]})
    sortby = [("update_date", -1)]
    if sort == 1:
        sortby = [("price", -1)]
    elif sort == 2:
        sortby = [("price", 1)]
    else:
        sortby = [("update_date", -1)]
    print("filter %s" % _filter)
    print("sort %s" % sortby)
    print(limit)
    total = cat_advs.count()
    query = cat_advs.find(SON(_filter),\
        limit = limit or total,\
        skip = skip or 0,\
        sort = sortby)
    count = query.count()
    advs = [adv for adv in query]

    if near_cities:
        for adv in advs:
            adv_city_id = adv.get("city_id")
            (near_city, dist) = next( ((city, dist) for city, \
            	dist in near_cities if \
            	city["city_id"] == adv_city_id), (None, None))
            adv["distance"] = int(round(dist / 1000, 0))

    return (advs, count, total)


def get_photo(filename):
    try:
        filename = filename.lower()
        name = os.path.basename(filename)
        # print("get_photo", name)
        photo = photos.files.find_one({"filename" : filename}, \
        	fields= ['_id'])
        # print(photo)
        with photos_gridfs.get(photo.get('_id')) as gridfs_file:
            return (gridfs_file.name, gridfs_file.read()) 
    except:
        print(sys.exc_info())
    
    return (None, None)

def save_photo(file):
    try:
        print("filename", file.name)
        return photos_gridfs.put(file.read(), \
        	filename = os.path.basename(file.name))
    except:
       print(sys.exc_info())

def get_short_adv_id(adv):
    gen_time_adv = adv.get('_id').generation_time
    user_id = adv.get('user_id')
    gen_time_user = ObjectId(user_id).generation_time
    short_adv_id = int(time.mktime(gen_time_adv.timetuple()))
    short_user_id = int(time.mktime(gen_time_user.timetuple()))
    # print(user_id)
    # print(short_adv_id)
    # print(short_user_id)
    # print(short_adv_id ^ short_user_id)
    return short_adv_id ^ short_user_id


def remove_dog_adv(adv_id, user_id):
    adv = dog_advs.find_one(
        {'_id': {'$in':[adv_id, ObjectId(adv_id)]}, 
        'user_id': {'$in': [user_id, \
        str(user_id)]}})
    if adv:
        dog_advs.remove(adv)
    return adv


def get_dog_advs_for_mosaic(skip, limit):
    return dog_advs.find(
        {"photos": {"$nin": [None, []]} }, \
        skip = skip, \
        fields = ["_id", "photos", "title", \
        "price", "breed_id", "update_date", "add_date"], \
        limit = limit, \
        sort = [('update_date', DESCENDING), \
        ("add_date", DESCENDING)])

def get_cat_advs_for_mosaic(skip, limit):
    return cat_advs.find(
        {"photos": {"$nin": [None, []]} }, \
        skip = skip, \
        fields = ["_id", "photos", "title", \
        "price", "breed_id", "update_date", "add_date"], \
        limit = limit, \
        sort = [('update_date', DESCENDING), \
        ("add_date", DESCENDING)])

def get_dog_by_cities():
    return sorted([adv for adv in dog_by_cities.find()], \
        key = lambda x : x['city_name'])

def get_cat_by_cities():
    return sorted([adv for adv in cat_by_cities.find()], \
        key = lambda x : x['city_name'])

def admin_get_users(limit, skip):
    return users.find(sort = [('signup_date', DESCENDING)], \
        limit = limit, skip = skip)