#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import httplib2
import os
import sys
import pprint
from datetime import (datetime, date, timedelta)

from apiclient import discovery
# from oauth2client import file
from oauth2client import client
from oauth2client import tools
from oauth2client.client import SignedJwtAssertionCredentials
from bson.objectid import ObjectId
from bson.errors import InvalidId
import re
import db

PROFILE_ID = "75433672"

# PRIVATE_KEY = os.path.join(os.path.dirname(__file__), 'a792a40b3bec713b5af7119be161a2ec545929f9-privatekey.p12')

PRIVATE_KEY = os.path.join(os.path.dirname(__file__), 'pk.pem')

def get_servive():
	try:

		f = file(PRIVATE_KEY, "rb")
		key = f.read()
		f.close()


		credentials = SignedJwtAssertionCredentials(
		  "575093701296-8ihh0r1gmt7ji895mtq6to5401hj8bls@developer.gserviceaccount.com", \
		  key, \
		  scope=[
	      'https://www.googleapis.com/auth/analytics',
	      'https://www.googleapis.com/auth/analytics.edit',
	      'https://www.googleapis.com/auth/analytics.manage.users',
	      'https://www.googleapis.com/auth/analytics.readonly']
		)

		# Create an httplib2.Http object to handle our HTTP requests and authorize it
		# with our good Credentials.
		http = httplib2.Http()
		http = credentials.authorize(http)

		# Construct the service object for the interacting with the Google Analytics API.
		service = discovery.build('analytics', 'v3', http=http)
		return service

	except client.AccessTokenRefreshError:
		print ("The credentials have been revoked or expired, please re-run the application to re-authorize")


def get_first_profile_id(service):
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    firstAccountId = accounts.get('items')[0].get('id')
    webproperties = service.management().webproperties().list(
        accountId=firstAccountId).execute()

    if webproperties.get('items'):
      firstWebpropertyId = webproperties.get('items')[0].get('id')
      profiles = service.management().profiles().list(
          accountId=firstAccountId,
          webPropertyId=firstWebpropertyId).execute()

      if profiles.get('items'):
        return profiles.get('items')[0].get('id')

  return None


def get_top_keywords(service, profile_id):
  return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date='2013-01-01',
      end_date='2014-03-15',
      metrics='ga:visits',
      dimensions='ga:source,ga:keyword',
      sort='-ga:visits',
      filters='ga:medium==organic',
      start_index='1',
      max_results='25').execute()


def get_page_views(service, profile_id):
	today = date.today()
	end_date = datetime.strftime(today, "%Y-%m-%d")
	start_date = datetime.strftime(today - timedelta(days = 365), "%Y-%m-%d")
	return service.data().ga().get(
      ids='ga:' + profile_id,
      start_date=start_date,
      end_date=end_date,
      metrics='ga:pageviews,ga:uniquePageviews',
      dimensions='ga:pagePath',
      sort='-ga:uniquePageviews',
      filters='ga:pagePath=~^/prodazha-sobak/[A-Za-z0-9]*/$',
      start_index='1',
      max_results='10000').execute()

def update_page_views_stat():
	service = get_servive()
	page_views = get_page_views(service, PROFILE_ID)
	for row in page_views.get('rows'):
		try:
			(url, views, unique_views) = (row[0], int(row[1]), int(row[2]))
			match = re.search('/([a-zA-Z0-9]*)/', url)
			if match:
				adv_id = ObjectId(match.group(1))
				adv = db.dog_advs.find_and_modify(query = {'_id': adv_id}, update = {'$set': {'stat.views' : views, 'stat.unique_views' : unique_views}}, upsert = False, full_response = False)
				# print(adv)
		except InvalidId, e:
			print(e, row)
			
if __name__ == '__main__':
	eval('{0}()'.format(sys.argv[1]))