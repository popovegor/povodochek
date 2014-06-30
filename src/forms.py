#!/usr/bin/python
# -*- coding: utf-8 -*-


from wtforms import (Form, BooleanField, TextField, PasswordField, validators, ValidationError, TextAreaField, HiddenField, IntegerField, RadioField, DateField, DateTimeField)

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
import dic.genders as genders
import dic.ages as ages
import dic.breeds as breeds 
from dic.pets import pets, get_pet_name
import dic.geo as geo
from dic.pet_docs import (dog_docs, doc_dog_pedigrees, 
    doc_dog_pedigrees_rkf, doc_puppy_cards)


import config
import db


MSG_REQUIRED = u"Обязательное поле"
MSG_MIN = u"Пожалуйста, введите число, большее или равное {0}"
MSG_RANGE = u"Пожалуйста, введите число от {0} до {1}"
MSG_RANGE_LENGTH = u"Пожалуйста, введите значение длиной от {0} до {1} символов"
MSG_MIN_LENGTH = u"Пожалуйста, введите не меньше {0} символов"
MSG_MAX_LENGTH = u"Пожалуйста, введите не больше {0} символов" 
MSG_EMAIL = u"Пожалуйста, введите корректный адрес электронной почты"
MSG_CHOISE = u""

def get_breed_from_field(field):
    breed = None
    if field.data:
        breed = breeds.get_breed_by_id(field.data)
        if not breed:
            breed = breeds.get_breed_by_name(field.data)
            if not breed:
                breed = breeds.get_breed_by_partname(field.data)
    return breed

def get_geo_from_field(field):
    region = get_region_from_field(field)
    print(1, region)
    city = None
    if not region:
        city = get_city_by_field(field)
        if city:
            region = db.get_region_by_id(city.get("region_id"))
    return (city, region)

def get_region_from_field(field):
    region = None
    if field.data:
        region = db.get_region_by_id(field.data)
        if not region:
            region = db.get_region_by_name(field.data)
    return region

def get_city_by_field(field):
    city = None
    if field.data:
        city = db.get_city_by_id(field.data)
        if not city:
            city = db.get_city_by_city_and_region(field.data)
    return city


def validate_location(form, field):
    field.city_id = None
    if field.data:
        city = get_city_by_field(field)
        if not city:
            raise ValidationError(u'Совпадений не найдено. Выберите населенный пункт из выпадающего списка, введя часть названия.')
        else:
            field.city_id = city.get("city_id")
            field.region_id = city.get("region_id")
            field.location = city.get("location")


def validate_breed(form, field):
    if field.data:
        breed = get_breed_from_field(field)
        if not breed:
            raise ValidationError(u'Совпадений не найдено. Выберите породу из выпадающего списка, введя часть названия.')
        else:
            field.breed_id = breed.get("breed_id")

def validate_login_used(form, field):
    user = db.get_user_by_login(field.data)
    if user:
        raise ValidationError(u"Логин '%s' занят" % field.data)

class ChangePassword(Form):
    current_password = PasswordField(u"Текущий пароль", \
        [Required(message=MSG_REQUIRED)])

    def validate_current_password(form, field):
        user = db.get_user(form.current_user.id)
        if not user or not check_password(user.get("pwd_hash"), field.data):
            raise ValidationError(u"Указан неправильный пароль")

    new_password = PasswordField(u"Новый пароль", \
        [Required(message=MSG_REQUIRED), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36))])

    repeat_new_password = PasswordField(u'Повторить новый пароль', \
        [ Required(message=MSG_REQUIRED), EqualTo('new_password', message=u'Пароли не совпадают.')])


class ChangeEmail(Form):
    
    new_email = PTextField(u"Новая эл. почта", \
        [Required(message=MSG_REQUIRED), Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()])

    def validate_new_email(form, field):
        print("validate confirm email %s" % field.data)
        check = config.DOMAIN_NAME_CHECK and config.DOMAIN_NAME in field.data
        user = db.users.find_one({'email': field.data})
        if check or user:
            raise ValidationError(u"Адрес '%s' уже зарегистрирован" % field.data)

    repeat_new_email = PTextField(u'Повторить эл. почту', \
        [ Required(message=MSG_REQUIRED), EqualTo('new_email', message=u'Адреса эл. почты не совпадают')])

class ResetPassword(Form):
    email_or_login = PTextField(u"Электронная почта или логин", \
        [Required(message=MSG_REQUIRED)], \
        filters = [lambda x : (x or '')])

    def validate_email_or_login(form, field):
        matcher = re.compile("^" + re.escape(field.data) + "$", re.IGNORECASE)
        user = db.users.find_one({'$or': [{'email': {'$regex' : matcher}},{'login': {'$regex' : matcher}}]})
        if not user:
            raise ValidationError(u"Электронная почта или логин '%s' не найдены" % field.data)
        else:
            field.user = user

class DogSearch(Form):

    #TODO: показывать только те породы, по которым есть объявления
    breed = PTextField(u'Порода',  
        default = u"")

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) 
        for gender_id, gender_name in genders.genders.items()])


    city = PTextField(u"Местоположение",  
        default = u"")

    distance = IntegerField(u"удаленность", default = 150)

    photo = BooleanField(u"с фото")
    video = BooleanField(u"с видео")
    champion_bloodlines = BooleanField(u"чемпионских кровей")
    delivery = BooleanField(u"из других городов с дотавкой")
    contract = BooleanField(u"с договором")
    pedigree = BooleanField(u"c родословной")

    # price
    price_from = PTextField(u"Цена от", \
        filters = [lambda x: (x or '').replace(' ', '')]
        )
    price_to = PTextField(u"Цена до", \
        filters = [lambda x: (x or '').replace(' ', '')])

    price_unit = SelectField(u"", choices = [(0, u"руб"), (1, u"тыс руб")])

    sort = SelectField(Markup(u"сортировать по"), choices = [(1, Markup(u"дороже")), (2, Markup(u"дешевле")), (3, u"дате"), (4, u"привлекательности и дате")], coerce = int)

    page = IntegerField(u"Страница", default = 1)

    perpage = SelectField(u"Объявлений на стр.", default = 15, coerce=int, choices = [(1, 10), (2, 20), (3, 30), (4, 50), (5, 100)])


class SaleSearch(Form):

    #TODO: показывать только те породы, по которым есть объявления
    breed = PTextField(u'Порода')

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) for 
        gender_id, gender_name in genders.genders.items()])


    city = PTextField(u"Местоположение")

    distance = IntegerField(u"Удаленность, км", default = 150)

    photo = BooleanField(u"Только с фото")

    # price
    price_from = IntegerField(u"Цена, тыс руб", default = 0)
    price_to = IntegerField(u"Цена до", default = 100)

    sort = SelectField(u"Сортировка", choices = [(1, u"Дороже"), (2, u"Дешевле"), (3, u"По дате")], coerce = int)

    page = IntegerField(u"Страница", default = 1)

    perpage = SelectField(u"Объявлений на стр.", default = 15, coerce=int, choices = [(1, 10), (2, 20), (3, 30), (4, 50), (5, 100)])

class Profile(Form):
    username = PTextField(u"Имя", validators = [Required(message=MSG_REQUIRED) ])

    surname = PTextField(u"Фамилия")

    city = PTextField(u"Город", validators = [validate_location], 
        db_name = 'city_id', \
        db_in = lambda f: f.city_id, \
        db_out = lambda v : geo.get_city_region(v))
    
    phone = PTextField(u"Телефонный номер")
    
    skype = PTextField(u"Skype")

    site_link = PTextField(Markup(u"Порсональный <span style='white-space:nowrap'>веб-сайт</span>"))
    # kennel_name = PTextField(u"Название питомника")
    

class Cat(Form):

    breed = TextField(u'Порода', \
        validators = [Required(message=MSG_REQUIRED), validate_breed]) 

    gender = SelectField(u"Пол", \
        choices = [(u"", u"")] + [ (str(gender_id), gender_name) for gender_id, gender_name in genders.genders.items()])
   
    title = TextField(u"Заголовок объявления", [Required(message=MSG_REQUIRED), Length(min=10, max=80, message=MSG_RANGE_LENGTH.format(10, 80))], \
         description = u"Не более 80 символов."
         )

    desc = TextAreaField(u"Подробное описание", [Required(message=MSG_REQUIRED), Length(min=100, message=MSG_MIN_LENGTH.format(100))], \
        description = u"Не менее 100 символов."
    )

    photos = HiddenField(u"Имена фалов, загруженных при помощи plupload")

    price = IntegerField(u"Цена (руб)", [Required(message=MSG_REQUIRED), NumberRange(min=10, max=900000, message=MSG_RANGE.format(10, 900000))], \
        description = Markup(u'Указывая реальную цену, покупатели проявят больше интереса к вашему объявлению!'))

    city = PTextField(u"Местоположение", [Required(message=MSG_REQUIRED), validate_location], \
        description = u"Введите населенный пункт, в котором продается питомец.")

    phone = PTextField(u"Телефонный номер")
    skype = PTextField(u"Skype")

    email = PTextField(u"Электронная почта / Email")
    username = PTextField(u"Имя")

class Dog(Form):

    # breed = SelectField(u'Порода', \
    #     choices = [(0, u"")] + [ (dog_id, dog_name) for (dog_id, dog_name) in dogs.items()], \
    #     coerce = int, 
    #     validators = [Required(message=MSG_REQUIRED)])


    breed = PTextField(u'Порода', \
        validators = [Required(message=MSG_REQUIRED), validate_breed], \
        db_name = 'breed_id', \
        db_in = lambda f: f.breed_id, \
        db_out = lambda v: breeds.get_breed_dog_name(v)) 

    gender = PSelectField(u"Пол", \
        choices = [(0, u'-- не указан --')] + [ (gender_id, gender_name) \
        for gender_id, gender_name in genders.genders.items()], \
        coerce=int, \
        attraction = True, \
        db_name = 'gender_id', \
        db_out = lambda v: num(v))
   
    title = PTextField(Markup(u"Заголовок<br/>объявления"), \
        validators = [Required(message=MSG_REQUIRED), Length(min=10, max=80, message=MSG_RANGE_LENGTH.format(10, 80))], \
         description = Markup(u"От 10 до 80 символов, осталось <span id='title_count' class='text-danger'>80</span>."), \
         db_name = 'title')

    desc = PTextAreaField(u"Текст рекламного объявления", \
        validators = [Required(message=MSG_REQUIRED), Length(max=1100, message=MSG_MAX_LENGTH.format(1000))], \
        description = Markup(u"Не более 1000 символов, осталось <span class='text-danger' id='desc_count'>1000</span>."))

    photos = PHiddenField(u"Имена фалов, загруженных при помощи plupload", \
        attraction = True, \
        db_in = lambda f: f.photonames, 
        db_out = lambda v: ",".join(v or []))

    video_link = PTextField(u"Ссылка на видео", \
        attraction = True, \
        description = Markup(u"Принимаются ссылки на видео только с <a target='_blank' href='http://youtube.com'>youtube.com</a>.")
        )

    price = PIntegerField(u"Цена", \
        validators = [Required(message=MSG_REQUIRED), \
         NumberRange(min=5000, max=300000, \
            message=MSG_RANGE.format(5000, 300000))], \
        # filters = [lambda x: x.replace(' ','')], \
        description = Markup(u'От 5&nbsp;000 до 300&nbsp;000 руб. Объявление с нереальной ценой будет <span style="color:red">удалено!</span>'),\
        db_out = lambda v: num(v))

    price_haggle = PBooleanField(u"Возможен торг") #Торг

    price_hp =  PBooleanField(u"Рассрочка") #рассрочка hire purchase

    city = PTextField(u"Местоположение", \
        validators = [Required(message=MSG_REQUIRED), validate_location], \
        description = u"", \
        db_name = 'city_id', \
        db_in = lambda f: f.city_id, \
        db_out = lambda v : geo.get_city_region(v))

    
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

    puppy_card_kennel = PTextAreaField(Markup(u"<small>Наименование, адрес и телефон питомника, выдавшего метрику</small>"), \
        attraction = True, \
        attraction_depends = {"id":"doc", "values": doc_puppy_cards.keys()},
        depends = {"id":"doc", "values": doc_puppy_cards.keys()})

    champion_bloodlines = PBooleanField(Markup(u"<small>Чемпионские крови</small>"), 
        depends = {"id":"doc"})
    
    father_name = PTextField(Markup(u"<small>Кличка</small>"), \
        attraction = True, \
        depends = {"id":"doc"})

    father_country = PSelectField(Markup(u"<small>Страна рождения</small>"), \
        choices = [(0, u"-- не указана --")] + geo.get_countries_for_dog_adv(), \
        coerce = int, \
        attraction = True, \
        depends = {"id":"doc"}, \
        db_name = 'father_country_id')

    father_pedigree_link = PTextField(Markup(u"<small>Ссылка на страницу с родословной</small>"), \
        description = Markup(u"Например, <a target='_blank' href='http://www.shiba-pedigree.ru/details.php?id=65529'>http://www.shiba-pedigree.ru/details.php?id=65529</a>"), 
        attraction = True, \
        depends = {"id": "doc"})

    father_misc = PTextAreaField(Markup(u"<small>Награды, титулы, оценки, тесты и прочее</small>"), 
        attraction = True,
        depends = {"id":"doc"}
        )

    father_color = PTextField(Markup(u"<small>Окрас</small>"), \
        attraction = True, \
        depends = {"id": "doc"})

    mother_name = PTextField(Markup(u"<small>Кличка</small>"), \
        attraction = True,\
        depends = {"id":"doc"})

    mother_country = PSelectField(Markup(u"<small>Страна рождения</small>"), \
        choices = [(0, u"-- не указана --")] + geo.get_countries_for_dog_adv(), \
        coerce = int, \
        attraction = True,\
        depends = {"id":"doc"}, \
        db_name = 'mother_country_id')

    mother_misc = PTextAreaField(Markup(u"<small>Награды, титулы, оценки, тесты и прочее</small>"), 
        attraction = True,
        depends = {"id":"doc"})

    mother_pedigree_link = PTextField(Markup(u"<small>Ссылка на страницу с родословной</small>"), \
        description = Markup(u"Например, <a target='_blank' href='http://www.pedigreedatabase.com/german_shepherd_dog/dog.html?id=2159170'>http://www.pedigreedatabase.com/german_shepherd_dog/dog.html?id=2159170</a>"), 
        attraction = True, \
        depends = {"id": "doc"})

    mother_color = PTextField(Markup(u"<small>Окрас</small>"), \
        attraction = True, \
        depends = {"id": "doc"})

    birthday = PTextField(Markup(u"Дата рождения"), \
        description = u"Дата в формате день/месяц/год, например, 24/02/2014", \
        attraction = True, \
        db_in = lambda f: str2date(f.data), \
        db_out = lambda v : date2str(v, "%d%m%Y") )
    

    vaccination = PBooleanField(u"Вакцинация (прививки) по возрасту", \
        attraction = True)

    vetpassport = PBooleanField(u"Ветеринарный паспорт", \
        attraction = True)

    microchip = PBooleanField(u"Микрочип", 
        attraction = True)

    breeding = PBooleanField(Markup(u"<small>Допуск в разведение</small>"), \
        depends = {"id":"doc", "values": doc_dog_pedigrees_rkf.keys()})


    show = PBooleanField(Markup(u"<small>Подходит для выставок</small>"))

    phone = PTextField(u"Телефонный номер")

    skype = PTextField(u"Skype")

    kennel_name = PTextField(u"Название питомника", 
        attraction = True)

    site_link = PTextField(Markup(u"Персональный<br/><span style='white-space:nowrap'>веб-сайт</span>"), \
        attraction = True)

    username = PTextField(u"Контактное лицо", \
        validators = [Required(message=MSG_REQUIRED)])

class Activate(Form): 

    email = TextField(u"Электронная почта", \
        [Required(message=MSG_REQUIRED), Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()])

    def validate_email(form, field):
        print("validate confirm  email %s" % field.data)
        if not db.users.find_one({'email': field.data}):
            raise ValidationError(u"Адрес '%s' не зарегистрирован" % field.data)

class SignIn(Form):

    login = PTextField(u"Электронная почта или логин", \
        [Required(message=MSG_REQUIRED)])

    remember = BooleanField(u"Запомнить меня", default = True)

    password = PasswordField(u'Пароль', \
        [Required(message=MSG_REQUIRED)])

class SignUpBasic(Form):
    username = PTextField(u"Ваше имя", \
        [Required(message=MSG_REQUIRED)], description = u"Увидят другие пользователи.")

    email = PTextField(u'Электронная почта', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)], \
    filters = [lambda x : (x or '').lower()], \
        description = u"")

    def validate_email(form, field):
        user = db.users.find_one({'email': field.data})
        check = config.DOMAIN_NAME_CHECK and config.DOMAIN_NAME in field.data
        if check or user:
            raise ValidationError(u"Адрес '%s' занят" % field.data)

    password = PasswordField(u"Пароль", \
        [Required(message=MSG_REQUIRED), \
        Length(min=6, max=36, message=MSG_RANGE_LENGTH.format(6, 36))], description=u"Введите надежный пароль от 6 до 36 символов.")

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
        user = db.users.find_one({'email': field.data})
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
    username = PTextField(u"Ваше имя", \
        validators = [Required(message=MSG_REQUIRED)])

    message = PTextAreaField(u"Сообщение", \
        validators = [Required(message=MSG_REQUIRED)])

    email = PTextField(u'Ваша электронная почта', \
        validators = [Required(message=MSG_REQUIRED),\
        Email(message=MSG_EMAIL)], \
        filters = [lambda x : (x or '').lower()])

    sms_alert = BooleanField(Markup(u"Отправить автору <abbr title='Получатель письма получет короткое sms-оповещение о новом электронном письме.'>sms-оповещение</abbr> (<i>бесплатно</i>)"))

class AdminNews(PForm):
    subject = PTextField(u"Заголовок", 
        validators = [Required(message=MSG_REQUIRED)])

    summary = PTextAreaField(u"Краткое описание", 
        validators = [Required(MSG_REQUIRED)])

    message = PTextAreaField(u"Новость", 
        validators = [Required(message=MSG_REQUIRED)])

    published = PBooleanField(u"Показать новость на сайте")

    email_single = PTextField(u"Отправить на эл. адрес", validators = [validators.Optional(), Email(message=MSG_EMAIL)], 
        filters = [lambda x : (x or '').lower()])

    email_everyone = PBooleanField(u"Отправить всем пользователям")

    publish_date = PDateTimeField(u'Дата публикации', 
        format='%Y-%m-%d %H:%M:%S')

class Comment(PForm):
    levels = PHiddenField(u"path", 
        filters = [lambda x: [int(level) for level in 
        (x or "").strip("_").split("_") if level]  ])

    text = PTextAreaField(u"Ваш комментарий", 
        validators = [Required(MSG_REQUIRED)])

