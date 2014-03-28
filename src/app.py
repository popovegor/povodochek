#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, flash, redirect, url_for, session, send_from_directory, send_file, abort, jsonify, Markup, make_response)
from flask_login import (LoginManager, current_user,
                            login_user, logout_user, login_required, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

from wtforms import (Form, BooleanField, TextField, PasswordField, validators)
from forms import (SignUp, SignIn, Cat, Contact, \
    Activate,ResetPassword, ChangePassword, \
    SaleSearch, get_city_by_city_field, \
    SendMail, ChangeEmail, SignUpBasic, \
    get_breed_by_form_field, Dog, DogSearch)
from werkzeug.datastructures import MultiDict, ImmutableMultiDict

from werkzeug.utils import secure_filename
import os
from uuid import uuid4, uuid1
from datetime import datetime, date, timedelta
import time
import re
import base64
from sys import maxint
from itertools import groupby
from bson.objectid import ObjectId

from flaskext.uploads import (UploadSet, configure_uploads, IMAGES,
                              UploadNotAllowed)

from security import hash_password, check_password

from flask_mail import (Mail, Message)
from threading import Thread
from momentjs import MomentJS
from photo_helper import (create_thumbnail, get_thumbnail_filename, resize_image, get_photo_size)
from helpers import (num, qoute_rus, morph_word, date2str)

from smsgate import send_sms

from dic.ages import ages
from dic.genders import genders
from dic.pets import (pets, get_pet_name, DOG_ID, CAT_ID)
from dic.breeds import (dogs, get_breed_name, cats, \
    get_breed_by_name, breeds, get_breed_dog_name, \
    get_breed_cat_name)
from dic.cities import (get_city_region, get_city, get_city_name, format_city_region, cities)
from dic.pet_docs import (doc_dog_pedigrees, doc_puppy_cards, \
    dog_docs, get_doc_dog_name)

from dic.countries import (get_country_name)

from flaskext.markdown import Markdown
from flask.ext.assets import Environment, Bundle
from advs_parser import parse_avito_adv
import db
             

import random
import json
from form_helper import (get_fields, calc_attraction)

photos = UploadSet('photos', IMAGES)

class User(UserMixin):
    def __init__(self, login, id, active = True, username = None, email = None, new_email = None, city_id = None, phone = None, skype = None):
        self.name = login
        self.username = username
        self.id = id
        self.active = active
        self.email = email
        self.new_email = new_email
        self.city_id = city_id
        self.phone = phone
        self.skype = skype

    def is_signed(self):
        return True

    def is_active(self):
        return True

class Anonymous(AnonymousUser):
    def __init__(self):
        self.name = u"Anonymous"
        self.username = u""
        self.email = u""

    def is_signed(self):
        return False

app = Flask(__name__)

config = os.path.join(app.root_path, 'config.py')
app.config.from_pyfile(config)

mail = Mail(app)

Markdown(app)
assets = Environment(app)

js = Bundle('js/jquery-1.11.0.min.js', \
    'js/jquery-ui-1.10.3.custom.min.js', \
    'js/chosen.jquery.js', \
    'js/jquery.validate.min.js', \
    'js/jquery.validate.ru.js', \
    'js/jquery.inputmask.bundle.min.js', \
    'js/moment.min.js', \
    'js/moment.min.ru.js', \
    'js/jquery.nouislider.min.js', \
    'js/jquery.flexslider.min.js', \
    'js/jquery.touch-punch.min.js', \
    'js/jquery.shapeshift.js', \
    'js/jquery.mosaicflow.min.js', \
    'js/bootstrap3-typeahead.min.js', \
    'js/holder.js', \
    'js/bootstrap.min.js', \
    'js/jquery.carouFredSel.min.js', \
    'js/povodochek.js', \
    'js/jquery.simplyCountable.js', \
    filters='rjsmin', \
    output='gen/js.js')
assets.register('js_all', js)

css = Bundle(
    'css/bootstrap.min.css', \
    'css/typeahead.js-bootstrap.css', \
    'css/nouislider.fox.css', \
    'css/rur-arial.css', \
    'css/flexslider.css', \
    'http://fonts.googleapis.com/css?family=Russo+One&subset=cyrillic', \
    filters = 'cssmin', \
    output = 'gen/css.css')
assets.register('css_all', css)

configure_uploads(app, (photos))

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "/signin/"
login_manager.login_message = u"Пожалуйста, войдите, чтобы уидеть содержимое страницы."
login_manager.refresh_view = "reauth"

login_manager.setup_app(app)

# jinja custom filters and globals

app.jinja_env.globals['momentjs'] = MomentJS

app.jinja_env.filters['json'] = json.dumps

def jinja_format_datetime(value, format='%H:%M, %d.%m.%y'):
    return value.strftime(format) if value  else ""

app.jinja_env.filters['format_datetime'] = jinja_format_datetime

def jinja_date(value):
    return datetime.date(value) if value else ""

app.jinja_env.filters['date'] = jinja_date

def jinja_format_price(value, template=u"{0:,}"):
    return Markup((template.format(value) if value else u"").replace(u",", u"&nbsp;"))

app.jinja_env.filters['format_price'] = jinja_format_price

def jinja_format(template=u"{0}", *args):
    return template.format(*args)

app.jinja_env.globals['format'] = jinja_format

app.jinja_env.filters['pet_name'] = get_pet_name

app.jinja_env.filters['breed_name'] = get_breed_name

app.jinja_env.filters['breed_dog_name'] = get_breed_dog_name
app.jinja_env.filters['breed_cat_name'] = get_breed_cat_name

def jinja_sorted(iterable, key = None, reverse = False):
    return sorted(iterable, key = eval(key), reverse = reverse) 

app.jinja_env.filters['sorted'] = jinja_sorted

# todo: add caching layer 
def get_gender_name(gender_id):
    id = num(gender_id)
    return genders[id] if id in genders else u""

app.jinja_env.filters['gender_name'] = get_gender_name

# todo: add caching layer 
def get_age_name(age_id):
    id = num(age_id)
    return ages[id] if id in ages else u""

app.jinja_env.filters['age_name'] = get_age_name
app.jinja_env.filters['city_region'] = get_city_region
app.jinja_env.filters['city_name'] = get_city_name
app.jinja_env.filters['morph_word'] = morph_word

def change_query(url, param, old, new):
    if url and param and old and new:
        param_value = "{0}={1}".format(param, old)
        url_non_param = url.replace("&" + param_value, "").replace(param_value, "")
        return "{0}{1}&{2}={3}".format(url_non_param, "?" if "?" not in url_non_param else "", param, new)
    return url

app.jinja_env.filters['change_query'] = change_query

def jinja_max(*args):
    return max(*args)

app.jinja_env.filters['max'] = jinja_max

def jinja_min(*args):
    return min(*args)

app.jinja_env.filters['min'] = jinja_min



def jinja_utcnow():
    return datetime.utcnow()

app.jinja_env.globals['utcnow'] = jinja_utcnow

app.jinja_env.globals['dog_docs'] = dog_docs
app.jinja_env.filters['doc_dog_name'] = get_doc_dog_name
app.jinja_env.globals['doc_puppy_cards'] = doc_puppy_cards
app.jinja_env.globals['doc_dog_pedigrees'] = doc_dog_pedigrees


def debug_write(msg):
    print("DEBUG INFO: %s" % msg)


def jinja_breeds():
	return [ breed for breed in breeds.values() ]

app.jinja_env.globals['breeds'] = jinja_breeds()

def jinja_dogs():
    return [ dog for dog in dogs.values() ]

app.jinja_env.globals['dogs'] = jinja_dogs()

def jinja_large_cities():
    dt1 = datetime.now()
    large_cities = [city for city in cities.values() if city.get('city_size') >= 5]
    dt2 = datetime.now()
    print(dt2 - dt1)
    return large_cities

app.jinja_env.globals['large_cities'] = jinja_large_cities()

app.jinja_env.filters['country_name'] = get_country_name


@login_manager.user_loader
def load_user(id):
    # print("user id = %s" % str(id))
    user = db.get_user(id)
    if user:
        return User(user.get('login'), user.get("_id"), active = user.get("activated"), username = user.get("username"), email = user.get("email"), new_email = user.get("new_email"), city_id = user.get("city_id"), phone= user.get("phone"), skype = user.get("skype") )
    else:
        return Anonymous()

@app.route("/")
def index():
    mosaic_advs = get_pet_advs_for_mosaic(0, 10, pet_id = DOG_ID)
    dog_advs = db.get_top_dog_advs()
    cat_advs = db.get_top_cat_advs()
    tmpl = render_template('index1.html', \
        pet_search_form = SaleSearch(), \
        top_cats = cat_advs, \
        top_dogs = dog_advs, \
        mosaic_advs = mosaic_advs, \
        title = u"Продажа и покупка породистых собак и кошек по всей России")
    return tmpl

@app.route("/signin/", methods = ["POST", "GET"])
def signin():
    form = SignIn(request.form)
    if request.method == "POST" and form.validate():
        (login, password, remember) = (form.login.data, form.password.data, form.remember.data)
        user = db.get_user_by_login(login)
        if user and check_password(user.get("pwd_hash"), password):
            if True or user.get("activated"):
                if login_user(User(login, user["_id"]), remember=remember):
                    return redirect(request.args.get("next") \
                        or url_for("account_contact"))
                else:
                    flash(u"Извините, но вы не можете войти.", "error")
            else:
                print('disactivated')
                flash(Markup(u"Вы не можете войти на сайт, так как регистрация не подтверждена. Проверьте, пожалуйста, электронную почту или отправьте <a target='_blank' href='{0}'>ссылку на активацию</a> повторно.".format(url_for('activate', confirm=''))), "error")
        else:
            flash(u"Неправильный логин или пароль.", "error")
    return render_template("signin.html", form=form, title=u"Вход")

@app.route("/ajax/activate/remember/later/")
@login_required
def ajax_activate_remember_later():
    later = session["activate_remember_later"] = True
    return "success"

@app.route("/ajax/typeahead/location/", methods = ["GET"])
def ajax_typeahead_location():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    locations = db.get_locations_for_typeahead(query, limit)
    return jsonify(items = locations )    

@app.route("/ajax/typeahead/breed/", defaults={'pet_id':None}, methods = ["GET"])
@app.route("/ajax/typeahead/breed/<int:pet_id>/", methods = ["GET"])
def ajax_typeahead_breed(pet_id = None):
    # print(str(request.args.get("query")))
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    matcher = query.lower()
    breeds = []
    _dogs = _cats = []    
    if not pet_id or pet_id == DOG_ID:
        _dogs = [u"{0}{1}".format(dog, u", Собаки") \
        for dog in dogs.values() if matcher in dog.lower() ] 
    if not pet_id or pet_id == CAT_ID:
        _cats = [u"{0}{1}".format(cat, u", Кошки") \
        for cat in cats.values() if matcher in cat.lower() ]
        _cats = sorted(_cats)

    if not matcher:
        breeds = _dogs[:limit/2] + _cats[:limit/2]
    else:
        breeds = _dogs[:limit/2] + _cats[:limit/2]
    return jsonify(items = breeds )  

@app.route("/ajax/typeahead/dog/", methods = ["GET"])
def ajax_typeahead_dog():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    matcher = query.lower()

    if matcher:
        breeds = [dog for dog in dogs.values() if matcher in dog.lower() ]
    else:
        breeds = dogs.values()[:limit]
    return jsonify(items = breeds ) 


@app.route("/ajax/typeahead/cat/", methods = ["GET"])
def ajax_typeahead_cat():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    matcher = query.lower()

    if matcher:
        breeds = [cat for cat in cats.values() \
        if matcher in cat.lower() ]
    else:
        breeds = cats.values()[:limit]
    return jsonify(items = breeds ) 


@app.route("/test/location/", methods = ["GET"])
def test_location():
    return render_template("test/location.html", title=u"Location")

@app.route("/test/email/stuff/")
def test_email_stuff():
    msg = Message("Hello", recipients=["popovegor@gmail.com"])
    mail.send(msg)
    return "Stuff email!"


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper

@async
def send_msg_aync(mailer, msg):
    mailer.send(msg)

def send_activate(email, confirm):
    msg = Message("Подтверждение регистрации на сайте Поводочек", recipients = [email])
    msg.html = render_template("email/activate.html", confirm = confirm)
    mail.send(msg)

def send_confirm_email(email):
    msg = Message("Подтверждение изменения почтового адреса на сайте Поводочек", recipients = [email])
    msg.html = render_template("email/confirm_email.html", base64_email = base64.b64encode(email))
    mail.send(msg)

def send_signup(username, login, email, password, confirm):
    msg = Message(u"Регистрация на сайте Поводочек", recipients=[email])
    msg.html = render_template("email/signup.html", username=username, login = login, email = email, password = password, confirm = confirm)
    mail.send(msg)

def send_reset_password(email, login, asign, password):
    msg = Message(u"Сброс пароля для сайта Поводочек", recipients=[email])
    msg.html = render_template("email/reset_password.html", login = login, password = password, asign = asign)
    mail.send(msg)

def send_from_sale(adv_id, adv_url, email, username, \
    seller_email, seller_username, subject, message):
    # adv = sales().find_one(ObjectId(sale_id))
    if adv_id and seller_email:
        msg = Message(subject, recipients=[seller_email])
        msg.html = render_template("email/from_adv.html", \
            subject = subject, \
            message = message, \
            adv_url = adv_url, \
            adv_id = adv_id, \
            seller_email = seller_email, \
            seller_username = seller_username, \
            email = email, \
            username = username, \
            date = datetime.now())
        mail.send(msg)

    
@app.route("/test/email/from_dog_adv/")
def test_email_from_dog_adv():
    msg = Message(u"Сообщение от %s сайта Поводочек" % (u'пользователя' if current_user.is_signed() else u'гостя'), \
        recipients=["popovegor@gmail.com"])
    adv = db.dog_advs.find(limit=1)[0]
    msg.html = render_template("email/from_adv.html", \
        subject = u"Сообщение от пользователя сайта Поводочек", \
        message = u"Некоторое тестовое сообщение.", \
        adv = adv, \
        username = u'Егор Попов АТИ', \
        email = u'popovegor@gmail.com', \
        seller = db.get_user(adv.get('user_id')), \
        date = datetime.now())
    # mail.send(msg)
    return msg.html

@app.route("/activate/", defaults={'confirm': None}, methods=["GET", "POST"])
@app.route("/activate/<confirm>/", methods = ["GET", "POST"])
def activate(confirm):
    form = Activate(request.form)

    if current_user.is_signed and current_user.active:
        return render_template("activate_success.html", user = current_user, title = u"Активация регистрации")

    if request.method == "POST":
        if form.validate():
            email = form.email.data
            user = db.get_user_by_email(email)
            if user:
                new_confirm = db.set_user_confirm(user['_id'])
                send_activate(email, new_confirm)
            return render_template("activate_sent.html", form = form, title = u"Активация регистрации", email = email)
        else:
            return render_template("activate.html", form = form, title = u"Активация регистрации",)
    else:
        
        if confirm:
            user = db.get_user_by_confirm(confirm)
            if user:
                db.activate_user(user['_id'])
                return render_template("activate_success.html", user = user, title = u"Активация регистрации")
            else:
                return render_template("activate.html", confirm = confirm, form = form, title = u"Активация регистрации")
        else:
            return render_template("activate.html", form = form, title = u"Активация регистрации")
        


@app.route("/asignin/<asign>/", methods = ["GET"])
def asignin(asign):
    user = db.get_user_by_asign(asign)
    title=u"Активация нового пароля"
    if user:
        db.asign_user(user)
        if login_user(User(user.get("login"), user.get("_id"))):
            return render_template("asignin_success.html", title = title)
    return render_template("asignin_failed.html", title=title)

@app.route("/account/change-password/", methods = ["GET", "POST"])
@login_required
def account_change_password():
    form = ChangePassword(request.form)
    form.current_user = current_user
    if request.method == "POST" and form.validate():
        db.change_user_password(current_user.id, \
            hash_password(form.new_password.data))
        flash(u"Пароль успешно изменен", "success")
    return render_template("account/change_password.html", title=u"Смена пароля", form = form)


@app.route("/account/confirm-email/<base64_email>/")
@login_required
def account_confirm_email(base64_email):
    new_email = base64.b64decode(base64_email)
    if new_email and current_user.new_email == new_email:
        db.confirm_user_email(current_user.id, new_email)
        flash(u"Новый почтовый адрес подтвержден.", "success")
    else:
        flash(u"Новый почтовый адрес не удалось подтвердить!", "error")
    return redirect(url_for('account_change_email'))


@app.route("/account/change-email/", methods = ["GET", "POST"])
@login_required
def account_change_email():
    form = ChangeEmail(request.form)
    form.current_user = current_user
    if request.method == "POST" and form.validate():
        db.change_user_email(current_user.id, form.new_email.data)
        send_confirm_email(form.new_email.data)
        flash(u"Для завершения изменения почтового адреса, необходимо перейти по ссылке, высланной письмом на новый почтовый адрес.", "warning")
    return render_template("account/change_email.html", title=u"Смена электронной почты", form = form)

@app.route("/test/email/signup/")
def test_email_signup():
    msg = Message("Регистрация на сайте Поводочек", recipients=["popovegor@gmail.com"])
    msg.html = render_template("email/signup.html", username=u"Егор", login = 'popovegor', password = u"sdfhk434988", email = u"popovegor@gmail.com", confirm=u"nab4eae954386beb2955e49c1ad50a51e")
    # mail.send(msg)
    return msg.html

@app.route("/test/email/reset-password/")
def test_email_reset_password():
    return render_template("email/reset_password.html", password = u"sdfhk434988", login = u"popovegor", asign=u"nab4eae954386beb2955e49c1ad50a51e")

@app.route("/test/email/activate/")
def test_email_activate():
    return render_template("email/activate.html", confirm = "1")


@app.route("/signup/", methods = ["POST", "GET"])
def signup_basic():
    form = SignUpBasic(request.form)
    if request.method == "POST" and form.validate():
        (login, email, password, confirm, username) = (form.login.data, form.email.data, form.password.data, str(uuid4()), "Пользователь")
        user_id = db.signup_user(login, email, \
            hash_password(password), username, confirm)
        send_signup(username, login, email, password, confirm)
        flash(u"Для того чтобы подтвердить регистрацию, перейдите по ссылке в отправленном Вам письме.", "info")
        if login_user(User(login, user_id), remember = True):
            return redirect(request.args.get('next') or url_for('account_contact'))
        else:
            return redirect(url_for('signin'))
    return render_template('signup_basic.html', form=form, title=u"Регистрация")

@app.route("/reset-password/", methods = ["GET", "POST"])
def reset_password():
    form = ResetPassword(request.form)
    title = u"Сброс пароля"
    if request.method == "POST" and form.validate():
        password = str(hash(str(uuid1())) % 10000000)
        asign = str(uuid4())
        user = db.reset_user_password(form.email_or_login.user, \
            hash_password(password), asign)
        if user:
            send_reset_password(user.get('email'), user.get("login"), asign, password)
            return render_template("reset_password_sent.html", title=title, email = user.get('email'))
    return render_template("reset_password.html", title=title, form = form)

@app.route("/signout/")
@login_required
def signout():
    logout_user()
    url = request.args.get("url")
    return redirect( url if url else url_for('index'))


def sale_find_header(form, pet_id, breed_id):
    # generate title
    header = u"Купить <span>(продают)</span> <span class='bg-warning'>{0}</span>{1}{2}"
    title = u"Купить {0}{1}{3}: Продажа {2}{1}{3}"
    pet = u"собаку или кошку"

    if pet_id == DOG_ID:
        pet = u"собаку"
    elif pet_id == CAT_ID:
        pet = u"кошку"

    breed = get_breed_name(breed_id, pet_id)
    breed_header = breed
    breed_title = breed
    if breed:
        # breed = u" {0}".format(morph_word(breed, {"gent"}).lower())
        breed_header = Markup(u" породы <span class='bg-warning'>%s</span>" % breed.lower() )
        breed_title = Markup(u" породы {0}".format(breed.lower()))

    city = get_city_name(form.city.city_id, "i") if form.city.city_id else u''
    city_header = city
    city_title = city
    if city:
        city_header = u" в г. <span class='bg-warning'>{0}</span>".format(city)
        city_title = u" в г. {0}".format(city)
        # if form.distance.data:
            # city = u"{0}(+ {1} км)".format(city, form.distance.data) 
    # else:
    #     city_header = u" в России"
    #     city_title = u" в России"

    return (header.format(pet, breed_header, city_header), \
        title.format(pet, breed_title, morph_word(pet, {"gent", "plur"}), city_title), pet, breed) 

@app.route("/prodazha-sobak/")
def dog_search():
    form = DogSearch(request.args)
    city = get_city_by_city_field(form.city)
    (form.city.data, form.city.city_id) = \
        (format_city_region(city), city.get("city_id")) if city else (None, None)
    (breed_id, pet_id) = get_breed_by_form_field(form.breed)
    if breed_id and pet_id:
        form.breed.data = get_breed_name(breed_id, pet_id)
    pet_id = DOG_ID
    # sort
    session["dog_sort"] = form.sort.data or \
        session.get("dog_sort") or 4

    (advs, count, total) = db.find_dog_advs(
        breed_id = breed_id, \
        gender_id = form.gender.data, \
        city = city, \
        distance = (form.distance.data + 0.01) if form.distance.data else None, \
        photo = form.photo.data, \
        price_from = form.price_from.data if form.price_from.data else None, \
        price_to = form.price_to.data if form.price_to.data else None, \
        sort = session.get("dog_sort"),
        skip = (form.page.data - 1) * form.perpage.data, \
        limit = form.perpage.data
        )

    (header, title, pet_name, breed_name) = sale_find_header(form, pet_id, breed_id)

    tmpl = render_template("dog/search.html", header=Markup(header), \
      title=title, form = form, advs = advs, \
      pet = pet_name, pet_id = pet_id, \
      breed = breed_name, breed_id = breed_id, \
      sort = session.get("dog_sort"), \
      count = count, total = total )
    return tmpl


@app.route("/prodazha-koshek/")
def cat_search(sale_search_form = None):
    form = sale_search_form or SaleSearch(request.args)
    city = get_city_by_city_field(form.city)
    (form.city.data, form.city.city_id) = \
        (format_city_region(city), city.get("city_id")) if city else (None, None)
    (breed_id, pet_id) = get_breed_by_form_field(form.breed)
    if breed_id and pet_id:
    	form.breed.data = get_breed_name(breed_id, pet_id)
    pet_id = CAT_ID
    # sort
    session["cat_sort"] = form.sort.data or session.get("cat_sort") or 3
    
    (advs, count, total) = db.find_cat_advs(pet_id = pet_id, \
        breed_id = breed_id, \
        gender_id = form.gender.data, \
        city = city, \
        distance = form.distance.data + 0.01, \
        photo = form.photo.data, \
        price_from = form.price_from.data  * 1000, \
        price_to = (form.price_to.data if num(form.price_to.data) < 100 else 0) * 1000, \
        sort = session.get("cat_sort"),
        skip = (form.page.data - 1) * form.perpage.data, \
        limit = form.perpage.data
        )

    (header, title, pet_name, breed_name) = sale_find_header(form, pet_id, breed_id)

    tmpl = render_template("cat/search.html", header=Markup(header), \
      title=title, form = form, advs = advs, \
      pet = pet_name, pet_id = pet_id, \
      breed = breed_name, breed_id = breed_id, \
      sort = session.get("cat_sort"), \
      count = count, total = total )
    return tmpl


@app.route('/prodazha-sobak/<adv_id>/')
def dog_adv_show(adv_id):
    adv = db.get_dog_adv(adv_id)
    if not adv:
        abort(404)

    name = u"Продам собаку породы {0} в г. {1}".format( \
        get_breed_dog_name(adv.get("breed_id")).lower(),\
        get_city_name(adv.get("city_id"), "i"))

    header = \
    Markup(u"Продам собаку породы {0} в г.&nbsp;{1}".format( \
        get_breed_dog_name(adv.get("breed_id")).lower(),\
        get_city_name(adv.get("city_id"), "i")
    ))
    title = u"{0} за {1}".format(name, \
        u"{0} {1}".format(u"{0:,}".format(adv.get("price")).replace(","," "), morph_word(u"рубль", count=adv.get("price"))))
    seller = db.get_user(adv.get("user_id"))
    return render_template("dog/adv_show.html", \
        header = header,
        title = title,
        adv = adv,
        seller = seller)


@app.route('/prodazha-koshek/<adv_id>/')
def cat_adv_show(adv_id):
    adv = None
    try:
        adv = db.get_cat_adv(adv_id)
    except Exception, e:
        print(e)
    
    if not adv:
        abort(404)

    name = u"Продам {0} породы {1} в г. {2}".format( \
        morph_word(get_pet_name(adv.get("pet_id")), {"accs"}).lower(), \
        get_breed_name(adv.get("breed_id"), adv.get("pet_id")).lower(),\
        get_city_name(adv.get("city_id"), "i")
    )
    header = Markup(u"Продам {0} породы {1} в г.&nbsp;{2}".format( \
        morph_word(get_pet_name(adv.get("pet_id")), {"accs"}).lower(), \
        get_breed_name(adv.get("breed_id"), adv.get("pet_id")).lower(),\
        get_city_name(adv.get("city_id"), "i")
    ))
    title = u"{0} за {1}".format(name, \
        u"{0} {1}".format(u"{0:,}".format(adv.get("price")).replace(","," "), morph_word(u"рубль", count=adv.get("price"))))
    seller = db.get_user(adv.get("user_id"))
    return render_template("cat/adv_show.html", \
        header = header,
        title = title,
        adv = adv,
        seller = seller)

def sale_show(id):
    adv = None
    try:
        adv = sales().find_one({'_id': ObjectId(id)}) if id else None
    except Exception, e:
        print(e)
    
    if not adv:
        abort(404)

    name = u"Продам {0} породы {1} в г. {2}".format( \
        morph_word(get_pet_name(adv.get("pet_id")), {"accs"}).lower(), \
        get_breed_name(adv.get("breed_id"), adv.get("pet_id")).lower(),\
        get_city_name(adv.get("city_id"), "i")
    )
    header = Markup(u"Продам {0} породы {1} в г.&nbsp;{2}".format( \
        morph_word(get_pet_name(adv.get("pet_id")), {"accs"}).lower(), \
        get_breed_name(adv.get("breed_id"), adv.get("pet_id")).lower(),\
        get_city_name(adv.get("city_id"), "i")
    ))
    title = u"{0} за {1}".format(name, \
        u"{0} {1}".format(u"{0:,}".format(adv.get("price")).replace(","," "), morph_word(u"рубль", count=adv.get("price"))))
    seller = db.get_user(adv.get("user_id"))
    return render_template("sale_show.html", \
        header = header,
        title = title,
        adv = adv,
        seller = seller)



@app.route("/account/")
@login_required
def account():
    return redirect(url_for('account_sale'))


@app.route("/account/stud/")
@login_required
def account_stud():
    tmpl = render_template("account/stud.html", title=u"Повязать")
    return tmpl


@app.route("/account/wanted/")
@login_required
def account_wanted():
    tmpl = render_template("account/wanted.html", title=u"Розыскиваю")
    return tmpl


@app.route("/account/user/")
@login_required
def account_user():
    tmpl = render_template("account/user.html", title=u"Учетные данные")
    return tmpl

@app.route("/account/contact/", methods = ["GET", "POST"])
@login_required
def account_contact():
    user = db.get_user(current_user.id)
    form = Contact(request.form)
    if request.method == "POST":
        if form.validate():
            db.save_user_contact(current_user.id, \
                form.username.data, form.city.city_id, \
                form.phone.data, form.skype.data)
            flash(u"Контактная информация обновлена.", "success")
            return redirect(url_for("account_contact"))
    else:
        form.city.data = get_city_region(user.get("city_id"))
        form.username.data = user.get("username")
        form.phone.data = user.get("phone") 
        form.skype.data = user.get("skype")

    tmpl = render_template("account/contact.html", title=u"Контактная информация", form = form)
    return tmpl

@app.route("/account/adoption/")
@login_required
def account_adoption():
    tmpl = render_template("account/adoption.html", title=u"Отдам даром")
    return tmpl

@app.route("/account/cat/")
@login_required
def account_cat_advs():
    advs = db.get_cat_advs_by_user(current_user.id)
    tmpl = render_template("account/cat/advs.html", \
        title=u"Мои объявления о продаже кошек", \
        advs = [dict(adv, **{'active_date': adv.get('update_date') + timedelta(days=14)}) for adv in advs])
    return tmpl


@app.route("/account/dog/")
@login_required
def account_dog_advs():
    advs = db.get_dog_advs_by_user(current_user.id)
    tmpl = render_template("account/dog/advs.html", \
        title=u"Мои объявления о продаже собак", \
        advs = [dict(adv, **{'active_date': adv.get('update_date') + timedelta(days=14)}) for adv in advs])
    return tmpl


@app.route("/account/dog/<adv_id>/", methods = ['GET', 'POST'])
@login_required
def account_dog_adv_edit(adv_id):
    dog = db.get_dog_adv_for_user(adv_id, current_user.id)
    if not dog:
        abort(404)

    form = Dog(request.form)
    if request.method == "POST":
        if form.validate():
            save_dog_adv(adv_id = adv_id, form = form)
            msg = u"Объявление '%s' опубликовано." % form.title.data
            flash(msg, "success")
            return render_template("/account/dog/adv_edit_success.html", title = msg)
    else:
        for f in form:
            f.set_db_val(dog.get(f.get_db_name()))
      
        form.username.data = dog.get("username") or (current_user.username if current_user.username != u'Пользователь' else u'')
        form.phone.data = dog.get("phone") or current_user.phone
        form.skype.data = dog.get("skype") or current_user.skype
    return render_template("/account/dog/adv_edit.html", \
        form = form, \
        title = u"Редактировать объявление о продаже собаки", \
        dog = dog, \
        fields = get_fields(form))

@app.route("/account/dog/new/", methods = ["GET", "POST"])
@login_required
def account_dog_adv_new():
    form = Dog(request.form)
    if request.method == "POST":
        if  form.validate():
            id = save_dog_adv(form)
            msg = u"Объявление '%s' добавлено." % form.title.data
            flash(msg, "success")
            return render_template("/account/dog/adv_edit_success.html", title=msg)
    else:
        form.username.data = current_user.username if current_user.username != u'Пользователь' else u''
        form.city.data = get_city_region(current_user.city_id)
        form.phone.data = current_user.phone
        form.skype.data = current_user.skype

    return render_template("/account/dog/adv_edit.html", \
        form = form, \
        fields = get_fields(form), \
        title=u"Новое объявление о продаже собаки")

def save_dog_adv(form, adv_id = None):
    form.photos.photonames = []
    if form.photos.data:
        form.photos.photonames = form.photos.data.split(',')
        form.photos.photonames = filter(lambda x: x and len(x) > 0, form.photos.photonames)
        for photoname in form.photos.photonames:
            if os.path.exists(photos.path(photoname)):
                with open(photos.path(photoname)) as file:
                    db.save_photo(file)

    db.save_dog_adv_2(user_id = current_user.id, \
        adv_id = adv_id, \
        form  = form, \
        attraction = calc_attraction(form)
        )
    return adv_id

@app.route("/account/dog/<adv_id>/remove/", methods = ['GET'])
@login_required
def account_dog_adv_remove(adv_id):
    adv = db.remove_dog_adv(adv_id, current_user.id)
    if adv:
        flash(u"Объявление '%s' удалено." % adv["title"], \
            "success")
    return redirect(url_for("account_dog_advs"))

@app.route("/account/sale/<adv_id>/remove", methods = ['GET'])
@login_required
def account_cat_adv_remove(adv_id):
    adv = sales().find_one(
        {'_id': {'$in':[id, ObjectId(id)]}, 
        'user_id': {'$in': [current_user.id, str(current_user.id)]}})
    if adv:
        sales().remove(adv)
        flash(u"Объявление '%s' удалено." % adv["title"], "success")
    return redirect(url_for("account_cat_advs"))
 

def save_cat_adv(form, adv_id = None, moderator = None):
    filenames = []
    if form.photos.data:
        filenames = form.photos.data.split(',')
        filenames = filter(lambda x: x and len(x) > 0, filenames)
        for filename in filenames:
            if os.path.exists(photos.path(filename)):
                with open(photos.path(filename)) as file:
                    db.save_photo(file)

    now = datetime.utcnow()
    cat = {
        'pet_id': form.breed.pet_id, \
        'breed_id': form.breed.breed_id, \
        'title': form.title.data, \
        'desc': form.desc.data, \
        'photos': filenames, \
        'price' : form.price.data, \
        'update_date' : now, \
        "city_id": form.city.city_id, \
        "phone" : form.phone.data, \
        "skype" : form.skype.data, \
        "gender_id": num(form.gender.data)}
    if moderator:
        cat['username'] = form.username.data
        cat['email'] = form.email.data
        cat['moderator_id'] = str(moderator.id)
        cat['moderate_date'] = now
    else:
        cat['user_id'] = str(current_user.id)
    if id:
        db.cat_advs.update(
            {'_id': ObjectId(adv_id)} 
            , {'$set': cat}, upsert=True)
    else:
        cat["add_date"] = now
        adv_id = db.cat_advs.insert(cat)
    return adv_id


@app.route("/account/cat/<adv_id>/", methods = ['GET', 'POST'])
@login_required
def account_cat_adv_edit(adv_id):
    cat = db.get_cat_adv_for_user(adv_id, current_user.id)
    if not cat:
        abort(404)

    form = Cat(request.form)
    if request.method == "POST":
        if form.validate():
            save_cat_adv(form, adv_id)
            flash(u"Объявление '%s' опубликовано." % form.title.data, "success")
            return redirect(url_for("account_cat_advs"))
    else:
        form.breed.data = get_breed_name(cat.get("breed_id"), cat.get("pet_id"))
        form.title.data = cat.get("title")
        form.desc.data = cat.get('desc')
        form.price.data = num(cat.get('price'))
        form.gender.data = str(num(cat.get('gender_id')) or '')
        form.photos.data = ",".join(cat.get("photos"))
        form.city.data = get_city_region(cat.get("city_id"))
        form.phone.data = cat.get("phone") or current_user.phone
        form.skype.data = cat.get("skype") or current_user.skype
    return render_template("/account/cat/adv_edit.html", form=form, title=u"Редактировать объявление о продаже", btn_name = u"Опубликовать", cat = cat)


@app.route("/account/cat/new/", methods = ['GET', 'POST'])
@login_required
def account_cat_adv_new():
    form = Cat(request.form)
    if request.method == "POST":
        if  form.validate():
            id = save_cat_adv(form)
            flash(u"Объявление '%s' добавлено." % form.title.data, "success")
            return redirect(url_for('account_cat_advs'))
    else:
        form.city.data = get_city_region(current_user.city_id)
        form.phone.data = current_user.phone
        form.skype.data = current_user.skype
    return render_template("/account/cat/adv_edit.html", form=form, title=u"Новое объявление о продаже кошки", btn_name = u"Добавить")


@app.route("/spravka/")
def help():
    return render_template("/help.html", \
        title=u"Справка", header=Markup(u"Справочная информация"))

@app.route("/spravka/privlekatelnost-obyavleniya/")
def help_attraction():
    return render_template("/help/faq_attraction.html", \
        title=u"Привлекательность объявления", header=Markup(u"Привлекательность объявления"))

@app.route("/poleznoe/")
def advice():
    return render_template("/advice.html", \
        title=u"Полезное", header = u"Статьи о животных")

@app.route("/poleznoe/10-oshibok-kotoryx-sleduet-izbegat-pokupaya-porodistogo-shhenka")
def advice_article_1():
    return render_template("/advice/10-oshibok-kotoryx-sleduet-izbegat-pokupaya-porodistogo-shhenka.html", \
        title = u"Десять ошибок, которых следует избегать, покупая породистого щенка")


@app.route("/poleznoe/kalendar-sobachej-beremennosti")
def advice_article_2():
    return render_template("/advice/kalendar-sobachej-beremennosti.html", title = u"Календарь собачьей беременности")

# upload files
# 

@app.route('/upload/', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    if file:
        filename = photos.save(file, name=str(uuid4()) + ".")
        # filename = resize_image(photos.path(filename), height = 400)
        return filename
        
@app.route('/thumbnail/<filename>/')
def thumbnail(filename):
    path = photos.path(get_thumbnail_filename(filename))
    if not os.path.exists(path):  
        (name, file) = db.get_photo(filename)
        if name and file:
            _name = create_thumbnail(file, photos.path(name), app.config['UPLOADED_PHOTOS_DEST'])
        else:
            if os.path.exists(photos.path(filename)):
                with open(photos.path(filename)) as f:
                    create_thumbnail(f.read(), photos.path(filename), app.config['UPLOADED_PHOTOS_DEST'])

    return send_file(path)
    
@app.route('/photo/<filename>/', defaults = {'height': 600})
@app.route('/photo/<filename>/<int:height>/')
def photo(filename, height):
    height = min(height, 600)
    if height:
        (name, ext) = os.path.splitext(filename)
        path = photos.path(name + str(height) + ext)
    else:
        path = photos.path(filename) 
    if not os.path.exists(path):
        try:
            (name, file) = db.get_photo(filename)
            if name and file:
                with open(path, 'w') as f:
                    f.write(file)
            if height:
                resize_image(path, height = height)    
        except Exception, e:
            print(e)
            os.remove(path)

    return send_file(path)

@app.route("/prodazha-sobak/<adv_id>/email/", \
    methods = ["POST", "GET"])
def dog_adv_email(adv_id):
    form = SendMail(request.form)
    adv = db.get_dog_adv(adv_id)
    
    if not adv:
        abort(404)

    seller = db.get_user(adv.get("user_id"))
    if not seller and not adv.get('email'):
        abort(404)
    seller_email = adv.get('email') or seller.get('email')
    seller_username = adv.get('username') or seller.get('username') 
    print("seller_username", seller_username)

    if request.method == "POST":
        if form.validate():
            send_from_sale(adv.get("_id"), \
                url_for('dog_adv_show', adv_id = adv.get('_id'), _external =True), \
                form.email.data, form.username.data, \
                seller_email, seller_username, \
                u"Сообщение от пользователя сайта Поводочек", form.message.data)
            # if form.sms_alert.data and seller.get('phone') and seller.get('phone_adv_sms'):
            #     send_sms(u"Пользователь сайта Поводочек отправил вам почтовое сообщение.", \
            #         [seller.get('phone')] )
            return render_template("/mail_sent.html", title = u"Сообщение успешно отправлено")
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("/dog/adv_email.html", form = form, seller_email = seller_email, seller_username = seller_username, title = u"Написать письмо пользователю %s" % seller_username, header=Markup(u"Написать письмо пользователю <small>%s</small>" % seller_username))

@app.route("/prodazha-koshek/<adv_id>/email/", methods = ["POST", "GET"])
def cat_adv_email(adv_id):
    form = SendMail(request.form)
    adv = db.get_cat_adv(adv_id)
    # adv = sales().find_one(ObjectId(id))
    
    if not adv:
        abort(404)

    seller = db.get_user(adv.get("user_id"))
    if not seller and not adv.get('email'):
        abort(404)
    seller_email = adv.get('email') or seller.get('email')
    seller_username = adv.get('username') or seller.get('username') 
    print("seller_username", seller_username)

    if request.method == "POST":
        if form.validate():
            send_from_sale(adv.get('_id'), \
                url_for('cat_adv_show', adv_id = adv.get('_id'), _external =True), \
                form.email.data, \
                form.username.data, seller_email, seller_username, \
                u"Сообщение от пользователя сайта Поводочек", \
                form.message.data)
            # if form.sms_alert.data and seller.get('phone') and seller.get('phone_adv_sms'):
            #     send_sms(u"Пользователь сайта Поводочек отправил вам почтовое сообщение.", \
            #         [seller.get('phone')] )
            return render_template("/mail_sent.html", title = u"Сообщение успешно отправлено")
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("/mail_sale.html", form = form, seller_email = seller_email, seller_username = seller_username, title = u"Написать письмо пользователю %s" % seller_username, header=Markup(u"Написать письмо пользователю <small>%s</small>" % seller_username))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/prodazha-koshek/goroda/')
def sale_cats_cities():
    return sale_pets_cities(pet_id = CAT_ID) 

@app.route('/prodazha-sobak/goroda/')
def sale_dogs_cities():
    return sale_pets_cities(pet_id = DOG_ID) 

def sale_pets_cities(pet_id):
    pet_name = morph_word(get_pet_name(pet_id), ["plur", "gent"]).lower()

    advs = db.get_dog_by_cities() if pet_id == DOG_ID \
        else db.get_cat_by_cities()

    breeds_by_cities = [(letter, list(group)) for letter, group in groupby(advs, lambda adv : adv['city_name'][0])]

    return render_template("/sale_cities.html", \
        title=u"Объявления о продаже {0} в городах России".format(pet_name), \
        breeds_by_cities = breeds_by_cities, \
        pet_id = pet_id, \
        pet_name = pet_name)


@app.route('/tos/')
def tos():
    return render_template("/tos.html", title = u"Пользовательское соглашение")

@app.route('/kontakty/')
def contacts():
    return render_template("/contacts.html", \
        title=u"Контактная информация")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title = u"Страница не найдена"), 404

# admin

from functools import wraps

def admin_requried(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user.email not in app.config["ADMIN_EMAILS"]:
            abort(401)
        return func(*args, **kwargs)
    return decorated_view


@app.route('/admin/user/')
@admin_requried
def admin_users():
    page = int(request.args.get("page") or 1)
    total = db.users.count()
    perpage = 100
    u = [user for user in db.admin_get_users(perpage, \
        (page - 1) * perpage)]

    return render_template('/admin/users.html', title = Markup(u"Админка: пользователи"), users = u, total = total, perpage = perpage, page = page)

@app.route('/admin/sale/')
@admin_requried
def admin_sale():
    page = int(request.args.get("page") or 1)
    total = sales().count()
    perpage = 100
    advs = [adv for adv in sales().find(sort = [('update_date', DESCENDING)], limit = perpage, skip = (page - 1) * perpage)]
    for seller in users.find({'_id':{'$in' : [ObjectId(adv.get('user_id')) for adv in advs if adv.get('user_id') ]}}):
        for adv in [adv for adv in advs if not adv.get('email')]:
            # print(seller['email'])
            if ObjectId(adv.get('user_id')) == seller['_id']:
                adv['email'] = seller['email']
                adv['username'] = seller['username']

    return render_template('/admin/sale.html', title = Markup(u"Админка: объявления о продаже"), advs = advs, total = total, perpage = perpage, page = page)


@app.route('/admin/sale/new/', methods = ['GET', 'POST'])
@admin_requried
def admin_sale_add():
    form = Sale(request.form)
    if request.method == "POST" and form.validate():
        id = sale_save(form, moderator = current_user)
        flash(u"Объявление '%s' добавлено." % form.title.data, "info")
        return redirect(url_for('admin_sale'))
    return render_template("/admin/sale_edit.html", form = form, title = Markup(u"Админка: добавить объявление о продаже"), btn_name = u"Добавить")

@app.route('/admin/sale/ban/<adv_id>/')
@admin_requried
def admin_sale_ban(adv_id):
    return ""


@app.route('/admin/sale/edit/<adv_id>/', methods = ["GET","POST"])
@admin_requried
def admin_sale_edit(adv_id):
    adv = sales().find_one({'_id': ObjectId(adv_id)})
    if not adv:
        abort(404)

    form = Sale(request.form)
    if request.method == "POST":
        print(form.price.data)
        if form.validate():
            sale_save(form, adv_id, moderator = current_user)
            flash(u"Объявление '%s' обновлено." % form.title.data, "info")
            return redirect(url_for("admin_sale"))
    else:
        form.breed.data = get_breed_name(adv.get("breed_id"), adv.get("pet_id"))
        form.title.data = adv.get("title")
        form.desc.data = adv.get('desc')
        form.price.data = num(adv.get('price'))
        form.gender.data = str(num(adv.get('gender_id')) or '')
        form.photos.data = ",".join(adv.get("photos"))
        form.city.data = get_city_region(adv.get("city_id"))
        # form.age.data = str(num(adv.get("age_id")))
        form.phone.data = adv.get("phone")
        form.skype.data = adv.get("skype")
        form.email.data = adv.get("email")
        form.username.data = adv.get("username")
    return render_template("/admin/sale_edit.html", form = form, title=u"Админка: редактировать объявление о продаже", btn_name = u"Сохранить", adv = adv)
    
@app.route('/test/parser/avito/')
def test_parser_avito():
    response = make_response(render_template('/test/parser_avito.html', title = u"Parsing from avito"))
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response

@app.route('/ajax/avito/parse/')
def ajax_avito_parse():
    adv_url = request.args["url"]
    if adv_url:
        adv = parse_avito_adv(adv_url)
    return jsonify(adv)

@app.route('/sitemap.xml')
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])


def get_pet_advs_for_mosaic(skip, limit = 10, pet_id = DOG_ID):
    if pet_id == DOG_ID:
        return [{"src":url_for('thumbnail', \
            filename = adv.get('photos')[0], width= 300), \
        'url' : url_for('dog_adv_show', adv_id = adv.get('_id')), \
        'id': str(adv.get('_id')), \
        'p' : adv.get('price'), \
        'b' : get_breed_dog_name(adv.get('breed_id')), \
        's' : {'h':100, 'w':150}, 
        't' : adv.get('title')}
        for adv in db.get_dog_advs_for_mosaic(skip, limit)]
    elif pet_id == CAT_ID:
        return  [{"src":url_for('thumbnail', \
            filename = adv.get('photos')[0], width= 300), \
        'url' : url_for('cat_adv_show', adv_id = adv.get('_id')), \
        'id': str(adv.get('_id')), \
        'p' : adv.get('price'), \
        'b' : get_breed_cat_name(adv.get('breed_id')), \
        's' : {'h':100, 'w':150}, 
        't' : adv.get('title')}
        for adv in db.get_cat_advs_for_mosaic(skip, limit)]
    else:
       return None

@app.route("/ajax/mosaic/showmore/<int:pet>/", methods = ["GET"], defaults= {"limit":10, 'skip': 0})
@app.route("/ajax/mosaic/showmore/<int:pet>/<int:skip>/", methods = ["GET"], defaults= {"limit":10})
@app.route("/ajax/mosaic/showmore/<int:pet>/<int:skip>/<int:limit>/", methods = ["GET"])
def ajax_mosaic_showmore(pet, skip, limit):
    print(pet)
    advs = get_pet_advs_for_mosaic(skip, limit = limit, pet_id = pet)
    return jsonify(advs = advs)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
