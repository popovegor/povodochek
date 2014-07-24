#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymongo import (MongoReplicaSetClient, ASCENDING, DESCENDING)
from bson.objectid import ObjectId
from bson.son import SON
from gridfs import GridFS
import re
from datetime import (datetime, timedelta)
from uuid import (uuid4, uuid1)
from helpers import (num, str2date)
from dic.pet_docs import (dog_docs, doc_dog_pedigrees)
import sys
import os
import time
import config

print(config.MONGODB_URI)
mongo = MongoReplicaSetClient(config.MONGODB_URI)
povodochek = mongo['povodochek']

users = povodochek.users
cat_advs = povodochek.cat_advs
cat_advs_archived = povodochek.cat_advs_archived
cat_advs_deleted = povodochek.cat_advs_deleted
dog_advs = povodochek.dog_advs
dog_advs_archived = povodochek.dog_advs_archived
dog_advs_deleted = povodochek.dog_advs_deleted
pets_by_cities = povodochek.pets_by_cities
dog_breeds_rating = povodochek.dog_breeds_rating
cat_breeds_rating = povodochek.cat_breeds_rating

dog_advs_by_cities = povodochek.dog_advs_by_cities
cat_advs_by_cities = povodochek.cat_advs_by_cities
dog_advs_by_regions = povodochek.dog_advs_by_regions
cat_advs_by_regions = povodochek.cat_advs_by_regions

cities = povodochek.cities
regions = povodochek.regions
photos = povodochek.photos
photos_gridfs = GridFS(povodochek, "photos")
typeahead_geo_all = povodochek.typeahead_geo_all
typeahead_geo_cities = povodochek.typeahead_geo_cities

typeahead_dog_breeds = povodochek.typeahead_dog_breeds
typeahead_cat_breeds = povodochek.typeahead_cat_breeds

news = povodochek.news
news_deleted = povodochek.news_deleted

def get_subscribe(subscribe):
    def_subscribe = {"news":True, "archived": True, "expired" : True}
    def_subscribe.update(subscribe or {})
    return def_subscribe

def check_subscribe(user_id, subscribe_name):
    subscribe = get_subscribe_for_user(user_id)
    return subscribe.get(subscribe_name)

def get_subscribe_for_user(user_id):
    user = users.find_one({'_id': ObjectId(user_id)},
     fields = ['subscribe'])
    if user:
        return get_subscribe(user.get("subscribe"))


def save_subscribe(user_id, subscribe):
    if subscribe:
        updater = {}
        for f in subscribe:
            updater['subscribe.%s' % f.get_db_name()] = f.get_val(subscribe)
    return users.find_and_modify(
        {'_id': ObjectId(user_id)}, 
        {"$set": updater},
        upsert = False, new = True
        )
    

def revert_singup(user_id):
    users.remove({'_id':ObjectId(user_id)})

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

def get_users_activated():
    return users.find({'activated' : True})

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

def signup_user(email, pwd_hash, username, confirm, ):
    return users.insert({
        'email': email, \
        'pwd_hash': pwd_hash, \
        'username': username, 'confirm': confirm, \
        'activated': False, 'signup_date': datetime.utcnow()})

def reset_user_password(user_id, pwd_hash, asign):
    return users.find_and_modify({"_id": ObjectId(user_id)}, \
        {"$set": {'asign_pwd_hash': pwd_hash, \
        'asign': asign}}, new = True, upsert = False)


def save_user_contact(user_id, form):
    now = datetime.utcnow()
    updater = {}
    
    user_set = {'update_date' : now}
    user_unset = {}

    for field in form:
        val = field.get_val(form)
        db_name = field.get_db_name()
        if val:
            user_set[db_name] = val
        else: 
            user_unset[db_name] = ""

    if user_unset:
        updater['$unset'] = user_unset
    if user_set:
        updater['$set'] = user_set

    user = users.update(\
        {'_id': ObjectId(user_id)}, updater, upsert = True)

    return user

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

def get_dog_adv_archived_for_user(adv_id, user_id):
    return dog_advs_archived.find_one({'_id': ObjectId(adv_id), 'user_id' : str(user_id)})

def get_cat_adv_archived_for_user(adv_id, user_id):
    return cat_advs_archived.find_one({'_id': ObjectId(adv_id), 'user_id' : str(user_id)})

def get_dog_adv_archived(adv_id):
    return dog_advs_archived.find_one({'_id': ObjectId(adv_id)})

def get_dog_adv_deleted(adv_id):
    return dog_advs_deleted.find_one({'_id':ObjectId(adv_id)})

def get_cat_adv(adv_id):
    return cat_advs.find_one({'_id': ObjectId(adv_id)})    

def get_cat_adv_archived(adv_id):
    return cat_advs_archived.find_one({'_id': ObjectId(adv_id)})

def get_expire_date(dt):
    return datetime(dt.date().year, dt.date().month, dt.date().day) + timedelta(days=config.DOG_ADV_EXPIRE_IN_DAYS)

def refresh_dog_adv(user_id, adv_id):
    now = datetime.utcnow()
    expire_date = get_expire_date(now)
    query = {'_id': ObjectId(adv_id), 'user_id' : str(user_id)}
    adv = dog_advs.find_and_modify(query, 
        {"$set":{"update_date" : now, 'expire_date' : expire_date}}, upsert = False, new = True)
    return adv


def upsert_dog_adv(user_id, adv_id, form, attraction):
    now = datetime.utcnow()
    updater = {}
    expire_date = get_expire_date(now)
    
    dog_set = {
        'user_id' : str(user_id),
        'update_date' : now,
        'expire_date' : expire_date,
        'attraction': attraction,
        'region_id' : form.city.region_id
        }
    dog_unset = {}

    for field in form:
        val = field.get_val(form)
        db_name = field.get_db_name()
        if val:
            dog_set[db_name] = val
        else:
            dog_unset[db_name] = ""

    updater['$set'] = dog_set
    updater['$setOnInsert'] = {'add_date':now}

    if dog_unset:
        updater['$unset'] = dog_unset

    query = {'_id': ObjectId(adv_id), 'user_id' : str(user_id)}
    adv = dog_advs.find_and_modify(query, updater, upsert = True, new = True)
    return adv

def get_dog_advs():
    return dog_advs.find()

def get_dog_advs_expired():
    now = datetime.utcnow()
    today = datetime(now.year, now.month, now.day)
    return dog_advs.find({'expire_date': {'$lte' : today}})

def get_dog_advs_by_user(user_id):
    return dog_advs.find(
        {'user_id': {'$in' : [str(user_id), user_id]} },\
        sort = [("update_date", DESCENDING), \
        ("add_date", DESCENDING)])

def get_dog_advs_archived_by_user(user_id):
    return dog_advs_archived.find(
        {'user_id': {'$in' : [str(user_id), user_id]} },\
        sort = [("update_date", DESCENDING), \
        ("add_date", DESCENDING)])

def get_cat_advs_by_user(user_id):
    return cat_advs.find(
        {'user_id': {'$in' : [str(user_id), user_id]} },\
        sort = [("update_date", DESCENDING), \
        ("add_date", DESCENDING)])

def get_cat_advs_archived_by_user(user_id):
    return cat_advs_archived.find(
        {'user_id': {'$in' : [str(user_id), user_id]} },\
        sort = [("update_date", DESCENDING), \
        ("add_date", DESCENDING)])

def get_dog_breeds_rating(limit = 25):
    return [breed for breed in dog_breeds_rating.find( \
        sort = [('count', DESCENDING)], limit = limit)]

def get_cat_breeds_rating(limit = 25):
    return [breed for breed in cat_breeds_rating.find( \
        sort = [('count', DESCENDING)], limit = limit)]

def get_dog_breeds_for_typeahead(query, limit):
    matcher = re.compile(re.escape(query.lower()))
    breeds = [breed.get('breed_name') \
        for breed in typeahead_dog_breeds.find(\
            {'breed_name_search': {"$regex": matcher}}, \
            limit = limit, \
            sort = [
            ('rating', DESCENDING),
            ('breed_name', ASCENDING)
            ] )]
    return breeds

def get_cat_breeds_for_typeahead(query, limit):
    matcher = re.compile(re.escape(query.lower()))
    breeds = [breed.get('breed_name') \
        for breed in typeahead_cat_breeds.find(\
            {'breed_name_search': {"$regex": matcher}}, \
            limit = limit, \
            sort = [
            ('rating', DESCENDING),
            ('breed_name', ASCENDING)
            ] )]
    return breeds

def get_geo_cities_for_typeahead(query, limit):
    matcher = re.compile("^" + re.escape(query.lower()))
    locations = [ city.get("name")  \
        for city in typeahead_geo_cities.find(\
            {'name_search': {"$regex": matcher}}, \
            limit = limit, \
            fields = ["name"], \
            sort = [('rating', DESCENDING), ('name_search',ASCENDING)] )]
    return locations

def get_geo_all_for_typeahead(query, limit):
    matcher = re.compile("^" + re.escape(query.lower()))
    locations = [ geo.get("name")  \
        for geo in typeahead_geo_all.find(\
            {'name_search': {"$regex": matcher}}, \
            limit = limit, \
            fields = ["name"], \
            sort = [('rating', DESCENDING), ('name_search',ASCENDING)] )]
    return locations


def get_distances_from_city(city_id):
    distances = {} # city_id : distance
    city = cities.find_one({'city_id': city_id})
    if city and city.get("location"):
        location = city.get("location")
        geoNear = povodochek.command(
            SON([("geoNear",  "cities"), 
            ("near", location), ( "spherical", True ), 
            ("limit", 15000)]))
        distances = { geo["obj"]['city_id'] : geo["dis"]
            for geo in geoNear.get("results")}
    return distances

def get_near_cities(city_id = None, distance = None):
    near_cities = []
    if city_id:
        search_city = cities.find_one(\
            {'city_id': city_id})
        if search_city and distance and search_city.get("location"):
            location = search_city.get("location")
            geoNear = povodochek.command(SON([("geoNear",  "cities"), \
                ("near", location), ( "spherical", True ), \
                ("maxDistance", distance * 1000), ("limit", 15000)]))
            near_cities = { 
            geo["obj"].get('city_id') : geo["dis"]
            for geo in geoNear.get("results")}
    return near_cities


def find_dog_advs(
    breed_id = None, gender_id = None, 
    region_id = None, city_id = None,
    distance = None, photo = False,
    video = False, delivery = False, 
    champion_bloodlines = False,
    contract = False, 
    pedigree = False,
    price_from = None, price_to = None,
    sort = None, skip = None, limit = None):

    _filter = []
    extend_filter = lambda k,v: _filter.append((k,v)) if v else None
    if num(gender_id):
        extend_filter('$or', [{'gender_id' : num(gender_id)}, \
            {'gender_id' : {'$exists': False}}])

    extend_filter("breed_id", num(breed_id))

    price_from = num(price_from)
    price_to = num(price_to)
    if price_from or price_to:
        extend_filter("price", \
            {"$gte" : price_from if price_from > 0 else 0,\
             "$lte" : price_to if price_to else sys.maxint })
    geo_distances = {}
    geo_filter = None

    if city_id:
        geo_distances = get_distances_from_city(city_id)
        if distance:
            near_cities = [c_id for c_id, dis in geo_distances.items() if dis <= distance * 1000]
            geo_filter = ('$or', [{"city_id" : {"$in": near_cities}}])
        else:
            geo_filter = ('$or', [{"city_id" : city_id}])
    elif region_id:
        geo_filter = ("$or", [{"region_id" : region_id}])

    if geo_filter:
        if delivery:
            geo_filter[1].append({"delivery":True})
        extend_filter(geo_filter[0], geo_filter[1]) 

    if photo:
        extend_filter("photos", {"$nin": [None, []]})

    if video:
        extend_filter("video_link" , {"$nin":[None, ""]})

    if champion_bloodlines: 
        extend_filter("champion_bloodlines", True)

    if contract:
        extend_filter("contract", True)

    if pedigree:
        extend_filter("doc_id", {'$exists' : True})

    sortby = [("update_date", -1)]
    if sort == 1:
        sortby = [("price", -1)]
    elif sort == 2:
        sortby = [("price", 1)]
    elif sort == 3:
        sortby = [("update_date", -1)]
    else:
        sortby = [("attraction",-1), ("update_date", -1)]

    # print("filter %s" % _filter)
    # print("sort %s" % sortby)
    # print(limit)
    total = dog_advs.count()
    query = dog_advs.find(SON(_filter),\
        limit = limit or total,\
        skip = skip or 0,\
        sort = sortby)
    count = query.count()
    advs = [adv for adv in query]

    #add distance into each adv 
    if geo_distances:
        for adv in advs:
            dist = geo_distances.get(adv.get('city_id'))
            if dist:
                adv["distance"] = int(round(dist / 1000, 0))

    return (advs, count, total)


def find_cat_advs(pet_id = 2, gender_id = None, \
    breed_id = None,  region = None, city = None, distance = None, \
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
    if city:
        if distance:
            near_cities = get_near_cities(city, distance)
            extend_filter("city_id", {"$in": [city.get("city_id") \
               for city, dis in near_cities]})
        else:
            extend_filter("city_id", {"$in": [city.get('city_id')]})
    elif region:
        extend_filter("region_id", region.get('region_id'))

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
            fields = ['_id'])
        # print(photo)
        if photo:
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


def archive_dog_adv(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = dog_advs.find_one(query)
    if adv:
        adv['archive_date'] = datetime.utcnow()
        dog_advs_archived.update(query, adv, multi = False, upsert = True)
        dog_advs.remove(query, multi = False)
    return adv

def archive_cat_adv(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = cat_advs.find_one(query)
    if adv:
        adv['archive_date'] = datetime.utcnow()
        cat_advs_archived.update(query, adv, multi = False, upsert = True)
        cat_advs.remove(query, multi = False)
    return adv


def remove_dog_adv_archived(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = dog_advs_archived.find_and_modify(query, remove = True)
    if adv:
        adv['delete_date'] = datetime.utcnow()
        dog_advs_deleted.save(adv)
    return adv

def remove_cat_adv_archived(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = cat_advs_archived.find_and_modify(query, remove = True)
    if adv:
        adv['delete_date'] = datetime.utcnow()
        cat_advs_deleted.save(adv)
    return adv

def remove_dog_adv(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = dog_advs.find_one(query)
    if adv:
        adv['delete_date'] = datetime.utcnow()
        dog_advs_deleted.update(query, adv, upsert = True, multi = False)
        dog_advs.remove(query, multi  = False)
    return adv

def undo_remove_dog_adv(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = dog_advs_deleted.find_one(query)
    if adv:
        dog_advs.update(query, adv, upsert = True, multi  = False)
        dog_advs_deleted.remove(query, multi  = False)
    return adv


def remove_cat_adv(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = cat_advs.find_one(query)
    if adv:
        adv['delete_date'] = datetime.utcnow()
        cat_advs_deleted.update(query, adv, upsert = True, multi = False)
        cat_advs.remove(query, multi  = False)
    return adv

def undo_remove_cat_adv(adv_id, user_id):
    query = {'_id': ObjectId(adv_id), 
        'user_id': {'$in': [user_id, str(user_id)]}}
    adv = cat_advs_deleted.find_one(query)
    if adv:
        cat_advs.update(query, adv, upsert = True, multi  = False)
        cat_advs_deleted.remove(query, multi  = False)
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

def get_cat_advs_for_fresh(skip, limit):
    return cat_advs.find(
        { }, \
        skip = skip, \
        fields = ["_id", "photos", "title", \
        "price", "breed_id", "update_date", "add_date"], \
        limit = limit, \
        sort = [('update_date', DESCENDING), \
        ("add_date", DESCENDING)])

def get_dog_advs_for_fresh(skip, limit):
    return dog_advs.find(
        {}, \
        skip = skip, \
        fields = ["_id", "photos", "title", \
        "price", "breed_id", "update_date", "add_date"], \
        limit = limit, \
        sort = [('update_date', DESCENDING), \
        ("add_date", DESCENDING)])


def get_dog_advs_by_cities():
    return [adv for adv in dog_advs_by_cities.find(
        sort=[('city_name', ASCENDING)])]

def get_cat_advs_by_cities():
    return sorted([adv for adv in cat_advs_by_cities.find()], \
        key = lambda x : x['city_name'])


def get_dog_advs_by_regions():
    return [adv for adv in dog_advs_by_regions.find(
        sort=[('region_name', ASCENDING)])]

def get_cat_advs_by_regions():
    return sorted([adv for adv in cat_advs_by_regions.find()], \
        key = lambda x : x['region_name'])

def upsert_news(news_id, subject, message, 
    published, summary, publish_date):
    now = datetime.utcnow()
    return news.find_and_modify({'_id' : ObjectId(news_id)}, 
        {'$set' : {'subject': subject, 
        'message' : message, 
        'update_date' : now,
        'published' : published, 
        'summary' : summary,
        'publish_date' : publish_date},
        "$setOnInsert" : {'create_date' : now, 'comments_count' : 0}},
        new = True, 
        upsert = True, 
        multi = False)

def get_news_by_id(news_id):
    return news.find_one({'_id': ObjectId(news_id)})

def remove_news(news_id):
    ret = news.find_and_modify({'_id': ObjectId(news_id)}, remove = True)
    news_deleted.insert(ret)

def get_news_all(limit = 0, published = True):
    query = {}
    if published:
        query['published'] = published
    return news.find(query, 
        sort = [('publish_date', DESCENDING), ('update_date', DESCENDING)], 
        limit = limit)

def comment_news(news_id, levels, text, author_id):
    if levels != []:
        str_path = '.'.join('comments.%d' % level for level in levels)
        str_path += '.comments'
    else:
        str_path = 'comments'
    
    now = datetime.utcnow()

    return news.find_and_modify(
        { '_id': ObjectId(news_id) },
        { "$inc" : {'comments_count' : 1},
        '$push': {
            str_path: {
                'create_date': now,
                'author_id': str(author_id),
                'text': text } } }, 
        new = True)

def admin_get_users(limit, skip):
    return users.find(
        sort = [('signup_date', DESCENDING)],
        limit = limit, skip = skip)

def get_dog_advs_for_last_mins(mins = 60):
    dt = datetime.utcnow() - timedelta(minutes = mins)
    return dog_advs.find({'update_date' : {'$gte':dt}})


def get_dog_advs_to_post_in_vk(mins = 60):
    dt = datetime.utcnow() - timedelta(minutes = mins)
    return dog_advs.find({'update_date' : {'$gte':dt}, 
        'vk.post':{'$ne':True} })

def mark_dog_adv_as_vk_posted(adv_id, post_id):
    now = datetime.utcnow()
    dog_advs.update({'_id': ObjectId(adv_id)}, 
        {'$set': 
        {'vk.post': True, 'vk.post_date' : now, 'vk.post_id':post_id}}, 
        multi = False, upsert = False)

def get_dog_advs_to_remove_from_vk():
    return [adv for adv in dog_advs_archived.find({'vk.post_deleted' : {'$ne':True}, 'vk.post' : True })] + [adv for adv in dog_advs_deleted.find({'vk.post_deleted' : {'$ne':True}, 'vk.post' : True })]

def mark_dog_adv_as_vk_deleted(adv_id):
    now = datetime.utcnow()
    dog_advs_archived.find_and_modify({'_id': ObjectId(adv_id)}, {'$set': {'vk.post_deleted' : True, 'vk.post_delete_date' : now}}, upsert = False)
    dog_advs_deleted.find_and_modify({'_id': ObjectId(adv_id)}, {'$set': {'vk.post_deleted' : True, 'vk.post_delete_date' : now}}, upsert = False)

def get_dog_advs_to_post_in_fb(mins = 60):
    dt = datetime.utcnow() - timedelta(minutes = mins)
    return dog_advs.find({'update_date' : {'$gte':dt}, 
        'fb.post':{'$ne':True} })

def mark_dog_adv_as_fb_posted(adv_id, post_id):
    now = datetime.utcnow()
    dog_advs.update({'_id': ObjectId(adv_id)}, 
        {'$set': 
        {'fb.post': True, 'fb.post_date' : now, 'fb.post_id':post_id}}, 
        multi = False, upsert = False)

def get_dog_advs_to_remove_from_fb():
    return 
    [adv for adv in dog_advs_archived.find({'fb.post_deleted' : {'$ne':True}, 'fb.post' : True })] 
    + [adv for adv in dog_advs_deleted.find({'fb.post_deleted' : {'$ne':True}, 'fb.post' : True })]

def mark_dog_adv_as_fb_deleted(adv_id):
    now = datetime.utcnow()
    dog_advs_archived.update({'_id': ObjectId(adv_id)}, {'$set': {'fb.post_deleted' : True, 'fb.post_delete_date' : now}}, multi = False, upsert = False)
    dog_advs_deleted.find_and_modify({'_id': ObjectId(adv_id)}, {'$set': {'fb.post_deleted' : True, 'fb.post_delete_date' : now}}, upsert = False)

def get_region_by_id(region_id):
    region = None
    try:
        region = regions.find_one({"region_id":int(region_id)})
    except:
        pass
    return region

def get_region_by_name(region_name):
    region = None
    if region_name:
        matcher = re.compile(u"^" + re.escape(region_name.strip().lower()))
        region = regions.find_one({"region_name_search": matcher},\
            sort = [('region_size', -1)])
    return region

def get_city_by_city_and_region(city_and_region):
    city = None
    if city_and_region: 
        matcher = re.compile(u"^" + re.escape(city_and_region.strip().lower()))
        city = cities.find_one({"city_region_search": matcher},\
            sort = [('city_size',-1)])
        # if city:
            # return get_city_by_city_id(city.get('city_id'))
        return city
    return city


def get_city_by_id(city_id):
    city = None
    try:
        city = cities.find_one({"city_id":int(city_id)})
    except:
        pass
        
    return city