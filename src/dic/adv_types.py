#!/usr/bin/python
# -*- coding: utf-8 -*-

LITTER = 1
FEMALE = 2
MALE = 3

adv_dog_type_litter = {
	LITTER: {"name_edit" : u"Щенков", "name_view" : u"щенков"}
}

adv_dog_type_female = {
	FEMALE : {"name_edit" : u"Девочку / суку", "name_view" : u"девочку"}
}

adv_dog_type_male = {
	MALE : {"name_edit" : u"Мальчика / кобеля", "name_view" : u"мальчика"}
}

adv_dog_type_single = {}

adv_dog_type_single.update(adv_dog_type_female)
adv_dog_type_single.update(adv_dog_type_male)

adv_dog_types = {}
adv_dog_types.update(adv_dog_type_litter)
adv_dog_types.update(adv_dog_type_single)


def get_adv_type_name(adv_type_id):
	adv_type = adv_dog_types.get(adv_type_id)
	return adv_type.get('name_view') if adv_type else u""
