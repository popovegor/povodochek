#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import (Form, BooleanField, TextField, PasswordField, validators, ValidationError, TextAreaField, HiddenField, IntegerField)

from wtforms.validators import *

from flask import Markup

from pymongo import MongoClient 
from bson.objectid import ObjectId

from itertools import groupby

from wtforms_extended_selectfield import SelectField
import re
from security import hash_password, check_password

from helpers import num

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

def cities():
    return mongo().cities

def ages():
    return mongo().ages

# def sale_advs():
#     return mongo().sales

class Test(Form):

    pet = SelectField(u'Тип животного', \
        choices = [(pet['id'], pet['name']) for pet in pets().find()], \
        validators = [Required(message=u'Тип животного не выбран')])  

def breed_key(breed):
    return u"{0}_{1}".format(breed["pet_id"], breed["id"])

def get_pet_name(pet_id):
    pet = pets().find_one({"id": pet_id}, fields=["name"])
    return pet["name"] if pet else ""


MSG_REQUIRED = u"Это обязательное поле"
MSG_MIN = u"Пожалуйста, введите число, большее или равное {0}"
MSG_RANGE = u"Пожалуйста, введите число от {0} до {1}"
MSG_RANGE_LENGTH = u"Пожалуйста, введите значение длиной от {0} до {1} символов"
MSG_MIN_LENGTH = u"Пожалуйста, введите не меньше {0} символов" 
MSG_EMAIL = u"Пожалуйста, введите корректный адрес электронной почты"

def pets_breeds():
    grouped_by_pet = \
        groupby([breed for breed in breeds().find().sort('pet_id',1)], lambda x : x["pet_id"]) 
    key = lambda pet_id: get_pet_name(pet_id)
    value = lambda pet_id, group: [("{0}_{1}".format(pet_id, breed["id"]), breed["name"]) for breed in sorted(group, key = lambda x: x['order']) ]
    return [ (key(pet_id), value(pet_id, group)) for pet_id, group in grouped_by_pet ]


def get_city_by_city_and_region(city_and_region):
    city = None
    if city_and_region: 
        matcher = re.compile(u"^" + re.escape(city_and_region.strip()), re.IGNORECASE)
        city = cities().find_one({"city_region": matcher}, fileds=["id", "region_id", "region_name", "city_name", "location"])
    return city

def check_location(form, field):
    field.city_id = None
    if field.data:
        city = get_city_by_city_and_region(field.data)
        if not city :
            raise ValidationError(u'Неправильно указан населенный пункт')
        else:
            field.city_id = city.get("id")
            field.location = city.get("location")


class ChangePassword(Form):
    current_password = PasswordField(u"Текущий пароль", \
        [Required(message=MSG_REQUIRED)])

    def validate_current_password(form, field):
        user = users().find_one({'_id': ObjectId(form.current_user.id)})
        if not user or not check_password(user.get("pwd_hash"), field.data):
            raise ValidationError(u"Указан неправильный пароль")

    new_password = PasswordField(u"Новый пароль", \
        [Required(message=MSG_REQUIRED), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36))])

    repeat_new_password = PasswordField(u'Повторить новый пароль', \
        [ Required(message=MSG_REQUIRED), EqualTo('new_password', message=u'Пароли не совпадают.')])


class ResetPassword(Form):
    email = TextField(u"Адрес электронной почты", \
        [Required(message=MSG_REQUIRED), Email(message=MSG_EMAIL)])

    def validate_email(form, field):
        user = users().find_one({'email': field.data})
        if not user:
            raise ValidationError(u"Адрес '%s' не зарегистрирован." % field.data)


class SaleSearch(Form):

    pet = SelectField(u'Вид', \
        choices = [(u"", u"")] + [(str(pet["id"]), pet["name"]) for pet in pets().find() ])

    #TODO: показывать только те породы, по которым есть объявления
    breed = SelectField(u'Порода', \
        choices = [("", [("","")] )]  + pets_breeds())    

    gender = SelectField(u"Пол", choices = [(u"", u"")] + \
        [(str(gender["id"]), gender["name"]) for gender in genders().find() ])

    age = SelectField(u"Возраст", \
        choices = [(u"", u"")] + [(str(age["id"]), age["name"]) for age in ages().find()])

    city = TextField(u"Местоположение")

    distance = IntegerField(u"Расстояние, км", default = 150)

    photo = BooleanField(u"Только с фото")

    price_from = IntegerField(u"Цена, тыс руб", default = 0, filters= [lambda x: x * 1000])
    price_to = IntegerField(u"Цена до", default = 0.1,  filters= [lambda x: x * 1000])

class Sale(Form):

    pet = SelectField(u'Вид',\
        choices = [(u"", u"")] + [(str(pet["id"]), pet["name"]) for pet in pets().find() ],\
        validators = [Required(message=MSG_REQUIRED)])

    breed = SelectField(u'Порода', \
        choices = [("", [("","")] )]  + pets_breeds(), \
        validators = [Required(message=MSG_REQUIRED)])    

    gender = SelectField(u"Пол", choices = [(u"", u"")] + \
        [(str(gender["id"]), gender["name"]) for gender in genders().find() ], \
        validators = [Required(message=MSG_REQUIRED)])

    # заголовок объявления
    title = TextField(u"Заголовок объявления", [Required(message=MSG_REQUIRED), Length(min=10, max=80, message=MSG_RANGE_LENGTH.format(10, 80))])

    desc = TextAreaField(u"Подробное описание", [Required(message=MSG_REQUIRED), Length(min=120, message=MSG_MIN_LENGTH.format(120))])

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")

    price = IntegerField(u"Цена (руб)", [Required(message=MSG_REQUIRED), NumberRange(min=10, max=900000, message=MSG_RANGE.format(10, 900000))])

    city = TextField(u"Местоположение", [Required(message=MSG_REQUIRED), check_location])

    age = SelectField(u"Возраст", \
        choices = [(u"", u"")] + [(str(age["id"]), age["name"]) for age in ages().find()], \
        validators = [Required(message=MSG_REQUIRED)])

class Contact(Form):
    username = TextField(u"Имя", validators = [Required(message=MSG_REQUIRED) ])

    city = TextField(u"Город", validators = [check_location])    

    phone = TextField(u"Телефонный номер")

class Activate(Form): 

    email = TextField(u"Адрес электронной почты", \
        [Required(message=MSG_REQUIRED), Email(message=MSG_EMAIL)])

    def validate_email(form, field):
        print("validate confirm  email %s" % field.data)
        if not users().find_one({'email': field.data}):
            raise ValidationError(u"Адрес '%s' не зарегистрирован." % field.data)

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

    email = TextField(u"Адрес электронной почты", \
        [Required(message=MSG_REQUIRED), Email(message=MSG_EMAIL)])

    # def validate_email(form, field):
    #     print("validate email %s" % field.data)
    #     print(users().find_one({'email': field.data}))
    #     if users().find_one({'email': field.data}):
    #         raise ValidationError(u'Адрес %s занят' % field.data)

    remember = BooleanField(u"Запомнить меня")

    password = PasswordField(u'Пароль', [
        Required(message=MSG_REQUIRED),])

class SignUp(Form):

    username = TextField(u"Имя", [Required(message=MSG_REQUIRED)])

    email = TextField(u'Адрес электронной почты', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)])

    def validate_email(form, field):
        print("validate email %s" % field.data)
        print(users().find_one({'email': field.data}))
        if users().find_one({'email': field.data}):
            raise ValidationError(u"Адрес '%s' занят" % field.data)

    password = PasswordField(u"Пароль", \
        [Required(message=MSG_REQUIRED), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36))])

    repeat_password = PasswordField(u'Повторить пароль', \
        [ Required(message=MSG_REQUIRED), EqualTo('password', message=u'Пароли не совпадают.')])

    accept_tos = BooleanField(Markup(u'С <a href="#">правилами</a> согласен'), [Required(u"Требуется ваше согласие")])


if __name__ == "__main__":
    print(pets_breeds())
