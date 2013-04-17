#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import (Form, BooleanField, TextField, PasswordField, validators, ValidationError, TextAreaField, HiddenField)

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

# def sale_advs():
#     return mongo().sales

class Test(Form):

    pet = SelectField(u'Тип животного', \
        choices = [(pet['_id'], pet['name']) for pet in pets().find()], \
        validators = [Required(message=u'Тип животного не выбран')])  


def breed_key(breed):
    return u"{0}_{1}".format(breed["pet"], breed["_id"])

def get_pet_name(pet_id):
    pet = pets().find_one(pet_id, {"name"})
    return pet["name"] if pet else ""


MSG_REQUIRED = u"Это поле необходимо заполнить"

def pets_breeds():
    return [
    # (k, [ (br[1]["_id"], bd[1]["name"]) for br in g]) 
    (get_pet_name(pet_id), [("{0}_{1}".format(pet_id, g_breed["_id"]), g_breed["name"]) for g_breed in g ] )
    for pet_id, g in groupby([breed for breed in breeds().find()], lambda x : x["pet"])]


class Sale(Form):

    pet = SelectField(u'Вид', \
        choices = [(u"", u"")] + [(str(pet["_id"]), pet["name"]) for pet in pets().find() ],\
        validators = [Required(message=MSG_REQUIRED)])

    breed = SelectField(u'Порода', \
        choices = [("", [("","")] )]  + pets_breeds(), \
        validators = [Required(message=MSG_REQUIRED)])    

    title = TextField(u"Заголовок объявления", [Required(message=MSG_REQUIRED)])

    desc = TextAreaField(u"Подробное описание", [Required(message=MSG_REQUIRED)])

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")


    price = TextField(u"Цена (руб)", [Required(message=MSG_REQUIRED)])



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