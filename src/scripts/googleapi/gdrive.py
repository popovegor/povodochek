#!/usr/bin/python
# -*- coding: utf-8 -*-


import httplib2
from pprint import pprint
from oauth2client.client import SignedJwtAssertionCredentials
from apiclient.http import MediaFileUpload
from oauth2client import client
from apiclient import discovery

import os
import sys
import subprocess
from datetime import datetime
from config import (MONGODB_HOSTS,MONGODB_REPLSET) 
import config
from datetime import datetime

from helpers import (log_exception)
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


if not config.DEBUG:
    from ThreadedSMTPHandler import ThreadedSMTPHandler
    mail_handler = ThreadedSMTPHandler(subject = 'povodochek:error:gdrive')
    mail_handler.setLevel(logging.ERROR)
    logger.addHandler(mail_handler)


PRIVATE_KEY = os.path.join(os.path.dirname(__file__), 'pk.pem')

def get_service():
	try:
		f = file(PRIVATE_KEY, "rb")
		key = f.read()
		f.close()

		credentials = SignedJwtAssertionCredentials(
		  "575093701296-8ihh0r1gmt7ji895mtq6to5401hj8bls@developer.gserviceaccount.com", \
		  key, \
		  scope=[
	      'https://www.googleapis.com/auth/drive', 
	      'https://www.googleapis.com/auth/drive.file', 
	      'https://www.googleapis.com/auth/drive.metadata.readonly']
		)

		http = httplib2.Http()
		credentials.refresh(http)
		http = credentials.authorize(http)

		service = discovery.build('drive', 'v2', http=http)

		return service

	except client.AccessTokenRefreshError, e:
		print ("The credentials have been revoked or expired, please re-run the application to re-authorize")
		print(e)


def create_backup_tar():
	ret_code = subprocess.call(["rm", "-Rf" , "/tmp/povodochek/"])
	print(ret_code)
	host = "{0}/{1}".format(MONGODB_REPLSET, ",".join(MONGODB_HOSTS))
	ret_code = subprocess.call(["mongodump", "-d", "povodochek", "-o", "/tmp/", "--host", host])
	print(ret_code)
	ret_code = subprocess.call(["tar", "-cf", "/tmp/povodochek.tar", "/tmp/povodochek/"])
	print(ret_code)
	return '/tmp/povodochek.tar'

def get_drive_about(service = None):
	service = service or get_service()
	about = service.about().get().execute()
	return about

def clear_drive_space(service = None):
	service = service or get_service()
	files = service.files().list(
		fields = "items(createdDate,fileSize,id)").execute()

	sorted_files = sorted(files.get("items"), key = lambda x: datetime.strptime(x.get('createdDate'), "%Y-%m-%dT%H:%M:%S.%fZ"))

	for f in sorted_files:
		about = get_drive_about(service)
		used = float(about.get('quotaBytesUsed'))
		total = float(about.get('quotaBytesTotal'))
		print(used, total, used / total)
		if used / total > 0.8:
			print(f.get("id"))
			service.files().delete(fileId = f.get("id")).execute()
		else:
			break

@log_exception(logger = logger)
def backup_db_to_gdrive():

	path = create_backup_tar()
	service = get_service()

	clear_drive_space(service)

	now = datetime.now()

	media_body = MediaFileUpload(path, mimetype='application/tar', resumable=True)
	body = {
	    'title': ('povodochek_db_%s.tar' % now.isoformat()) ,
	    # 'title': 'povodochek_db.tar' ,
	    'description': '',
	    'mimeType': 'application/tar'
	}

	file = service.files().insert(body=body, media_body=media_body).execute()

	pprint(file)

	permission = {
	  'value': 'povodochek.rf@gmail.com',
	  'type': 'user',
	  'role': 'writer'
	}

	service.permissions().insert(
        fileId=file.get("id"), body=permission).execute()

	pprint(file)


if __name__ == '__main__':
	eval('{0}()'.format(sys.argv[1]))