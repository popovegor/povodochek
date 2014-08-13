#!/usr/bin/python
# -*- coding: utf-8 -*-


from dic.cities import cities
from dic.regions  import regions
from dic.geo import (get_region_by_city_id, format_city_region, get_region_by_id, get_city_by_id, get_region_name)
import db
import sys
from pymongo import (GEO2D, GEOSPHERE, ASCENDING, DESCENDING)
from bson.objectid import ObjectId
from dic.breeds import (dogs, cats, get_breed_name)
from forms import (Dog)
from form_helper import (calc_attraction)
from mailing import mailer
from helpers import (log_exception)
import config

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

if not config.DEBUG:
    from ThreadedSMTPHandler import ThreadedSMTPHandler
    mail_handler = ThreadedSMTPHandler(subject = 'povodochek:error:tasks')
    mail_handler.setLevel(logging.ERROR)
    logger.addHandler(mail_handler)

@log_exception(logger = logger)
def run_db_tasks():
    rebuild_advs_by_geos('cat')
    rebuild_advs_by_geos('dog')
    rebuild_geos()
    rebuild_typeahead_geos()
    rebuild_typeahead_breeds()
    rebuild_breeds_rating('cat')
    rebuild_breeds_rating('dog')

@log_exception(logger = logger)
def rebuild_breeds_rating(pet):
    breeds = cats if pet == 'cat' else dogs
    advs = db.povodochek['%s_advs' % pet]
    tmp_top_breeds_name = '%s_breeds_rating_tmp' % pet
    tmp_top_breeds = db.povodochek[tmp_top_breeds_name]
    top_breeds_name = '%s_breeds_rating' % pet
    top_breeds = db.povodochek[top_breeds_name]
    tmp_top_breeds.drop()


    for k in advs.aggregate({
        '$group' : 
        {'_id': '$breed_id',
        'count': {'$sum':1}, 
        'min_price' : {'$min': '$price'}, 
        'max_price' : {'$max' : '$price'}, 
        'avg_price' : {'$avg' : '$price'}, 
        }}, allowDiskUse = True)["result"]:
        breed_name = get_breed_name(k['_id'])
        tmp_top_breeds.insert({'count': k['count'], 
            'breed_id': int(k['_id']), 
            'breed_name': breed_name, 
            'min_price' : k['min_price'],
            'max_price' : k['max_price'], 
            'avg_price' : k['avg_price']
            })

    if tmp_top_breeds_name in db.povodochek.collection_names():
        tmp_top_breeds.rename(top_breeds_name, dropTarget=True)
    else:
        top_breeds.drop()

@log_exception(logger = logger)
def rebuild_typeahead_breeds():
    db.povodochek.typeahead_dog_breeds_tmp.drop()
    db.povodochek.typeahead_cat_breeds_tmp.drop()

    group_dog_breeds = { 
        k.get('_id'):k.get('count') 
        for k in db.dog_advs.aggregate({'$group' : 
            {'_id':'$breed_id', 'count': {'$sum':1}}})["result"] }

    group_cat_breeds = { 
        k.get('_id'):k.get('count') 
        for k in db.cat_advs.aggregate({'$group' : 
            {'_id':'$breed_id', 'count': {'$sum':1}}})["result"] }

    typeahead_dog_breeds = []
    for breed in dogs.values():
        breed_id = breed.get("breed_id")
        breed_name = breed.get("breed_name")
        rating = group_dog_breeds.get(breed_id) or 0
        typeahead_dog_breeds.append({'rating':rating, 
        'breed_id': breed_id, 
        'breed_name' : breed_name, 
        'breed_name_search' : breed_name.lower()})

    typeahead_cat_breeds = []
    for breed in cats.values():
        breed_id = breed.get("breed_id")
        breed_name = breed.get("breed_name")
        rating = group_cat_breeds.get(breed_id) or 0
        typeahead_cat_breeds.append({'rating':rating, 
        'breed_id': breed_id, 
        'breed_name' : breed_name, 
        'breed_name_search' : breed_name.lower()})

    db.povodochek.typeahead_dog_breeds_tmp.insert(typeahead_dog_breeds)
    db.povodochek.typeahead_cat_breeds_tmp.insert(typeahead_cat_breeds)


    db.povodochek.typeahead_dog_breeds_tmp.ensure_index([('breed_name_search', ASCENDING)])

    db.povodochek.typeahead_cat_breeds_tmp.ensure_index([('breed_name_search', ASCENDING)])

    db.povodochek.typeahead_dog_breeds_tmp.rename('typeahead_dog_breeds', dropTarget=
        'typeahead_dog_breeds' in db.povodochek.collection_names())

    db.povodochek.typeahead_cat_breeds_tmp.rename('typeahead_cat_breeds', dropTarget=
        'typeahead_cat_breeds' in db.povodochek.collection_names())


@log_exception(logger = logger)
def rebuild_typeahead_geos():
    db.povodochek.typeahead_geo_cities_tmp.drop()   
    db.povodochek.typeahead_geo_cities_tmp.drop()

    dog_group_regions = { 
        k.get('_id'):k.get('count') 
            for k in db.dog_advs.aggregate({'$group' : 
                {'_id':'$region_id', 'count': {'$sum':1}}})["result"] }

    cat_group_regions = { 
        k.get('_id'):k.get('count') 
            for k in db.cat_advs.aggregate({'$group' : 
                {'_id':'$region_id', 'count': {'$sum':1}}})["result"] }

    dog_group_cities = { 
        k.get('_id'):k.get('count') 
            for k in db.dog_advs.aggregate({'$group' : 
                {'_id':'$city_id', 'count': {'$sum':1}}})["result"] }

    cat_group_cities = { 
        k.get('_id'):k.get('count') 
            for k in db.cat_advs.aggregate({'$group' : 
                {'_id':'$city_id', 'count': {'$sum':1}}})["result"] }

    rating_geo_cities = []
    
    for c in cities.values():
        c_id = c['city_id']
        rating = (dog_group_cities.get(c_id) or 0) + (cat_group_cities.get(c_id) or 0)
        city_region = format_city_region(c)
        rating_geo_cities.append({'geo_id' : c_id,
                'rating' : rating, 
                'name' : city_region, 
                'name_search' : city_region.lower()})

    rating_geo_all = list(rating_geo_cities)

    for r in regions.values():
        r_id = r['region_id']
        rating = (dog_group_regions.get(r_id) or 0) + (cat_group_regions.get(r_id) or 0)

        rating_geo_all.append({'geo_id' : r_id,
                'rating' : rating, 
                'name' : r['region_name'], 
                'name_search' : r['region_name'].lower()})


    db.povodochek.typeahead_geo_cities_tmp.insert(rating_geo_cities)

    db.povodochek.typeahead_geo_cities_tmp.ensure_index([("rating", DESCENDING), ('name_search', ASCENDING)])
    db.povodochek.typeahead_geo_cities_tmp.ensure_index([('name_search', ASCENDING)])


    db.povodochek.typeahead_geo_all_tmp.insert(rating_geo_all)
    db.povodochek.typeahead_geo_all_tmp.ensure_index([("rating", DESCENDING), ('name_search', ASCENDING)])
    db.povodochek.typeahead_geo_all_tmp.ensure_index([('name_search', ASCENDING)])

    db.povodochek.typeahead_geo_cities_tmp.rename('typeahead_geo_cities', dropTarget=
        'typeahead_geo_cities' in db.povodochek.collection_names())
    db.povodochek.typeahead_geo_all_tmp.rename('typeahead_geo_all', dropTarget=
        'typeahead_geo_all' in db.povodochek.collection_names())

@log_exception(logger = logger)
def update_regions_in_advs():
    # dogs
    for adv in db.dog_advs.find({'region_id' : {"$in": [None, ""]}}):
        r = get_region_by_city_id(adv.get('city_id'))
        print(adv.get('city_id'), r)
        db.dog_advs.update({'_id': adv.get('_id')}, 
            {'$set': {'region_id' : r.get("region_id")}})
    # cats
    for adv in db.cat_advs.find({'region_id' : {"$in": [None, ""]}}):
        r = get_region_by_city_id(adv.get('city_id'))
        db.cat_advs.update({'_id': adv.get('_id')}, 
            {'$set': {'region_id' : r.get("region_id")}})

@log_exception(logger = logger)
def rebuild_geos():
    db.povodochek.cities_tmp.drop()
    db.povodochek.regions_tmp.drop()

    for c in cities.values():
        c_id = c['city_id']
        r_id = c['region_id']
        c_size = c['city_size']
        r = get_region_by_id(r_id)
        location = {'type': "Point", 'coordinates' : [ c['longitude'], c['latitude'] ] }
        db.povodochek.cities_tmp.update({'city_id': c_id}, \
            {'$set' : { 
            'city_id': c_id, \
            'city_name' : c['city_name'], \
            'city_name_search' : c['city_name'].lower(), \
            'city_region' : format_city_region(c), \
            'city_region_search' : format_city_region(c).lower(), \
            'city_size' : c_size, \
            'region_id' : r_id, \
            'location' :  location }}, \
            upsert=True)
        db.povodochek.regions_tmp.update({'region_id': r_id}, \
            {'$set': {
            'region_id': r_id, 
            'region_name': r['region_name'], 
            'region_name_search' : r['region_name'].lower(),
            'region_name_d' : r['region_name_d'],
            'region_name_p' : r['region_name_p']}, 
            "$inc" : {'region_size' : c_size},
            '$push': {'cities': c_id} }, upsert = True)

        db.povodochek.cities_tmp.ensure_index([("location", GEOSPHERE)])

        db.povodochek.cities_tmp.ensure_index([("city_id", ASCENDING)])

        db.povodochek.regions_tmp.ensure_index([("region_id", ASCENDING)])

    db.povodochek.cities_tmp.rename('cities', dropTarget=True)
    db.povodochek.regions_tmp.rename('regions', dropTarget=True)

@log_exception(logger = logger)
def rebuild_advs_by_geos(pet):
    advs = db.povodochek['%s_advs' % pet]
    tmp_pet_by_cities_name = '%s_advs_by_cities_tmp' % pet
    tmp_pet_by_cities = db.povodochek[tmp_pet_by_cities_name]
    tmp_pet_by_regions_name = '%s_advs_by_regions_tmp' % pet
    tmp_pet_by_regions = db.povodochek[tmp_pet_by_regions_name]
    pet_by_cities_name = '%s_advs_by_cities' % pet
    pet_by_cities = db.povodochek[pet_by_cities_name]
    pet_by_regions_name = '%s_advs_by_regions' % pet
    pet_by_regions = db.povodochek[pet_by_regions_name]

    tmp_pet_by_cities.drop()

    for adv in advs.find():
        city = get_city_by_id(adv.get('city_id'))
        if city:
            city_id = city.get('city_id')
            city_name = city.get('city_name')
            region_id = city.get('region_id')
            region_name = get_region_name(region_id)
            breed_id = adv.get('breed_id')
            breed_name = get_breed_name(breed_id)
            tmp_pet_by_cities.update({'city_id': city_id}, {
                '$inc': {'count': 1},
                '$push': {'breeds': {"breed_id" : breed_id}},
                '$setOnInsert': {
                    'city_id': city_id,
                    'city_name': city_name, \
                    'region_name': region_name}  \
                    }, upsert = True, multi = False)
            
            tmp_pet_by_regions.update({'region_id': region_id}, {
                '$inc': {'count': 1},
                '$push': {'breeds': {"breed_id" : breed_id}},
                '$setOnInsert': {
                'region_id': region_id, 
                'region_name': region_name}}, \
                    upsert = True, multi = False)


    tmp_pet_by_cities.rename(
        pet_by_cities_name, dropTarget=tmp_pet_by_cities_name in db.povodochek.collection_names())

    tmp_pet_by_regions.rename(
        pet_by_regions_name, dropTarget=tmp_pet_by_regions_name in db.povodochek.collection_names())

@log_exception(logger = logger)
def recalc_attraction_in_advs():
    for dog in db.dog_advs.find():
        form = Dog()
        for f in form:
            f.set_val(dog.get(f.get_db_name()))
        attraction = calc_attraction(form)
        print(attraction, dog.get('_id'))
        db.dog_advs.find_and_modify({'_id' : dog.get('_id')}, \
            {'$set': {'attraction': attraction}})
        

@log_exception(logger = logger)
def set_expire_date_for_dog_advs(days = 4):
    from datetime import (datetime, timedelta)
    now = datetime.utcnow()
    today = datetime(now.year, now.month, now.day)
    for adv in db.dog_advs.find():
        current_period = now.date() - adv.get('update_date').date()
        if current_period.days > config.DOG_ADV_EXPIRE_IN_DAYS:
            expire_date = now.date() + timedelta(days = days)
        else:
            expire_date = adv.get('update_date').date() + timedelta(days = config.DOG_ADV_EXPIRE_IN_DAYS)
        adv = db.dog_advs.find_and_modify(
            {'_id': adv.get('_id')}, 
            {"$set":{'expire_date' : 
                datetime(expire_date.year, 
                    expire_date.month, 
                    expire_date.day)}}, 
            upsert = False, new = True)

@log_exception(logger = logger)
def notify_about_expired_dog_advs(days = 4):
    from datetime import (datetime, timedelta)
    now = datetime.utcnow()
    notify_date = now.date() + timedelta(days = int(days))

    for adv in db.dog_advs.find({'expire_date' : 
        {'$lt':datetime(notify_date.year, notify_date.month, notify_date.day)}}):
        if (adv.get('expire_date').date() - now.date()).days > 0:
            user = db.get_user(adv.get('user_id'))
            if config.DEBUG:
                user = db.get_user('5278d08ba3b1086ca967262f')
                print("notify expired dog adv %s" % adv.get('_id'))
            mailer.notify_user_of_dog_adv_expired(user, adv)
            if config.DEBUG:
                break

@log_exception(logger = logger)
def archive_expired_dog_advs():
    for adv in db.get_dog_advs_expired():
        user = db.get_user(adv.get('user_id'))
        if config.DEBUG:
            user = db.get_user('5278d08ba3b1086ca967262f')
            print("archive dog adv %s" % adv.get('_id'))
        db.archive_dog_adv(
            adv_id = adv.get('_id'),
            user_id = adv.get('user_id'))
        mailer.notify_user_of_dog_adv_archived(user, adv)
        if config.DEBUG:
            break

if __name__ == '__main__':
    func = sys.argv[1]
    args = "{0}".format(sys.argv[2:]).strip("[]")
    ex = '{0}({1})'.format(func, args )
    print(ex)
    eval(ex)
