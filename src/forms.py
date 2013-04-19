#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import (Form, BooleanField, TextField, PasswordField, validators, ValidationError, TextAreaField, HiddenField, IntegerField)

from wtforms.validators import *

from flask import Markup

from pymongo import MongoClient 
from bson.objectid import ObjectId

from itertools import groupby

from wtforms_extended_selectfield import SelectField

def mongo():
    return MongoClient().povodochek

def users():
    return mongo().users

def pets():
    return mongo().pets

def breeds():
    return mongo().breeds

def genders():
    return mongo().genders

# def sale_advs():
#     return mongo().sales

class Test(Form):

    pet = SelectField(u'Тип животного', \
        choices = [(pet['_id'], pet['name']) for pet in pets().find()], \
        validators = [Required(message=u'Тип животного не выбран')])  


def breed_key(breed):
    return u"{0}_{1}".format(breed["pet"], breed["_id"])

def get_pet_name(pet_id):
    pet = pets().find_one(pet_id, fileds=["name"])
    return pet["name"] if pet else ""


MSG_REQUIRED = u"Это поле необходимо заполнить"
MSG_MIN = u"Пожалуйста, введите число, большее или равное {0}"
MSG_RANGE = u"Пожалуйста, введите число от {0} до {1}"
MSG_RANGE_LENGTH = u"Пожалуйста, введите значение длиной от {0} до {1} символов"
MSG_MIN_LENGTH = u"Пожалуйста, введите не меньше {0} символов" 

def pets_breeds():
    grouped_by_pet = \
        groupby([breed for breed in breeds().find().sort('pet',1)], lambda x : x["pet"]) 
    key = lambda pet_id: get_pet_name(pet_id)
    value = lambda pet_id, group: [("{0}_{1}".format(pet_id, breed["_id"]), breed["name"]) for breed in sorted(group, key = lambda x: x['order']) ]
    return [ (key(pet_id), value(pet_id, group))
    for pet_id, group in grouped_by_pet ]


class Sale(Form):

    pet = SelectField(u'Вид', \
        choices = [(u"", u"")] + [(str(pet["_id"]), pet["name"]) for pet in pets().find() ],\
        validators = [Required(message=MSG_REQUIRED)])

    breed = SelectField(u'Порода', \
        choices = [("", [("","")] )]  + pets_breeds(), \
        validators = [Required(message=MSG_REQUIRED)])    

    gender = SelectField(u"Пол", choices = [(u"", u"")] + \
        [(str(gender["_id"]), gender["name"]) for gender in genders().find() ])

    title = TextField(u"Заголовок объявления", [Required(message=MSG_REQUIRED), Length(min=10, max=80, message=MSG_RANGE_LENGTH.format(10, 80))])

    desc = TextAreaField(u"Подробное описание", [Required(message=MSG_REQUIRED), Length(min=120, message=MSG_MIN_LENGTH.format(120))])

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")


    price = IntegerField(u"Цена (руб)", [Required(message=MSG_REQUIRED), NumberRange(min=10, max=900000, message=MSG_RANGE.format(10, 900000))])



class Stud(Form):

    pet_type = SelectField(u'Тип животного', \
        choices = [("1", u"Собака"), ("2", u"Кошка")], \
        validators = [Required(message=u'Тип животного не выбран')])    

    breed = SelectField(u'Порода', \
        choices = [("1", u"Померанский шпиц"), ("2", u"Овчарка")], \
        validators = [Required(message=u'Порода не выбрана')])    

    title = TextField(u"Краткое описание", [Required(message=u"Краткое описание не заполнено")])

    description = TextAreaField(u"Полное описание", [Required(message=u"Полное описание не заполнено")])

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")

class SignIn(Form):

    email = TextField(u'Адрес электронной почты', [Email(message=u'Неправильный адрес эл. почты')])

    # def validate_email(form, field):
    #     print("validate email %s" % field.data)
    #     print(users().find_one({'email': field.data}))
    #     if users().find_one({'email': field.data}):
    #         raise ValidationError(u'Адрес %s занят' % field.data)

    remember = BooleanField(u"Запомнить меня")

    password = PasswordField(u'Пароль', [
        Required(message=u"Пароль не указан"),])

class SignUp(Form):

    email = TextField(u'Адрес электронной почты', [Email(message=u'Неправильный адрес эл. почты')])


    def validate_email(form, field):
        print("validate email %s" % field.data)
        print(users().find_one({'email': field.data}))
        if users().find_one({'email': field.data}):
            raise ValidationError(u'Адрес %s занят' % field.data)


    password = PasswordField(u'Пароль', [
        Required(message=u"Пароль не указан"),])
    confirm = PasswordField(u'Повторить пароль', [EqualTo('password', message=u'Пароли не совпадают')])
    accept_tos = BooleanField(Markup(u'С <a href="#">правилами</a> согласен'), [Required(u"Требуется ваше согласие")])



    if __name__ == "__main__":
        print(pets_breeds())
