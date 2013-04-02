#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import Form, BooleanField, TextField, PasswordField, validators, ValidationError, SelectField, TextAreaField
from flask import Markup

from pymongo import MongoClient 
from bson.objectid import ObjectId


def mongo():
    return MongoClient().povodochek

def users():
    return mongo().users

def sale_advs():
    return mongo().sales


class Sale(Form):

    pet_type = SelectField(u'Тип животного', \
        choices = [("1", u"Собака"), ("2", u"Кошка")], \
        validators = [validators.Required(message=u'Тип животного не выбран')])    

    breed = SelectField(u'Порода', \
        choices = [("1", u"Померанский шпиц"), ("2", u"Овчарка")], \
        validators = [validators.Required(message=u'Порода не выбрана')])    

    title = TextField(u"Краткое описание", [validators.Required(message=u"Краткое описание не заполнено")])

    description = TextAreaField(u"Полное описание", [validators.Required(message=u"Полное описание не заполнено")])


class SignIn(Form):

    email = TextField(u'Адрес электронной почты', [validators.Email(message=u'Неправильный адрес эл. почты')])

    # def validate_email(form, field):
    #     print("validate email %s" % field.data)
    #     print(users().find_one({'email': field.data}))
    #     if users().find_one({'email': field.data}):
    #         raise ValidationError(u'Адрес %s занят' % field.data)

    remember = BooleanField(u"Запомнить меня")

    password = PasswordField(u'Пароль', [
        validators.Required(message=u"Пароль не указан"),])

class SignUp(Form):

    email = TextField(u'Адрес электронной почты', [validators.Email(message=u'Неправильный адрес эл. почты')])


    def validate_email(form, field):
        print("validate email %s" % field.data)
        print(users().find_one({'email': field.data}))
        if users().find_one({'email': field.data}):
            raise ValidationError(u'Адрес %s занят' % field.data)


    password = PasswordField(u'Пароль', [
        validators.Required(message=u"Пароль не указан"),])
    confirm = PasswordField(u'Повторить пароль', [validators.EqualTo('password', message=u'Пароли не совпадают')])
    accept_tos = BooleanField(Markup(u'С <a href="#">правилами</a> согласен'), [validators.Required(u"Требуется ваше согласие")])