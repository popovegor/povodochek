#!/usr/bin/python
# -*- coding: utf-8 -*-


from pymongo import MongoClient
from random import randint

db = MongoClient()['povodochek']

def clear_sale_advs():
	for adv in db.sales.find():
		if not adv.get('title'):
			db.sales.remove(adv)

def copy_sale_advs():
	for adv in db.sales.find():
		del(adv['_id'])
		db.sales.insert(adv)


def shuffle_photos():
	count = db.photos.files.count()
	for adv in db.sales.find():
		adv['photos'] = [file['filename'] for file in db.photos.files.find(skip = randint(0, count-1), limit=randint(1,5)) if file.get('filename')]
		db.sales.save(adv)
		# print(adv)

if __name__ == "__main__":
	# update_broken_photos()
	# clear_sale_advs()
	# copy_sale_advs()
	shuffle_photos()	
