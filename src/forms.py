#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import (Form, BooleanField, TextField, PasswordField, validators, ValidationError, SelectField, TextAreaField, HiddenField)

from wtforms.validators import *

from flask import Markup

from pymongo import MongoClient 
from bson.objectid import ObjectId

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

def breed_name(breed):
    return u"{0}, {1}".format(breed["name"], pets().find_one(breed["pet"])["name"].lower()) 

class Sale(Form):

    # pet = SelectField(u'Тип животного', \
    #     choices = [(u"", u"")] + [(str(pet["_id"]), pet["name"]) for pet in pets().find() ], \
    #     validators = [Required(message=u'Тип животного не выбран')])

    breed = SelectField(u'Порода', \
        choices = [(u"", u"")] + [( breed_key(breed), breed_name(breed))
            for breed in breeds().find()], \
        validators = [Required(message=u'Порода не выбрана')])    

    title = TextField(u"Заголовок", [Required(message=u"Краткое описание не заполнено")])

    desc = TextAreaField(u"Описание", [Required(message=u"Полное описание не заполнено")])

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")


    price = TextField(u"Цена (руб)", [Required(message=u"Цена не указана")])



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