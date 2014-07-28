#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import codecs 
import re
from pprint import pprint
import time
import os
from os import path


def extract_emails_from_page(html):
    emails = []
    soup = BeautifulSoup(html)
    for stigma in soup.find_all("div", attrs = {'class':'stigma_item'}):
        for td in stigma.table.find_all("td"):
            if u"E-mail" in unicode(td) and td.next_sibling:
                email = td.next_sibling
                # print(email.prettify())
                email_clean = unicode(email).replace('<img src="http://zooclub.ru/img/at11.gif">', "@").replace("</img>", "").strip("<td>").strip("</td>")
                if email_clean:
                    emails.append(email_clean)
    return set(emails)

if __name__ == '__main__':
    emails = set()
    for p in xrange(25, 285):
        r = requests.get("http://zooclub.ru/stigma/", params = {'p' : p})
        print(p)
        counter = 0
        while r.status_code != requests.codes.ok:
            r = requests.get("http://zooclub.ru/stigma/", params = {'p' : p})
            counter += 1
            print(counter)
            time.sleep(1)
        emails = emails | extract_emails_from_page(r.text)

    output = path.join(path.dirname(path.abspath(__file__)), "zooclub_emails.txt")
    with codecs.open(output, "w", "utf-8") as f:
        for email in emails:
            try:
                f.write(u"%s\n" % unicode(email))
            except Exception, e:
                print(e)
            
