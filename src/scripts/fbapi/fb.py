#!/usr/bin/python
# -*- coding: utf-8 -*-


import requests
from pprint import pprint 
import db
import sys

FB_USER_ID = "10152387162700930" #EGOR POPOV
FB_APP_ID = "277074232467800"
FB_PAGE_ID = "232676253593173"
FB_PAGE_TOKEN = "CAAD7ZC18z4VgBAPKvDhh9UD1tprxZCG68TD23BbDMzp5hGNZATkjbMbcQb1svkB5lLrwDGrcH4imgjgo6BYTVM3MnzXw8xaxbZBIzzkJvcJ1VS4xA2mszttgbMG7CG0SN6tQpD4gtHVcYqeqqVuguSS6tZBztC2ZBCuKNZB4xpmUvs4eUn8ZB3YlUlNwjLHKZBwQZD"

def post_dog_adv(adv):
	fields = {"link" : "http://povodochek.com/prodazha-sobak/%s/" % adv.get('_id')}
	if adv.get("photos"):
		fields["picture"] = "http://povodochek.com/thumbnail/%s" % adv.get("photos")[0]
	return call_api(method = "POST", 
		node_id = FB_PAGE_ID, 
		edge_name = 'feed', 
		fields = fields)

def call_api(method = "GET", node_id = "", edge_name = "", fields = {}):
	url = "https://graph.facebook.com/v2.0/%s/%s" % (node_id, edge_name)
	fields['access_token'] = FB_PAGE_TOKEN
	if method == "GET":
		return requests.get(url, params = fields).json()
	if method == "POST":
		return requests.post(url, params = fields).json()
	

def post_dog_advs_to_fb():
    for adv in db.get_dog_advs_for_fb(mins = 1440):
        post = post_dog_adv(adv)
        pprint(post)
        db.mark_dog_adv_as_fb_posted(adv.get('_id'), post['id'])


if __name__ == '__main__':
	# adv = db.get_dog_adv('53607cfba3b108152e938746')
	# adv = db.get_dog_adv('5344cd98a3b1082f62019993')
	# post = post_dog_adv(adv)
	# pprint(post)
	eval('{0}()'.format(sys.argv[1]))
	
