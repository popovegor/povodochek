#!/usr/bin/python
# -*- coding: utf-8 -*-

doc_dog_pedigrees = {
	1 : u"Родословная РКФ (FCI)", 
	3 : u"Родословная СКОР (IKU)",
	5 : u"Родословная МАК «Добрый мир» (UCI)"}

doc_puppy_cards = {
	2 : u"Метрика щенка РКФ (FCI)", \
    4 : u"Метрика щенка СКОР (IKU)", \
    6 : u"Метрика щенка МАК «Добрый мир» (UCI)" 
}

dog_docs = dict(\
	[ (id, name) for (id, name) in doc_dog_pedigrees.items()] + \
	[ (id, name) for (id, name) in doc_puppy_cards.items()])

def get_doc_dog_name(doc_id):
	doc_name = dog_docs.get(doc_id)
	return doc_name or u""
