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
import subprocess
from datetime import datetime


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
	      'https://www.googleapis.com/auth/drive', 
	      'https://www.googleapis.com/auth/drive.file']
		)

		# Create an httplib2.Http object to handle our HTTP requests and authorize it
		# with our good Credentials.
		http = httplib2.Http()
		http = credentials.authorize(http)

		# Construct the service object for the interacting with the Google Analytics API.
		service = discovery.build('drive', 'v2', http=http)
		return service

	except client.AccessTokenRefreshError:
		print ("The credentials have been revoked or expired, please re-run the application to re-authorize")



def create_backup_tar():
	ret_code = subprocess.call(["rm", "-Rf" , "/tmp/povodochek/"])
	print(ret_code)
	ret_code = subprocess.call(["mongodump", "-d", "povodochek", "-o", "/tmp/"])
	print(ret_code)
	ret_code = subprocess.call(["tar", "-cf", "/tmp/povodochek.tar", "/tmp/povodochek/"])
	print(ret_code)
	return '/tmp/povodochek.tar'

def backup_db_to_gdrive():

	path = create_backup_tar()
	service = get_service()
	now = datetime.now()

	media_body = MediaFileUpload(path, mimetype='application/tar', resumable=True)
	body = {
	    'title': ('povodochek_db_%s.tar' % now.isoformat()) ,
	    # 'title': 'povodochek_db.tar' ,
	    'description': '',
	    'mimeType': 'application/tar'
	}


	file = service.files().insert(body=body, media_body=media_body).execute()

	pprint.pprint(file)

	permission = {
	  'value': 'povodochek.rf@gmail.com',
	  'type': 'user',
	  'role': 'writer'
	}

	service.permissions().insert(
        fileId=file.get("id"), body=permission).execute()

	pprint.pprint(file)


if __name__ == '__main__':
	eval('{0}()'.format(sys.argv[1]))