#!/usr/bin/python
# -*- coding: utf-8 -*-

doc_dog_pedigrees_rkf = {
	1 : u"Cвидетельство о происхождении РКФ (FCI)",
	5 : u"Certified Export Pedigree RKF (FCI)"
}

doc_dog_pedigrees_skor = {
	3 : u"Cвидетельство о происхождении СКОР (IKU)"
}

doc_dog_pedigrees = dict(
	[ (id, name) for (id, name) in doc_dog_pedigrees_rkf.items()]
	+
	[ (id, name) for (id, name) in doc_dog_pedigrees_skor.items()]
)

doc_puppy_cards = {
	2 : u"Метрика щенка РКФ (FCI)", 
    4 : u"Метрика щенка СКОР (IKU)" 
}

dog_docs = dict(
	 [ (id, name) for (id, name) in doc_puppy_cards.items()]
	 + 
	 [ (id, name) for (id, name) in doc_dog_pedigrees.items()]
	)

def get_doc_dog_name(doc_id):
	doc_name = dog_docs.get(doc_id)
	return doc_name or u""
