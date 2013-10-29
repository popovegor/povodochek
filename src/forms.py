#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import (Form, BooleanField, TextField, PasswordField, validators, ValidationError, TextAreaField, HiddenField, IntegerField, RadioField)

from wtforms.validators import *

from flask import (Markup, url_for)

from pymongo import MongoClient 
from bson.objectid import ObjectId

from itertools import groupby

from wtforms_extended_selectfield import SelectField
import re
from security import hash_password, check_password

from helpers import (num, morph_word)
from dic.genders import genders
from dic.ages import ages
from dic.breeds import (dogs, cats, get_breed_name)
from dic.pets import pets, get_pet_name
from dic.cities import (get_city)

def db():
    return MongoClient().povodochek

def users():
    return db().users


MSG_REQUIRED = u"Это обязательное поле"
MSG_MIN = u"Пожалуйста, введите число, большее или равное {0}"
MSG_RANGE = u"Пожалуйста, введите число от {0} до {1}"
MSG_RANGE_LENGTH = u"Пожалуйста, введите значение длиной от {0} до {1} символов"
MSG_MIN_LENGTH = u"Пожалуйста, введите не меньше {0} символов" 
MSG_EMAIL = u"Пожалуйста, введите корректный адрес электронной почты"

def pets_breeds():
    _dogs = [(morph_word(get_pet_name(1), ["plur"]), \
        [("%s_%s" % (1, dog_id), dog_name) for dog_id, dog_name in dogs.items()])]
    _cats = [(morph_word(get_pet_name(2), ["plur"]), \
        [("%s_%s" % (2, cat_id), cat_name) for cat_id, cat_name in cats.items()])]
    return _dogs + _cats


def get_city_by_city_field(field):
    city = None
    if field.data:
        city = get_city_by_city_id(field.data)
        if not city:
            city = get_city_by_city_and_region(field.data)
    return city

def get_city_by_city_and_region(city_and_region):
    city = None
    if city_and_region: 
        matcher = re.compile(u"^" + re.escape(city_and_region.strip()), re.IGNORECASE)
        city = db().cities.find_one({"city_region": matcher}, fileds=["city_id"])
        return get_city_by_city_id(city.get('city_id'))
    return city

def get_city_by_city_id(city_id):
    city = None
    if (isinstance(city_id, unicode) and city_id.isdigit()) \
        or (isinstance(city_id, int)):
        city = get_city(int(city_id))
    return city


def validate_location(form, field):
    field.city_id = None
    if field.data:
        city = get_city_by_city_field(field)
        if not city:
            raise ValidationError(u'Неправильно указан населенный пункт')
        else:
            field.city_id = city.get("city_id")
            field.location = city.get("location")

def validate_login_used(form, field):
    matcher = re.compile("^" + re.escape(field.data) + "$", re.IGNORECASE)
    user = users().find_one({'login': {'$regex': matcher}})
    if user:
        raise ValidationError(u"Логин '%s' занят" % field.data)


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


class ChangeEmail(Form):
    
    new_email = TextField(u"Новая эл. почта", \
        [Required(message=MSG_REQUIRED), Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()])

    def validate_new_email(form, field):
        print("validate confirm email %s" % field.data)
        if users().find_one({'email': field.data}):
            raise ValidationError(u"Адрес '%s' уже зарегистрирован" % field.data)

    repeat_new_email = TextField(u'Повторить эл. почту', \
        [ Required(message=MSG_REQUIRED), EqualTo('new_email', message=u'Адреса эл. почты не совпадают')])

class ResetPassword(Form):
    email_or_login = TextField(u"Электронная почта или Логин", \
        [Required(message=MSG_REQUIRED)], \
        filters = [lambda x : (x or '').lower()])

    def validate_email_or_login(form, field):
        user = users().find_one({'$or': [{'email': field.data}, {'login':field.data}]})
        if not user:
            raise ValidationError(u"Электронная почта или Логин '%s' не найдены" % field.data)


class SaleSearch(Form):

    pet = SelectField(u'Тип животного', \
        choices = [(u"", u"")] + [(str(pet_id), pet_name) for pet_id, pet_name in pets.items() ])

    #TODO: показывать только те породы, по которым есть объявления
    breed = SelectField(u'Порода', \
        choices = [("", [("","")] )]  + pets_breeds())

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) for 
        gender_id, gender_name in genders.items()])


    city = TextField(u"Местоположение")

    distance = IntegerField(u"Расстояние, км", default = 150)

    photo = BooleanField(u"Только с фото")

    # price
    price_from = IntegerField(u"Цена, тыс руб", default = 0)
    price_to = IntegerField(u"Цена до", default = 100)

    sort = SelectField(u"Сортировка", choices = [(1, u"Дороже"), (2, u"Дешевле"), (3, u"Новее")], coerce = int)

    page = IntegerField(u"Страница", default = 1)

    perpage = SelectField(u"Объявлений на стр.", default = 15, coerce=int, choices = [(1, 10), (2, 20), (3, 30), (4, 50), (5, 100)])

class Contact(Form):
    username = TextField(u"Имя", validators = [Required(message=MSG_REQUIRED) ])

    city = TextField(u"Город", validators = [validate_location])    
    city_adv_hide = BooleanField(u"Не показывать город в объявлениях")

    phone = TextField(u"Телефонный номер")
    phone_adv_hide = BooleanField(u"Не показывать телефонный номер в объявлениях")
    phone_adv_sms = BooleanField(Markup(u"Присылать sms-оповещения об отликах на объявления (<i>бесплатно</i>)"))

    skype = TextField(u"Skype")
    skype_adv_hide = BooleanField(u"Не показывать skype-номер в объявлениях")


class Sale(Form):

    pet = SelectField(u'Тип животного',\
        choices = [(u"", u"")] + [(str(pet_id), pet_name) for pet_id, pet_name in pets.items() ], \
        validators = [Required(message=MSG_REQUIRED)])

    breed = SelectField(u'Порода', \
        choices = [("", [("","")] )]  + pets_breeds(), \
        validators = [Required(message=MSG_REQUIRED)], \
        description = u"Перед тем как выбрать породу, укажите тип животного выше.") 

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) for gender_id, gender_name in genders.items()])
   
    title = TextField(u"Заголовок объявления", [Required(message=MSG_REQUIRED), Length(min=10, max=80, message=MSG_RANGE_LENGTH.format(10, 80))], \
         description = u"Не более 80 символов."
         )

    desc = TextAreaField(u"Подробное описание", [Required(message=MSG_REQUIRED), Length(min=120, message=MSG_MIN_LENGTH.format(120))], \
        description = u"Не менее 120 символов."
    )

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")

    price = IntegerField(u"Цена (руб)", [Required(message=MSG_REQUIRED), NumberRange(min=10, max=900000, message=MSG_RANGE.format(10, 900000))], \
        description = Markup(u'Указывайте <abbr data-status="loading" id="price-desc" data-toggle="tooltip" title="Указываю реальную цену, вы многократно повышаете свои шансы успешной продажи, так как покупатели проявят больше интереса к вашему объявлению.">достоверную цену</abbr>!'))

    city = TextField(u"Местоположение", [Required(message=MSG_REQUIRED), validate_location], \
        description = u"Введите населенный пункт, в котором продается питомец.")

    phone = TextField(u"Телефонный номер")
    skype = TextField(u"Skype")

    email = TextField(u"Электронная почта / Email")
    username = TextField(u"Имя пользователя")


class Activate(Form): 

    email = TextField(u"Электронная почта", \
        [Required(message=MSG_REQUIRED), Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()])

    def validate_email(form, field):
        print("validate confirm  email %s" % field.data)
        if not users().find_one({'email': field.data}):
            raise ValidationError(u"Адрес '%s' не зарегистрирован" % field.data)

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

    login = TextField(u"Логин", \
        [Required(message=MSG_REQUIRED)])

    remember = BooleanField(u"Запомнить меня")

    password = PasswordField(u'Пароль', \
        [Required(message=MSG_REQUIRED)])

class SignUpBasic(Form):
    login = TextField(u"Логин", \
        [Required(message=MSG_REQUIRED), \
        Regexp(u"^[.a-zA-Z0-9_-]+$", message=u"Неправильный формат: только цифры, латинские буквы, дефисы, подчеркивания и точки."), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36)), \
        validate_login_used],\
        filters = [lambda x : (x or '').lower()], \
        description = u'Допускается вводить латинские буквы, цифры, дефисы, подчёркивания и точки, от 6 до 36 символов.')


    email = TextField(u'Эл. почта / Email', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()], \
        description = u"После регистрации не забудьте подтвердить эл. почту, перейдя по ссылке в письме.")

    def validate_email(form, field):
        user = users().find_one({'email': field.data})
        if user:
            raise ValidationError(u"Адрес '%s' занят" % field.data)

    password = PasswordField(u"Пароль", \
        [Required(message=MSG_REQUIRED), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36))],
        description = u"Длина пароля от 6 до 36 символов.")

    accept_tos = BooleanField(Markup(u'Я согласен с <a target="_blank" href="/tos/">правилами</a>'), [Required(u"Требуется ваше согласие")])

class SignUp(Form):

    username = TextField(u"Имя", [Required(message=MSG_REQUIRED)])

    login = TextField(u"Логин", \
        [Required(message=MSG_REQUIRED), \
        Regexp(u"^[.a-zA-Z0-9_-]+$", message=u"Неправильный формат: только цифры, латинские буквы, дефисы, подчеркивания и точки."), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36)),\
        validate_login_used],\
        filters = lambda x : (x or '').lower(), \
        description = u'Допускается вводить латинские буквы, цифры, дефисы, подчёркивания и точки, от 6 до 36 символов.')

    email = TextField(u'Эл. почта / Email', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()], \
        description = u"После регистрации не забудьте подтвердить эл. почту, перейдя по ссылке в письме.")

    def validate_email(form, field):
        user = users().find_one({'email': field.data})
        if user:
            raise ValidationError(u"Адрес '%s' занят" % field.data)

    password = PasswordField(u"Пароль", \
        [Required(message=MSG_REQUIRED), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36))],
        description = u"Длина пароля от 6 до 36 символов.")

    repeat_password = PasswordField(u'Повторить пароль', \
        [ Required(message=MSG_REQUIRED), EqualTo('password', message=u'Пароли не совпадают.')])

    accept_tos = BooleanField(Markup(u'С <a target="_blank" href="/tos/">правилами</a> согласен'), [Required(u"Требуется ваше согласие")])


class SendMail(Form):
    username = TextField(u"Ваше имя", \
        validators = [Required(message=MSG_REQUIRED)])

    subject = TextField(u"Тема", \
        default = u"Сообщение от пользователя сайта Поводочек", \
        validators = [Required(message=MSG_REQUIRED)])

    message = TextAreaField(u"Сообщение")

    email = TextField(u'Ваша электронная почта', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()])

    sms_alert = BooleanField(Markup(u"Отправить автору <abbr title='Получатель письма получет короткое sms-оповещение о новом электронном письме.'>sms-оповещение</abbr> (<i>бесплатно</i>)"))


if __name__ == "__main__":
    print(pets_breeds())
