#!/usr/bin/python
# -*- coding: utf-8 -*-


import vk_auth
import json
import os
from pprint import pprint
import requests
import db
from dic.breeds import (get_breed_dog_name)
from dic.geo import (get_city_name)
from photo_helper import (create_thumbnail, get_thumbnail_filename)
import sys
import config

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


if not config.DEBUG:
    from ThreadedSMTPHandler import ThreadedSMTPHandler
    mail_handler = ThreadedSMTPHandler(subject = 'povodochek:error:vk')
    mail_handler.setLevel(logging.ERROR)
    logger.addHandler(mail_handler)

USER_ID = 4325506
USER_EMAIL = 'popovegor@gmail.com'
USER_PWD = '''/d+Aq7q8Ts?ZMGjs|ShdaMN3j/=q#c:?'''
TMP_FOLDER = '/tmp'

def call_api(method, params, token):
    params['access_token'] = token
    url = "https://api.vk.com/method/%s" % method
    response = requests.get(url, params = params)
    json = response.json()
    pprint(json)
    return json["response"]


def get_wall_messages():
    token, user_id = vk_auth.auth(USER_EMAIL, USER_PWD, USER_ID, ['wall'])
    messages = call_api('wall.get', { 
            'owner_id':-config.VK_GROUP_ID}, token)
    pprint(messages)


def remove_dog_adv(adv_id):
    try:
        token, user_id = vk_auth.auth(USER_EMAIL, USER_PWD, USER_ID, ['wall'])
        adv = db.get_dog_adv_archived(adv_id)
        pprint(adv)
        result = call_api('wall.delete', {
            'post_id':adv.get('vk').get('post_id'), 
            'owner_id':-config.VK_GROUP_ID}, token)
        db.mark_dog_adv_as_vk_deleted(adv.get('_id'))
        return result

    except Exception, e:
        logger.exception(e)
        raise e



def post_dog_adv(adv_id):
    try:
        token, user_id = vk_auth.auth(USER_EMAIL, USER_PWD, USER_ID, ['wall','photos'])
        photo_srv = call_api('photos.getWallUploadServer', {'group_id': config.VK_GROUP_ID}, token)
        files = {}
        photo_id = ''
        adv = db.get_dog_adv(adv_id)
        if adv.get('photos'):
            (photo_name, photo) = db.get_photo(adv.get('photos')[0])
            if photo_name and photo:
                photo_path = os.path.join(TMP_FOLDER, photo_name) 
                with open(photo_path, 'w') as f:
                    f.write(photo)

                files['file'] = open(photo_path, 'rb')

                response = requests.post(photo_srv['upload_url'], files = files)

                photo_srv = json.loads(response.text)

                photo = call_api('photos.saveWallPhoto', {'group_id': config.VK_GROUP_ID, 'photo':photo_srv['photo'], 'server':photo_srv['server'], 'hash': photo_srv['hash']}, token)
                photo_id = photo[0]['id']

        url = u'http://поводочек.рф/prodazha-sobak/%s/' % adv.get('_id')

        msg = u"«{0}»\n{1}, {2}, {3} руб\n{4} {5}\n{6}".format(
            adv.get('title'),
            get_breed_dog_name(adv.get('breed_id')),
            get_city_name(adv.get('city_id')),
            '{0:,}'.format(adv.get('price')).replace(',', ' '),
            adv.get('username'), 
            adv.get('phone') or u'', 
            url
            )

        url = u'http://povodochek.com/prodazha-sobak/%s/' % adv.get('_id')

        post = call_api('wall.post', {'message': msg, \
            'attachments': ",".join([ photo_id, url]), 'owner_id': -config.VK_GROUP_ID, 'from_group': '0', 'signed': 0}, token)

        db.mark_dog_adv_as_vk_posted(adv.get('_id'), post['post_id'])

        return post

    except Exception, e:
        logger.exception(e)
        raise e
    

def post_dog_advs_to_vk():
    for adv in db.get_dog_advs_to_post_in_vk(mins = 3*24*60):
        post = post_dog_adv(adv.get('_id'))
        pprint(post)

def remove_dog_advs_from_vk():
    for adv in db.get_dog_advs_to_remove_from_vk():
        result = remove_dog_adv(adv.get('_id'))
        pprint(result)
             
if __name__ == '__main__':
    func = sys.argv[1]
    args = "{0}".format(sys.argv[2:]).strip("[]")
    ex = '{0}({1})'.format(func, args )
    print(ex)
    eval(ex)