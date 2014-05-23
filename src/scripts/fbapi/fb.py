#!/usr/bin/python
# -*- coding: utf-8 -*-


import requests
from pprint import pprint 
import db
import sys

import logging
import config
logging.basicConfig()
logger = logging.getLogger(__name__)

if not config.DEBUG:
    from ThreadedSMTPHandler import ThreadedSMTPHandler
    mail_handler = ThreadedSMTPHandler(subject = 'povodochek:error:fb')
    mail_handler.setLevel(logging.ERROR)
    logger.addHandler(mail_handler)


FB_USER_ID = "10152387162700930" #EGOR POPOV
FB_APP_ID = "277074232467800"
FB_PAGE_TOKEN = "CAAD7ZC18z4VgBAPKvDhh9UD1tprxZCG68TD23BbDMzp5hGNZATkjbMbcQb1svkB5lLrwDGrcH4imgjgo6BYTVM3MnzXw8xaxbZBIzzkJvcJ1VS4xA2mszttgbMG7CG0SN6tQpD4gtHVcYqeqqVuguSS6tZBztC2ZBCuKNZB4xpmUvs4eUn8ZB3YlUlNwjLHKZBwQZD"

def call_api(method = "GET", node_id = "", edge_name = "", fields = {}):
	url = "https://graph.facebook.com/v2.0/%s/%s" % (node_id, edge_name)
	fields['access_token'] = FB_PAGE_TOKEN
	if method == "GET":
		return requests.get(url, params = fields).json()
	if method == "POST":
		return requests.post(url, params = fields).json()
	if method == "DELETE":
		return requests.delete(url, params = fields).json()

def post_dog_adv(adv_id):
	try:
		adv = db.get_dog_adv(adv_id)
		fields = {"link" : "http://povodochek.com/prodazha-sobak/%s/" % adv.get('_id')}
		if adv.get("photos"):
			fields["picture"] = "http://povodochek.com/thumbnail/%s" % adv.get("photos")[0]
		post = call_api(method = "POST", 
			node_id = config.FB_PAGE_ID, 
			edge_name = 'feed', 
			fields = fields)

		db.mark_dog_adv_as_fb_posted(adv.get('_id'), post['id'])

		return post

	except Exception, e:
		logger.exception(e)
		raise e
	

def remove_dog_adv(adv_id):
    try:
        adv = db.get_dog_adv_archived(adv_id)
        pprint(adv)
        result = call_api(method = "DELETE", 
			node_id = adv.get('fb').get('post_id'))
        db.mark_dog_adv_as_fb_deleted(adv.get('_id'))
        pprint(result)
        return result

    except Exception, e:
        logger.exception(e)
        raise e


def post_dog_advs_to_fb():
    for adv in db.get_dog_advs_to_post_in_fb(mins = 1440):
        post = post_dog_adv(adv)
        pprint(post)


def remove_dog_advs_from_fb():
    for adv in db.get_dog_advs_to_remove_from_fb():
        result = remove_dog_adv(adv.get('_id'))
        pprint(result)


if __name__ == '__main__':
	func = sys.argv[1]
	args = "{0}".format(sys.argv[2:]).strip("[]")
	ex = '{0}({1})'.format(func, args )
	print(ex)
	eval(ex)
	
