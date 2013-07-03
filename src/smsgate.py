#!/usr/bin/python
# -*- coding: utf-8 -*-

import littlesms
import re


def get_api():
    return littlesms.Api("popovegor@gmail.com", "76IjzV")

def send_sms(message, phones):
    api = get_api()
    raw_phones = [''.join(re.findall(r'(\d+)', phone)) for phone in phones if phone]
    print(raw_phones)
    response = api.send(message, \
        raw_phones, \
        sender = 'Povodochek')
    print(response)
    return response

if __name__ == "__main__":
    # api = littlesms.Api("acc-63c6f51f", "MYTKiNP5")
    api = littlesms.Api("popovegor@gmail.com", "76IjzV")
    print(api.balance())
    print(send_sms(u"Привет от поводочек.рф!", [u"+7(921)7963651"]))