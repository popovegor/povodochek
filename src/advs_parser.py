#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import codecs 
import re

def parse_avito_adv(url):
	adv = {}
	r = urllib2.urlopen(url)
	if r.code == 200:
		soup = BeautifulSoup(r.read())
		try:
			adv["title"] = soup.find("h1", {"class": "item_title item_title-large"}).get_text()
			adv["seller"] = soup.find(id="seller").strong.get_text().strip()
			adv["price"] = "".join(re.findall("\d+", soup.find("span", {"class":"p_i_price t-item-price"}).strong.get_text()))	
			adv["desc"] = soup.find(id="desc_text").p.get_text()
			adv["breed"] = soup.find("a", {"class":"link_inverted second-link"}).strong.get_text()
			adv["city"] = soup.find(id="map").span.get_text()
			adv["img"] = [img.attrs.get('src').replace('100x75', "1280x960") for img in soup.find_all("img", {"class": "thumb"})]
		finally:
			print(adv)

	return adv
