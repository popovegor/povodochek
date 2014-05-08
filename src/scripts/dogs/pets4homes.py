#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup
import codecs 
import re

def fetch_page_numbers_of_dog_articles():
	number = 1
	r = urllib2.urlopen("http://www.pets4homes.co.uk/pet_advice.php?&browse=dogs")
	if r.code == 200:
		soup = BeautifulSoup(r.read())
		numbers = [int(a.getText()) for a in soup.find_all("a", attrs = {"href":re.compile(r"^/pet_advice\.php\?page=")}) if a.getText().isdigit()]
	return range(1, max(numbers) + 1)

def fetch_dog_article(url):
	page = urllib2.urlopen(url)
	if page.code == 200:
		return page

def fetch_dog_article_likes(url):
	url = "http://wd.sharethis.com/api/getCount2.php?cb=stButtons.processCB&refDomain=www.pets4homes.co.uk&refQuery=pet-advice%2Fdogs%2F&pgurl={0}&pubKey=2920f05e-7f6a-48b9-a7f0-f96f747597a3&url={0}".format(url)
	likes_page = urllib2.urlopen(url)
	likes = 0
	try:
		likes = int(re.findall(r'"total":(\d+)', likes_page.read())[0])
	except Exception, e:
		print(e)

	return likes

def fetch_popular_dog_articles():
	popular_articles = {}
	for article_url in fetch_dog_article_urls()[:]:
		likes = fetch_dog_article_likes(article_url)
		popular_articles[article_url] = likes
	return sorted(popular_articles.items(), key = lambda x : x[1], reverse = True) 

def fetch_dog_article_urls():
	article_urls = []
	page_numbers = fetch_page_numbers_of_dog_articles()
	for page_number in page_numbers:
		page_with_article_headers = urllib2.urlopen("http://www.pets4homes.co.uk/pet_advice.php?page={0}&browse=dogs".format(page_number))
		if page_with_article_headers.code == 200:
			soup = BeautifulSoup(page_with_article_headers.read())
			matcher = r"^http://www.pets4homes.co.uk/pet-advice/"
			for article_a in [article_a for article_a in soup.find_all("a", attrs = {"href": re.compile(matcher)}) if "Full Article" in article_a.getText()]:
				article_urls.append(article_a["href"])
	return article_urls

import os
from os import path

if __name__ == '__main__':
	output = path.join(path.dirname(path.abspath(__file__)), "popular_dog_articles.txt")
	with open(output, "w") as f:
		for url, likes in fetch_popular_dog_articles():
			msg = "{0} - {1}\n".format(likes, url)
			print(msg)
			f.write(msg)