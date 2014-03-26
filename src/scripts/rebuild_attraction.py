#!/usr/bin/python
# -*- coding: utf-8 -*-

import db
from forms import (Dog)
from form_helper import (calc_attraction)
import sys


def dog_advs():
	for dog in db.dog_advs.find():
		form = Dog()
		for f in form:
			f.set_db_val(dog.get(f.get_db_name()))
		attraction = calc_attraction(form)
		print(attraction)
		db.dog_advs.update(dog, \
			{'$set': {'attraction': attraction}}, upsert = False)


if __name__ == '__main__':
	eval('{0}()'.format(sys.argv[1]))