#!/usr/bin/python
# -*- coding: utf-8 -*-


import httplib2
import pprint
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.http import MediaFileUpload
from oauth2client import client
from apiclient import discovery

import os
import sys
from datetime import datetime
import re

PRIVATE_KEY = os.path.join(os.path.dirname(__file__), 'pk.pem')

def get_service():
	try:
		f = file(PRIVATE_KEY, "rb")
		key = f.read()
		f.close()

		credentials = SignedJwtAssertionCredentials(
		  "575093701296-4fme7oorbh6jp39srobnv57ghq8i58l4@developer.gserviceaccount.com", \
		  key, \
		  scope=[ 
	      'https://www.googleapis.com/auth/youtube']
		)

		# Create an httplib2.Http object to handle our HTTP requests and authorize it
		# with our good Credentials.
		http = httplib2.Http()
		http = credentials.authorize(http)

		service = discovery.build('youtube', 'v3', http=http)
		return service

	except client.AccessTokenRefreshError:
		print ("The credentials have been revoked or expired, please re-run the application to re-authorize")

def extract_video_id_from_url(url):
	if url:
		match = re.findall("""https?:\/\/(?:[0-9A-Z-]+\.)?(?:youtu\.be\/|youtube(?:-nocookie)?\.com\S*[^\w\s-])([\w-]{11})(?=[^\w-]|$)(?![?=&+%\w.-]*(?:['"][^<>]*>|<\/a>))[?=&+%\w.-]*""", url, re.IGNORECASE)
		return match[0] if match else None
	return None

def check_video(url):
	video_id = extract_video_id_from_url(url)
	if video_id:
		service = get_service()
		video = service.video().list(
		    part="id, player", 
		    id = video_id
		  ).execute()
		pprint(video)


if __name__ == '__main__':
	check_video("http://www.youtube.com/watch?v=9zNwgKzrDQg")
	# eval('{0}()'.format(sys.argv[1]))