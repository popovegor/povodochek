#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import (Form, BooleanField, TextField, PasswordField, validators, ValidationError, TextAreaField, HiddenField, IntegerField, RadioField, DateField)

from wtforms.validators import *

from flask import (Markup, url_for)

from pymongo import MongoClient 
from bson.objectid import ObjectId

from itertools import groupby

from wtforms_extended_selectfield import SelectField
from form_helper import *
import re
from security import hash_password, check_password

from helpers import (num, morph_word, str2date, date2str)
from dic.genders import genders
from dic.ages import ages
from dic.breeds import (dogs, cats, get_breed_name, get_breed_by_name, get_breed_by_id, get_breed_dog_name)
from dic.pets import pets, get_pet_name
from dic.cities import (get_city, get_city_region)
from dic.countries import (countries, get_countries_for_dog_adv)
from dic.pet_docs import (dog_docs, doc_dog_pedigrees, doc_dog_pedigrees_rkf)

import config

def db():
    return MongoClient().povodochek

def users():
    return db().users


MSG_REQUIRED = u"Обязательное поле"
MSG_MIN = u"Пожалуйста, введите число, большее или равное {0}"
MSG_RANGE = u"Пожалуйста, введите число от {0} до {1}"
MSG_RANGE_LENGTH = u"Пожалуйста, введите значение длиной от {0} до {1} символов"
MSG_MIN_LENGTH = u"Пожалуйста, введите не меньше {0} символов"
MSG_MAX_LENGTH = u"Пожалуйста, введите не больше {0} символов" 
MSG_EMAIL = u"Пожалуйста, введите корректный адрес электронной почты"
MSG_CHOISE = u""

def pets_breeds():
    _dogs = [(morph_word(get_pet_name(1), ["plur"]), \
        [("%s_%s" % (1, dog_id), dog_name) for dog_id, dog_name in dogs.items()])]
    _cats = [(morph_word(get_pet_name(2), ["plur"]), \
        [("%s_%s" % (2, cat_id), cat_name) for cat_id, cat_name in cats.items()])]
    return _dogs + _cats


def get_breed_by_form_field(field):
	(breed, pet) = (None, None)
	if field.data:
		(breed, pet) = get_breed_by_id(field.data)
		if not breed or not pet:
			(breed, pet) = get_breed_by_name(field.data)
	return (breed, pet)

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
        city = db().cities.find_one({"city_region": matcher},\
            sort = [('city_size',-1)], fileds=["city_id"])
        if city:
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
            raise ValidationError(u'Совпадений не найдено. Выберите населенный пункт из выпадающего списка, введя часть названия.')
        else:
            field.city_id = city.get("city_id")
            field.location = city.get("location")


def validate_breed(form, field):
    if field.data:
        (breed_id, pet_id) = get_breed_by_name(field.data)
        if not breed_id or not pet_id:
            raise ValidationError(u'Совпадений не найдено. Выберите породу из выпадающего списка, введя часть названия.')
        else:
            field.pet_id = pet_id
            field.breed_id = breed_id

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
        check = config.DOMAIN_NAME_CHECK and config.DOMAIN_NAME in field.data
        user = users().find_one({'email': field.data})
        if check or user:
            raise ValidationError(u"Адрес '%s' уже зарегистрирован" % field.data)

    repeat_new_email = TextField(u'Повторить эл. почту', \
        [ Required(message=MSG_REQUIRED), EqualTo('new_email', message=u'Адреса эл. почты не совпадают')])

class ResetPassword(Form):
    email_or_login = TextField(u"Электронная почта или логин", \
        [Required(message=MSG_REQUIRED)], \
        filters = [lambda x : (x or '')])

    def validate_email_or_login(form, field):
        matcher = re.compile("^" + re.escape(field.data) + "$", re.IGNORECASE)
        user = users().find_one({'$or': [{'email': {'$regex' : matcher}},{'login': {'$regex' : matcher}}]})
        if not user:
            raise ValidationError(u"Электронная почта или логин '%s' не найдены" % field.data)
        else:
            field.user = user

class DogSearch(Form):

    #TODO: показывать только те породы, по которым есть объявления
    breed = TextField(u'Порода', default = u"")

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) for 
        gender_id, gender_name in genders.items()])


    city = TextField(u"Местоположение", default = u"")

    distance = IntegerField(u"удаленность")

    photo = BooleanField(u"Только с фото")

    # photo = BooleanField(u"С документами")

    # price
    price_from = IntegerField(u"Цена", \
        # filters = [lambda x : x.replace(' ','') ]
        )
    price_to = IntegerField(u"до")

    price_unit = SelectField(u"", choices = [(0, u"руб"), (1, u"тыс руб")])

    sort = SelectField(Markup(u"сортировать по"), choices = [(1, Markup(u"дороже")), (2, Markup(u"дешевле")), (3, u"дате"), (4, u"привлекательности и дате")], coerce = int)

    page = IntegerField(u"Страница", default = 1)

    perpage = SelectField(u"Объявлений на стр.", default = 15, coerce=int, choices = [(1, 10), (2, 20), (3, 30), (4, 50), (5, 100)])


class SaleSearch(Form):

    #TODO: показывать только те породы, по которым есть объявления
    breed = TextField(u'Порода')

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) for 
        gender_id, gender_name in genders.items()])


    city = TextField(u"Местоположение")

    distance = IntegerField(u"Удаленность, км", default = 150)

    photo = BooleanField(u"Только с фото")

    # price
    price_from = IntegerField(u"Цена, тыс руб", default = 0)
    price_to = IntegerField(u"Цена до", default = 100)

    sort = SelectField(u"Сортировка", choices = [(1, u"Дороже"), (2, u"Дешевле"), (3, u"По дате")], coerce = int)

    page = IntegerField(u"Страница", default = 1)

    perpage = SelectField(u"Объявлений на стр.", default = 15, coerce=int, choices = [(1, 10), (2, 20), (3, 30), (4, 50), (5, 100)])

class Contact(Form):
    username = TextField(u"Имя", validators = [Required(message=MSG_REQUIRED) ])

    city = TextField(u"Город", validators = [validate_location])    
    
    phone = TextField(u"Телефонный номер")
    
    skype = TextField(u"Skype")
    

class Cat(Form):

    breed = TextField(u'Порода', \
        validators = [Required(message=MSG_REQUIRED), validate_breed]) 

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) for gender_id, gender_name in genders.items()])
   
    title = TextField(u"Заголовок объявления", [Required(message=MSG_REQUIRED), Length(min=10, max=80, message=MSG_RANGE_LENGTH.format(10, 80))], \
         description = u"Не более 80 символов."
         )

    desc = TextAreaField(u"Подробное описание", [Required(message=MSG_REQUIRED), Length(min=100, message=MSG_MIN_LENGTH.format(100))], \
        description = u"Не менее 100 символов."
    )

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")

    price = IntegerField(u"Цена (руб)", [Required(message=MSG_REQUIRED), NumberRange(min=10, max=900000, message=MSG_RANGE.format(10, 900000))], \
        description = Markup(u'Указывая реальную цену, покупатели проявят больше интереса к вашему объявлению!'))

    city = TextField(u"Местоположение", [Required(message=MSG_REQUIRED), validate_location], \
        description = u"Введите населенный пункт, в котором продается питомец.")

    phone = TextField(u"Телефонный номер")
    skype = TextField(u"Skype")

    email = TextField(u"Электронная почта / Email")
    username = TextField(u"Имя")

class Dog(Form):

    # breed = SelectField(u'Порода', \
    #     choices = [(0, u"")] + [ (dog_id, dog_name) for (dog_id, dog_name) in dogs.items()], \
    #     coerce = int, 
    #     validators = [Required(message=MSG_REQUIRED)])


    breed = PTextField(u'Порода', \
        validators = [Required(message=MSG_REQUIRED), validate_breed], \
        db_name = 'breed_id', \
        db_in = lambda f: f.breed_id, \
        db_out = lambda v: get_breed_dog_name(v)) 

    gender = PSelectField(u"Пол", \
        choices = [(0, u'-- не указан --')] + [ (gender_id, gender_name) \
        for gender_id, gender_name in genders.items()], \
        coerce=int, \
        attraction = True, \
        db_name = 'gender_id', \
        db_out = lambda v: num(v))
   
    title = PTextField(u"Заголовок объявления", \
        [Required(message=MSG_REQUIRED), Length(min=10, max=80, message=MSG_RANGE_LENGTH.format(10, 80))], \
         description = Markup(u"От 10 до 80 символов, осталось <span id='title_count' class='text-danger'>80</span>."), \
         db_name = 'title')

    desc = PTextAreaField(u"Текст рекламного объявления", \
        [Required(message=MSG_REQUIRED), Length(max=1000, message=MSG_MAX_LENGTH.format(1000))], \
        description = Markup(u"Не более 1000 символов, осталось <span class='text-danger' id='desc_count'>1000</span>."))

    photos = PHiddenField(u"Имена фалов, загруженных при помощи plupload", \
        attraction = True, \
        db_in = lambda f: f.photonames, 
        db_out = lambda v: ",".join(v or []))

    price = PIntegerField(u"Цена", \
        [Required(message=MSG_REQUIRED), \
         NumberRange(min=5000, max=300000, \
            message=MSG_RANGE.format(5000, 300000))], \
        # filters = [lambda x: x.replace(' ','')], \
        description = Markup(u'От 5&nbsp;000 до 300&nbsp;000 руб. Объявление с нереальной ценой будет <span style="color:red">удалено!</span>'),\
        db_out = lambda v: num(v))

    price_haggle = PBooleanField(u"Возможен торг") #Торг

    price_hp =  PBooleanField(u"Рассрочка") #рассрочка hire purchase

    city = PTextField(u"Местоположение", \
        [Required(message=MSG_REQUIRED), validate_location], \
        description = u"Населенный пункт, в котором можно посмотреть и купить собаку.", \
        db_name = 'city_id', \
        db_in = lambda f: f.city_id, \
        db_out = lambda v : get_city_region(v))

    
    color = PTextField(u"Окрас", \
        attraction = True)

    contract = PBooleanField(u"Договор купли-продажи", \
        attraction = True)

    delivery = PBooleanField(u"Возможна доставка в другой город")

    doc = PSelectField(u"Документы о происхождении", \
        choices = [(0, u"-- нет документов --")] + [(doc_id , doc_name) for (doc_id, doc_name) in dog_docs.items()], \
        coerce = int, \
        attraction = True, \
        db_name = 'doc_id')
    
    father_name = PTextField(Markup(u"<small>Кличка</small>"), \
        attraction = True, \
        depends = {"id":"doc"})

    father_country = PSelectField(Markup(u"<small>Страна происхождения</small>"), \
        choices = [(0, u"-- не указана --")] + get_countries_for_dog_adv(), \
        coerce = int, \
        attraction = True, \
        depends = {"id":"doc"}, \
        db_name = 'father_country_id')

    father_misc = PTextAreaField(Markup(u"<small>Прочее</small>"))

    father_pedigree = PTextField(Markup(u"<small>№ родословной</small>"), \
        attraction = True, \
        depends = {"id":"doc"})

    mother_name = PTextField(Markup(u"<small>Кличка</small>"), \
        attraction = True,\
        depends = {"id":"doc"})

    mother_country = PSelectField(Markup(u"<small>Страна происхождения</small>"), \
        choices = [(0, u"-- не указана --")] + get_countries_for_dog_adv(), \
        coerce = int, \
        attraction = True,\
        depends = {"id":"doc"}, \
        db_name = 'mother_country_id')

    mother_misc = PTextAreaField(Markup(u"<small>Прочее</small>"))

    mother_pedigree = PTextField(Markup(u"<small>№ родословной</small>"), \
        attraction = True, \
        depends = {"id":"doc"})

    birthday = PTextField(Markup(u"Дата рождения"), \
        description = u"Дата в формате день/месяц/год, например, 24/02/2014", \
        attraction = True, \
        db_in = lambda f: str2date(f.data), \
        db_out = lambda v : date2str(v, "%d%m%Y") )
    

    tatoo = PTextField(Markup(u"<small>№ клейма</small>"), \
        attraction = True, \
        depends = {"id":"doc"})

    pedigree = PTextField(Markup(u"<small>№ родословной</small>"), \
        attraction = True, \
        attraction_depends = {"id":"doc", "values": doc_dog_pedigrees.keys()}, \
        depends = {"id":"doc", "values": doc_dog_pedigrees.keys()})
    
    vaccination = PBooleanField(u"Вакцинация (прививки) по возрасту", \
        attraction = True)

    vetpassport = PBooleanField(u"Ветеринарный паспорт", \
        attraction = True)

    microchip = PBooleanField(u"Микрочип")

    breeding = PBooleanField(Markup(u"<small>Допуск в разведение</small>"), \
        depends = {"id":"doc", "values": doc_dog_pedigrees_rkf.keys()})

    show = PBooleanField(Markup(u"<small>Подходит для выставок</small>"))

    phone = PTextField(u"Телефонный номер")

    skype = PTextField(u"Skype")

    username = PTextField(u"Контактное лицо", \
        validators = [Required(message=MSG_REQUIRED)])

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

    remember = BooleanField(u"Запомнить меня", default = True)

    password = PasswordField(u'Пароль', \
        [Required(message=MSG_REQUIRED)])

class SignUpBasic(Form):
    login = TextField(u"Логин", \
        [Required(message=MSG_REQUIRED), 
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36)), \
        validate_login_used],\
        filters = [lambda x : (x or '')], \
        description = u'Длина логина от 6 до 36 символов.')


    email = TextField(u'Электронная почта / Email', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()], \
        description = u"После регистрации не забудьте подтвердить эл. почту, перейдя по ссылке в письме.")

    def validate_email(form, field):
        user = users().find_one({'email': field.data})
        check = config.DOMAIN_NAME_CHECK and config.DOMAIN_NAME in field.data
        if check or user:
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

    message = TextAreaField(u"Сообщение", \
    	validators = [Required(message=MSG_REQUIRED)])

    email = TextField(u'Ваша электронная почта', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()])

    sms_alert = BooleanField(Markup(u"Отправить автору <abbr title='Получатель письма получет короткое sms-оповещение о новом электронном письме.'>sms-оповещение</abbr> (<i>бесплатно</i>)"))


if __name__ == "__main__":
    print(pets_breeds())
