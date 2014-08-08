#!/usr/bin/python
# -*- coding: utf-8 -*-

marks = {
	1 : {'name' : u"Отлично", 'breeding' : True},
	2 : {'name' : u"Очень хорошо", 'breeding' : True},
	3 : {'name' : u"Хорошо", 'breeding' : True},
	4 : {'name' : u"Удовлетворительно", 'breeding' : False},
	5 : {'name' : u"Дисквалификация", 'breeding' : False}
}


def get_marks_for_edit_adv():
	return [ (mark_id, mark.get('name') ) for (mark_id, mark) in marks.items() if mark.get("breeding")]