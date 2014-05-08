#!/usr/bin/env 
# -*- coding: utf-8 -*-

from  urllib2 import urlopen, quote
import xml.etree.ElementTree as et

def fetch_padezhy(name):
	try:
		url = u"http://export.yandex.ru/inflect.xml?name={0}".format(quote(name.encode('utf-8')))
		res = urlopen(url)
		xml = et.fromstring(res.read())
		padezhy = (i, r, d, v, t, p) = [e.text for e in xml.findall("./inflection")]
		return padezhy
	except ValueError as e:
		print(e)
	finally:
		if res:
			res.close()

	return ([name] * 6)