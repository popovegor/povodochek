#!/usr/bin/env 
# -*- coding: utf-8 -*-


from cities import cities
from regions import regions
from countries import countries

import random
import db



def get_city_name(city_id, padezh = 'i'):
	city = cities.get(city_id)
	# return city.get('city_name_' + padezh) if city else u""
	return city.get('city_name') if city else u""

def get_city_by_id(city_id):
	return cities.get(city_id)

def get_city_region(city_id):
	city = cities.get(city_id)
	return format_city_region(city) if city else u"" 

def format_city_region_by_city_id(city_id):
	city = cities.get(city_id)
	return format_city_region(city) if city else u""

def format_city_region(city):
	region = get_region_by_id(city.get('region_id'))
	return u"{0}, {1}".format(city['city_name'], region['region_name'])

def get_region_name_by_city_id(city_id):
	region = get_region_by_city_id(city_id)
	return region.get("region_name") if region else u""
	
def get_region_name(region_id):
	region = get_region_by_id(region_id)
	return region.get('region_name') if region else u""

def get_region_by_id(region_id):
	return regions.get(region_id)

def get_region_by_city_id(city_id):
	city = cities.get(city_id)
	return regions.get(city.get('region_id'))

def get_country_by_id(country_id):
	return countries.get(country_id) or u''

def get_country_name(country_id):
	c = countries.get(country_id)
	return c.get('name') if c else u""

def get_countries_for_dog_adv():
	return [ (c.get("country_id"), 
		u"%s (%s)" % (c["name"], c["alpha3"])) for c in countries.values() if c.get("dog")] 



import sys

if __name__ == '__main__':
    eval('{0}()'.format(sys.argv[1]))