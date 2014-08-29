#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, flash, redirect, url_for, session, send_from_directory, send_file, abort, jsonify, Markup, make_response)
from flask_login import (LoginManager, current_user,
    login_user, logout_user, login_required,
    confirm_login, fresh_login_required, user_logged_in)

from wtforms import (Form, BooleanField, TextField, PasswordField, validators)
from forms import (SignUp, SignIn, Cat, Profile, \
    Activate,ResetPassword, ChangePassword, \
    SaleSearch, SendMail, ChangeEmail, SignUpBasic, \
    get_breed_from_field, Dog, DogSearch, get_geo_from_field,
    AdminNews, Comment, Subscribe)
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

from flaskext.uploads import (UploadSet, configure_uploads, IMAGES,UploadNotAllowed)

from security import hash_password, check_password

from flask_mail import (Mail, Message)
from threading import Thread
from momentjs import MomentJS
from photo_helper import (create_thumbnail, get_thumbnail_filename, resize_image, get_photo_size)
from helpers import (num, qoute_rus, morph_word, date2str)

from smsgate import send_sms

import dic.ages as ages
import dic.genders as genders
import dic.pets as pets
import dic.breeds as breeds
import dic.geo as geo
import dic.pet_docs
import dic.adv_types as adv_types
import dic.dog_marks as dog_marks
import dic.metro as metro

from flaskext.markdown import Markdown
from flask.ext.assets import Environment, Bundle
from advs_parser import parse_avito_adv
import db
from pymongo.errors import InvalidId
             

import random
import json
from pprint import pprint 
from forms.fields import (get_fields, calc_attraction)
import cProfile
import sys

from mailing import mailer
import users


photos = UploadSet('photos', IMAGES)

app = Flask(__name__)

config = os.path.join(app.root_path, 'config.py')
app.config.from_pyfile(config)

mail = Mail(app)
markdown = Markdown(app)
assets = Environment(app)

js = Bundle('js/jquery-1.11.0.min.js', \
    'js/jquery-ui-1.10.3.custom.min.js', \
    'js/jquery.validate.min.js', \
    'js/jquery.validate.ru.js', \
    'js/jquery.inputmask.bundle.min.js', \
    'js/moment.min.js', \
    'js/moment.min.ru.js', \
    'js/jquery.nouislider.min.js', \
    'js/jquery.flexslider.js', \
    'js/jquery.touch-punch.min.js', \
    'js/jquery.shapeshift.js', \
    'js/jquery.mosaicflow.min.js', \
    'js/bootstrap3-typeahead.js', \
    'js/bootstrap.min.js', \
    'js/list.min.js',
    'js/list.fuzzysearch.js',
    'js/bootstrap-datepicker.js',
    'js/bootstrap-datepicker.ru.js',
    'js/povodochek.js',
    'js/jquery.simplyCountable.js',
    filters='rjsmin',
    output='gen/js.js')
assets.register('js_all', js)

js_ie8 = Bundle('js/html5shiv.js', \
    'js/respond.min.js', \
    filters='rjsmin', \
    output='gen/js_ie8.js')
assets.register('js_ie8', js_ie8)

css = Bundle(
    'css/bootstrap.min.css', \
    'css/nouislider.fox.css', \
    'css/font-awesome.min.css', \
    'css/flexslider.css', \
    'css/datepicker3.css', \
    filters = 'cssmin', \
    output = 'gen/css.css')
assets.register('css_all', css)

configure_uploads(app, (photos))

login_manager = LoginManager()

login_manager.anonymous_user = users.Anonymous
login_manager.login_view = "/signin/"
login_manager.login_message = u"Пожалуйста, войдите, чтобы увидеть содержимое страницы."
login_manager.refresh_view = "reauth"

login_manager.setup_app(app)

def is_signed_in(sender, user, **extra):
    session["dog_sort"] = 3
    session["cat_sort"] = 3

user_logged_in.connect(is_signed_in, app)

# jinja custom filters and globals

app.jinja_env.globals['momentjs'] = MomentJS
app.jinja_env.filters['json'] = json.dumps

def jinja_format_datetime(value, format='%H:%M, %d.%m.%y'):
    return value.strftime(format) if value  else ""

app.jinja_env.filters['format_datetime'] = jinja_format_datetime

def jinja_date(value):
    return datetime.date(value) if value else ""

app.jinja_env.filters['date'] = jinja_date

def jinja_format_price(value, template=u"{0:,.0f}"):
    return Markup((template.format(value) if value else u"").replace(u",", u"&nbsp;"))

app.jinja_env.filters['format_price'] = jinja_format_price

def jinja_format(template=u"{0}", *args):
    return template.format(*args)

app.jinja_env.globals['format'] = jinja_format

def jinja_sorted(iterable, key = None, reverse = False):
    return sorted(iterable, key = eval(key), reverse = reverse) 

app.jinja_env.filters['sorted'] = jinja_sorted
app.jinja_env.globals['genders'] = genders
app.jinja_env.globals['ages'] = ages
app.jinja_env.globals['geo'] = geo
app.jinja_env.globals['utcnow'] = datetime.utcnow()
app.jinja_env.globals['pet_docs'] = dic.pet_docs
app.jinja_env.globals['breeds'] = breeds
app.jinja_env.globals['pets'] = pets
app.jinja_env.globals['users'] = users
app.jinja_env.globals['adv_types'] = adv_types
app.jinja_env.globals['dog_marks'] = dog_marks
app.jinja_env.globals['metro'] = metro
app.jinja_env.filters['morph_word'] = morph_word



def change_query(url, param, old, new):
    if url and param and old and new:
        param_value = u"{0}={1}".format(param, old)
        url_non_param = url.replace(u"&" + param_value, u"").replace(param_value, "")
        return u"{0}{1}&{2}={3}".format(url_non_param, u"?" if u"?" not in url_non_param else u"", param, new)
    return url

app.jinja_env.filters['change_query'] = change_query

def jinja_max(*args):
    return max(*args)

app.jinja_env.filters['max'] = jinja_max

def jinja_min(*args):
    return min(*args)

app.jinja_env.filters['min'] = jinja_min


if not app.debug and app.config["MAIL_SERVER"] != '':
    import logging
    from ThreadedSMTPHandler import ThreadedSMTPHandler
    mail_handler = ThreadedSMTPHandler(subject = 'povodochek:error:web')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('log/povodochek.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


@login_manager.user_loader
def load_user(user_id):
    try:
        return users.get_user(user_id)
    except Exception, e:
        app.logger.error(e)
    return
    

@app.route("/")
def index():
    tmpl = render_template('index.html',
        dog_breeds_rating = db.get_dog_breeds_rating(limit = 10),
        cat_breeds_rating = db.get_cat_breeds_rating(limit = 10),
        title = u"Продажа и покупка породистых собак и кошек")
    return tmpl

@app.route("/signin/", methods = ["POST", "GET"])
def signin():
    form = SignIn(request.form)
    if request.method == "POST" and form.validate():
        (login_or_email, password, remember) = (form.login.data, form.password.data, form.remember.data)
        user = db.get_user_by_login(login_or_email) or db.get_user_by_email(login_or_email)
        if user and check_password(user.get("pwd_hash"), password):
            if True or user.get("activated"):
                if login_user(users.User(user.get('_id')), remember=remember):
                    return redirect(request.args.get("next") \
                        or url_for("account_profile"))
                else:
                    flash(u"Извините, но вы не можете войти.", "error")
            else:
                app.logger.info('disactivated')
                flash(Markup(u"Вы не можете войти на сайт, так как регистрация не подтверждена. Проверьте, пожалуйста, электронную почту или отправьте <a target='_blank' href='{0}'>ссылку на активацию</a> повторно.".format(url_for('activate', confirm=''))), "error")
        else:
            flash(u"Неправильный логин или пароль.", "error")
    return render_template("signin.html", form=form, title=u"Вход")

@app.route("/ajax/activate/remember/later/")
@login_required
def ajax_activate_remember_later():
    later = session["activate_remember_later"] = True
    return "success"

@app.route("/ajax/typeahead/geo/city/", methods = ["GET"])
def ajax_typeahead_geo_cities():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    cities = db.get_geo_cities_for_typeahead(query, limit)
    return jsonify(items = cities )   

@app.route("/ajax/typeahead/geo/all/", methods = ["GET"])
def ajax_typeahead_geo_all():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    geo_all = db.get_geo_all_for_typeahead(query, limit)
    return jsonify(items = geo_all)  

@app.route("/ajax/typeahead/breed/all/", methods = ["GET"])
def ajax_typeahead_breed():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    dog_breeds = [u"%s, Собаки" % name for name 
        in db.get_dog_breeds_for_typeahead(query, limit /2)]
    cat_breeds = [u"%s, Кошки" % name for name 
        in db.get_cat_breeds_for_typeahead(query, limit /2)]

    return jsonify(items = dog_breeds + cat_breeds )  

@app.route("/ajax/typeahead/breed/dog/", methods = ["GET"])
def ajax_typeahead_dog():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)

    breeds = db.get_dog_breeds_for_typeahead(query, limit)
    return jsonify(items = breeds ) 


@app.route("/ajax/typeahead/breed/cat/", methods = ["GET"])
def ajax_typeahead_cat():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    matcher = query.lower()

    breeds = db.get_cat_breeds_for_typeahead(query, limit)
    return jsonify(items = breeds ) 


@app.route("/ajax/breed/picker/dog/", methods = ["GET"])
def ajax_breed_picker_dog():
    return render_template('dog/breed_picker.html', input_id = request.args.get("input_id"), trigger_id = request.args.get("trigger_id"))

@app.route("/ajax/breed/picker/cat/", methods = ["GET"])
def ajax_breed_picker_cat():
    return render_template('cat/breed_picker.html', input_id = request.args.get("input_id"), trigger_id = request.args.get("trigger_id"))

@app.route('/ajax/avito/parse/')
def ajax_avito_parse():
    adv_url = request.args["url"]
    if adv_url:
        adv = parse_avito_adv(adv_url)
    return jsonify(adv)

@app.route("/test/location/", methods = ["GET"])
def test_location():
    return render_template("test/location.html", title=u"Location")

@app.route("/test/email/stuff/")
def test_email_stuff():
    msg = Message("Hello", recipients=["popovegor@gmail.com"])
    mail.send(msg)
    return "Stuff email!"

def send_activate(email, confirm):
    msg = Message("Подтверждение регистрации на сайте Поводочек", recipients = [email])
    msg.html = render_template("email/activate.html", confirm = confirm)
    mail.send(msg)

def send_confirm_email(email):
    msg = Message("Подтверждение изменения почтового адреса на сайте Поводочек", recipients = [email])
    msg.html = render_template("email/confirm_email.html", base64_email = base64.b64encode(email))
    mail.send(msg)

def send_signup(username, email, password, confirm):
    msg = Message(u"Регистрация на сайте Поводочек", recipients=[email])
    msg.html = render_template("email/signup.html", username=username, email = email, password = password, confirm = confirm)
    mail.send(msg)

def send_reset_password(email, login, asign, password):
    msg = Message(u"Сброс пароля для сайта Поводочек", recipients=[email])
    msg.html = render_template("email/reset_password.html", email = email, password = password, asign = asign)
    mail.send(msg)

def send_from_sale(adv_id, adv_title, adv_url, email, username, \
    seller_email, seller_username, subject, message):
    # adv = sales().find_one(ObjectId(sale_id))
    if adv_id and seller_email:
        msg = Message(subject, recipients=[seller_email])
        msg.html = render_template("email/from_adv.html", \
            subject = subject, \
            message = message, \
            adv_url = adv_url, \
            adv_id = adv_id, \
            adv_title = adv_title, \
            seller_email = seller_email, \
            seller_username = seller_username, \
            email = email, \
            username = username, \
            date = datetime.now())
        msg.reply_to  = u"%s <%s>" % (username or u"", email)
        mail.send(msg)

    
@app.route("/test/email/from_dog_adv/")
def test_email_from_dog_adv():
    msg = Message(u"Сообщение от %s сайта Поводочек" % (u'пользователя' if current_user.is_authenticated() else u'гостя'), \
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

    if current_user.is_authenticated() and current_user.activated:
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
        if login_user(users.get_user(user.get('_id'))):
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
        (email, password, confirm, username) = (form.email.data,  form.password.data, str(uuid4()), form.username.data)
        user_id = db.signup_user(email, hash_password(password), username, confirm)
        try:
            send_signup(username, email, password, confirm)
        except Exception, e:
            db.revert_singup(user_id)
            flash(u"У нас на сервере произошла ошибка, попробуйте зарегистрироваться чуть позже.", "error")
            raise e

        flash(Markup(u"Для того чтобы подтвердить регистрацию, перейдите по ссылке в отправленном на адрес <b>%s</b> письме." % (email)), "info")
        if login_user(users.User(user_id), remember = True):
            return redirect(request.args.get('next') or url_for('account_profile'))
        else:
                return redirect(url_for('signin'))

    return render_template('signup_basic.html', form=form, title=u"Регистрация")

@app.route("/reset-password/", methods = ["GET", "POST"])
def reset_password():
    form = ResetPassword(request.form)
    title = u"Сброс пароля"
    if request.method == "POST":
        if form.validate():
            password = str(hash(str(uuid1())) % 10000000)
            asign = str(uuid4())
            user = db.reset_user_password(form.email_or_login.user.get("_id"), \
                hash_password(password), asign)
            if user:
                send_reset_password(user.get('email'), user.get("login"), asign, password)
                return render_template("reset_password_sent.html", title=title, email = user.get('email'))
    elif current_user.is_authenticated():
        form.email_or_login.data = current_user.email
    
    return render_template("reset_password.html", title=title, form = form)

@app.route("/signout/")
@login_required
def signout():
    logout_user()
    url = request.args.get("url")
    return redirect( url if url else url_for('index'))


def sale_find_header(pet_id, breed_id, city, region):
    # generate title
    header = u"Купить <span>(продают)</span> <span class=''>{0}</span>{1}{2}"
    title = u"Купить {0}{1}{3}: Продажа {2}{1}{3}"
    pet = u"собаку или кошку"

    if pet_id == pets.DOG_ID:
        pet = u"собаку"
    elif pet_id == pets.CAT_ID:
        pet = u"кошку"

    breed = breeds.get_breed_name(breed_id)
    breed_header = breed
    breed_title = breed
    if breed:
        # breed = u" {0}".format(morph_word(breed, {"gent"}).lower())
        breed_header = Markup(u" породы <b class='dsf-header-breed'>%s</b>" % breed.lower() )
        breed_title = Markup(u" породы {0}".format(breed.lower()))

    geo_header = u""
    geo_title = u""
    if city:
        geo_header = u" в г. <b class='dsf-header-location'>{0}</b>".format(city.get('city_name'))
        geo_title = u" в г. {0}".format(city.get('city_name'))
        # if form.distance.data:
            # city = u"{0}(+ {1} км)".format(city, form.distance.data) 
    elif region:
        geo_header = u" в <b class='dsf-header-location'>%s</b>" % region.get('region_name_p')
        geo_title = u" в %s" % region.get('region_name_p')

    return (header.format(pet, breed_header, geo_header), \
        title.format(pet, breed_title, morph_word(pet, {"gent", "plur"}), geo_title), pet, breed) 


#city=Ленинградская область
#city=Сосновый Бор, Ленинградская область
#city=1
#city=-1
@app.route("/prodazha-sobak/")
def dog_search():
    
    form = DogSearch(request.args)

    (city, region) = get_geo_from_field(form.city)

    if city:
        form.city.data = geo.format_city_region(city)
    elif region:
        form.city.data = region.get('region_name')

    breed = get_breed_from_field(form.breed)
    breed_id = None
    if breed:
        form.breed.data = breed.get("breed_name")
        breed_id = breed.get("breed_id")
    pet_id = pets.DOG_ID
    # sort
    session["dog_sort"] = form.sort.data or \
        session.get("dog_sort") or (3 if current_user.is_authenticated() else 4)

    (advs, count, total) = db.find_dog_advs(
        breed_id = breed_id, \
        gender_id = form.gender.data, \
        region_id = region.get('region_id') if region else None, \
        city_id = city.get('city_id') if city else None, \
        distance = (form.distance.data + 0.01) if form.distance.data else None, \
        photo = form.photo.data, \
        video = form.video.data, \
        delivery = form.delivery.data, \
        champion_bloodlines = form.champion_bloodlines.data, \
        contract = form.contract.data, \
        pedigree = form.pedigree.data, \
        price_from = form.price_from.data if form.price_from.data else None, \
        price_to = form.price_to.data if form.price_to.data else None, \
        sort = session.get("dog_sort"),
        skip = (form.page.data - 1) * form.perpage.data, \
        limit = form.perpage.data
        )

    (header, title, pet_name, breed_name) = sale_find_header(pet_id, breed_id, city, region)

    tmpl = render_template("dog/search.html", header=Markup(header), \
      title=title, form = form, advs = advs, \
      pet = pet_name, pet_id = pet_id,
      breed = breed_name, breed_id = breed_id,
      region = region.get("region_name") if region else None,
      region_id = region.get('region_id') if region else None, 
      city = city.get("city_name") if city else None, \
      city_id = city.get("city_id") if city else None, \
      sort = session.get("dog_sort"), \
      count = count, total = total )
    return tmpl


@app.route("/prodazha-koshek/")
def cat_search(sale_search_form = None):
    form = sale_search_form or SaleSearch(request.args)
    

    (city, region) = get_geo_from_field(form.city)

    if city:
        form.city.data = geo.format_city_region(city)
    elif region:
        form.city.data = region.get('region_name')

    breed = get_breed_from_field(form.breed)
    breed_id = None
    if breed:
        form.breed.data = breed.get("breed_name")
        breed_id = breed.get("breed_id")
    pet_id = pets.CAT_ID
    # sort
    session["cat_sort"] = form.sort.data or session.get("cat_sort") or (3 if current_user.is_authenticated() else 4)
    
    (advs, count, total) = db.find_cat_advs(breed_id = breed_id, \
        gender_id = form.gender.data, \
        region = region, \
        city = city, \
        distance = form.distance.data + 0.01, \
        photo = form.photo.data, \
        price_from = form.price_from.data  * 1000, \
        price_to = (form.price_to.data if num(form.price_to.data) < 100 else 0) * 1000, \
        sort = session.get("cat_sort"),
        skip = (form.page.data - 1) * form.perpage.data, \
        limit = form.perpage.data
        )

    (header, title, pet_name, breed_name) = sale_find_header(pet_id, breed_id, city, region)

    tmpl = render_template("cat/search.html", header=Markup(header), \
      title=title, form = form, advs = advs, \
      pet = pet_name, pet_id = pet_id, \
      breed = breed_name, breed_id = breed_id, \
      region = region.get("region_name") if region else None,
      region_id = region.get('region_id') if region else None, 
      city = city.get("city_name") if city else None, \
      city_id = city.get("city_id") if city else None, \
      sort = session.get("cat_sort"), \
      count = count, total = total )
    return tmpl


@app.route('/prodazha-sobak/<adv_id>/')
def dog_adv_show(adv_id):
    adv = None
    archived = False
    try:
        adv = db.get_dog_adv(adv_id)
        if not adv:
            adv = db.get_dog_adv_archived(adv_id)
            archived = True
    except InvalidId, e:
        abort(404)
    
    if not adv:
        abort(404)

    name = u"Продам {0} породы {1} в г. {2}".format(
        adv_types.get_adv_type_name(adv.get('adv_type')) or u"собаку",
        breeds.get_breed_name(adv.get("breed_id")).lower(),
        geo.get_city_name(adv.get("city_id"), "i"))

    header = \
    Markup(u"Продам {0} породы {1} в г.&nbsp;{2}".format(
        adv_types.get_adv_type_name(adv.get('adv_type')) or u"собаку",
        breeds.get_breed_name(adv.get("breed_id")).lower(),
        geo.get_city_name(adv.get("city_id"), "i")
    ))
    title = u"{0} за {1}".format(name, \
        u"{0} {1}".format(u"{0:,}".format(adv.get("price")).replace(","," "), morph_word(u"рубль", count=adv.get("price"))))
    seller = db.get_user(adv.get("user_id"))
    return render_template("dog/adv_show.html", \
        header = header,
        title = title,
        adv = adv,
        seller = seller, 
        archived = archived)


@app.route('/prodazha-koshek/<adv_id>/')
def cat_adv_show(adv_id):
    adv = None
    try:
        adv = db.get_cat_adv(adv_id)
    except Exception, e:
        app.logger.warning(e)
    
    if not adv:
        abort(404)

    name = u"Продам кошку породы {0} в г. {1}".format( \
        breeds.get_breed_name(adv.get("breed_id")).lower(),\
        geo.get_city_name(adv.get("city_id"), "i")
    )
    header = Markup(u"Продам кошку породы {0} в г.&nbsp;{1}".format( \
        breeds.get_breed_name(adv.get("breed_id")).lower(),\
        geo.get_city_name(adv.get("city_id"), "i")
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
        app.logger.warning(e)
    
    if not adv:
        abort(404)

    name = u"Продам {0} породы {1} в г. {2}".format( \
        morph_word(get_pet_name(adv.get("pet_id")), {"accs"}).lower(), \
        get_breed_name(adv.get("breed_id"), adv.get("pet_id")).lower(),\
        geo.get_city_name(adv.get("city_id"), "i")
    )
    header = Markup(u"Продам {0} породы {1} в г.&nbsp;{2}".format( \
        morph_word(get_pet_name(adv.get("pet_id")), {"accs"}).lower(), \
        get_breed_name(adv.get("breed_id"), adv.get("pet_id")).lower(),\
        geo.get_city_name(adv.get("city_id"), "i")
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
    return redirect(url_for('account_dog_advs'))


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

@app.route("/unsubscribe/<user_id>/<subscribe_name>/", methods = ["GET"])
def unsubscribe(user_id, subscribe_name):
    subscribe = db.get_subscribe_for_user(user_id)
    title = u"Отписка от рассылки"
    if subscribe:
        form = Subscribe()
        form.load_from_db_entity(subscribe)
        form.set_field_val(subscribe_name, False)
        db.save_subscribe(user_id, form)
        return render_template('unsubscribe_success.html', title = title)
    else:
        return render_template('unsubscribe_failed.html', title = title)


@app.route("/account/subscribe/", methods = ["GET", "POST"])
@login_required
def account_subscribe():
    form = Subscribe(request.form)
    if request.method == "POST":
        if form.validate():
            db.save_subscribe(user_id = current_user.id, subscribe = form)
            flash(u"Подписки успешно обновлены.", "success")
            return redirect(url_for('account_subscribe'))
    else:
        subscribe = db.get_subscribe_for_user(current_user.id)
        if subscribe:
            form.load_from_db_entity(subscribe)
    tmpl = render_template("account/subscribe.html", title=u"Мои подписки", form = form)
    return tmpl

@app.route("/account/profile/", methods = ["GET"])
@login_required
def account_profile():
    user = db.get_user(current_user.id)
    tmpl = render_template("account/profile.html", title=u"Профиль")
    return tmpl

@app.route("/account/profile/edit/", methods = ["GET", "POST"])
@login_required
def account_profile_edit():
    user = db.get_user(current_user.id)
    form = Profile(request.form)
    if request.method == "POST":
        if form.validate():
            db.save_user_contact(current_user.id, form)
            flash(u"Ваш профиль обновлен.", "success")
            return redirect(url_for("account_profile"))
    else:
        for f in form:
            f.set_val(user.get(f.get_db_name()))

    tmpl = render_template("account/profile_edit.html", title=u"Редактирование профиля", form = form)
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
        advs = advs)
    return tmpl


@app.route("/account/dog/")
@login_required
def account_dog_advs():
    advs = db.get_dog_advs_by_user(current_user.id)
    tmpl = render_template("account/dog/advs.html", \
        title=u"Мои объявления о продаже собак", \
        advs = advs)
    return tmpl


@app.route("/account/dog/archived/")
@login_required
def account_dog_advs_archived():
    advs = db.get_dog_advs_archived_by_user(current_user.id)
    tmpl = render_template("account/dog/advs_archived.html", \
        title=u"Архив объявлений о продаже собак", \
        advs = advs)
    return tmpl

@app.route("/account/cat/archived/")
@login_required
def account_cat_advs_archived():
    advs = db.get_cat_advs_archived_by_user(current_user.id)
    tmpl = render_template("account/cat/advs_archived.html", \
        title=u"Архив объявлений о продаже кошек", \
        advs = advs)
    return tmpl


@app.route("/account/cat/archived/<adv_id>/restore/", 
    methods = ['GET', 'POST'])
@login_required
def account_cat_adv_archived_restore(adv_id):
    cat = db.get_cat_adv_archived_for_user(adv_id, current_user.id)
    if not cat:
        abort(404)

    form = Cat(request.form)
    if request.method == "POST":
        if form.validate():
            adv = save_cat_adv(form, adv_id = adv_id)
            db.remove_cat_adv_archived(adv_id, current_user.id) # 
            msg = Markup(u"Объявление <a href='{1}' target='_blank'>&laquo;{0}&raquo;</a> восстановлено и опубликовано.".format(form.title.data, url_for('cat_adv_show', adv_id = adv.get('_id'))))
            flash(msg, "success")
            return render_template("/account/cat/adv_edit_success.html", header=msg, title = u"Объявление '%s' восстановлено" % form.title.data)
    else:
        form.breed.data = breeds.get_breed_name(cat.get("breed_id"))
        form.title.data = cat.get("title")
        form.desc.data = cat.get('desc')
        form.price.data = num(cat.get('price'))
        form.gender.data = str(num(cat.get('gender_id')) or '')
        form.photos.data = ",".join(cat.get("photos"))
        form.city.data = geo.get_city_region(cat.get("city_id"))
        form.phone.data = cat.get("phone") or current_user.phone
        form.skype.data = cat.get("skype") or current_user.skype
    return render_template("/account/cat/adv_edit.html", form=form, title=u"Восстановить объявление о продаже кошки", 
        btn_name_progress = u"Восстанавливается...", 
        btn_name = Markup(u"<i class='fa fa-undo'></i>&ensp;Восстановить"), cat = cat)


@app.route("/account/dog/archived/<adv_id>/restore/", 
    methods = ['GET', 'POST'])
@login_required
def account_dog_adv_archived_restore(adv_id):
    dog = db.get_dog_adv_archived_for_user(adv_id, current_user.id)
    if not dog:
        abort(404)

    form = Dog(request.form)
    if request.method == "POST":
        if form.validate():
            adv = save_dog_adv(form = form, adv_id = adv_id)
            db.remove_dog_adv_archived(adv_id, current_user.id) # remove the old one
            msg = Markup(u"Объявление <a target='_blank' href='%s'>&laquo;%s&raquo;</a> восстановлено и опубликовано." % (url_for('dog_adv_show', adv_id = adv.get('_id')), form.title.data))
            flash(msg, "success")
            return render_template("/account/dog/adv_edit_success.html", header = msg, title = u"Объявление '%s' восстановлено и опубликовано" % form.title.data)
    else:
        for f in form:
            f.set_val(dog.get(f.get_db_name()))
      
        autofill_user_to_adv(form)
        
    return render_template("/account/dog/adv_edit.html", \
        form = form, \
        title = u"Восстановить объявление о продаже собаки", \
        dog = dog, \
        btn_name = Markup(u'<i class="fa fa-undo"></i>&ensp;Восстановить'), \
        btn_name_progress = u'Восстанавливается...', \
        fields = get_fields(form))

def autofill_user_to_adv(form):
    form.username.data = form.username.data or (current_user.username + " " + (current_user.surname or "") if current_user.username != u'Пользователь' else u'')
    form.phone.data = form.phone.data or current_user.phone
    form.skype.data = form.skype.data or current_user.skype
    form.site_link.data = form.site_link.data or current_user.site_link
    # form.kennel_name.data = form.kennel_name.data or current_user.kennel_name


@app.route("/ajax/account/dog/<adv_id>/refresh/", methods = ["GET"])
@login_required
def ajax_account_dog_adv_refresh(adv_id):
    adv = db.refresh_dog_adv(current_user.id, adv_id)
    return jsonify(items = {
        'expire_date': str(adv.get('expire_date').strftime("%Y-%m-%dT%H:%M:%SZ")),
        'update_date' :str(adv.get('update_date').strftime("%Y-%m-%dT%H:%M:%SZ"))
        })


@app.route("/account/dog/<adv_id>/edit/", methods = ['GET', 'POST'])
@login_required
def account_dog_adv_edit(adv_id):
    dog = db.get_dog_adv_for_user(adv_id, current_user.id)
    if not dog:
        abort(404)

    form = Dog(request.form)
    if request.method == "POST":
        if form.validate():
            save_dog_adv(adv_id = adv_id, form = form)
            msg = Markup(u"Объявление <a target='_blank' href='%s'>&laquo;%s&raquo;</a> опубликовано." % (url_for('dog_adv_show', adv_id = adv_id), form.title.data))
            flash(msg, "success")
            return render_template("/account/dog/adv_edit_success.html", header = msg, title = u"Объявление '%s' опубликовано" % form.title.data)
        else:
            print(form.errors)
    else:
        for f in form:
            f.set_val(dog.get(f.get_db_name()))
      
        autofill_user_to_adv(form)
        
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
            adv = save_dog_adv(form)
            msg =  Markup(u"Объявление <a target='_blank' href='%s'>&laquo;%s&raquo;</a> опубликовано." % (url_for('dog_adv_show', adv_id = adv.get('_id')), form.title.data))
            flash(msg, "success")
            return render_template(
                "/account/dog/adv_edit_success.html", header=msg, title = u"Объявление '%s' опубликовано" % form.title.data)
        else:
            print(form.errors)
    else:
        autofill_user_to_adv(form)
        form.city.data = form.city.data or geo.format_city_region_by_city_id(current_user.city_id)

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
    
    adv = db.upsert_dog_adv(user_id = current_user.id, \
        adv_id = adv_id, \
        form  = form, \
        attraction = calc_attraction(form))
    return adv

@app.route("/account/dog/<adv_id>/remove/undo/", methods = ['GET'])
@login_required
def account_dog_adv_remove_undo(adv_id):
    adv = db.undo_remove_dog_adv(adv_id, current_user.id)
    if adv:
        adv_show_url = url_for('dog_adv_show', \
            adv_id = adv.get('_id'))
        flash(Markup(u"Объявление <a target='_blank' href='%s'>&laquo;%s&raquo;</a> вновь опубликовано." % (adv_show_url, adv["title"])), \
            "success")
    return redirect(url_for("account_dog_advs"))

@app.route("/account/dog/<adv_id>/remove/", methods = ['GET'])
@login_required
def account_dog_adv_remove(adv_id):
    adv = db.remove_dog_adv(adv_id, current_user.id)
    if adv:
        undo_url = url_for('account_dog_adv_remove_undo', adv_id = adv.get('_id'))
        flash(Markup(u"Объявление &laquo;%s&raquo; удалено. <a target='_self' title='Восстановить удаленное объявление' href='%s'>Отменить удаление</a>." % (adv["title"], undo_url)), \
            "success")
    return redirect(url_for("account_dog_advs"))



@app.route("/account/dog/archived/<adv_id>/remove/", methods = ['GET'])
@login_required
def account_dog_adv_archived_remove(adv_id):
    adv = db.remove_dog_adv_archived(adv_id, current_user.id)
    if adv:
        flash(Markup(u"Объявление &laquo;%s&raquo; удалено." % adv["title"]), \
            "success")
    return redirect(url_for("account_dog_advs_archived"))


@app.route("/account/cat/archived/<adv_id>/remove/", methods = ['GET'])
@login_required
def account_cat_adv_archived_remove(adv_id):
    adv = db.remove_cat_adv_archived(adv_id, current_user.id)
    if adv:
        flash(Markup(u"Объявление &laquo;%s&raquo; удалено." % adv["title"]), \
            "success")
    return redirect(url_for("account_cat_advs_archived"))

@app.route("/account/dog/<adv_id>/archive/", methods = ['GET'])
@login_required
def account_dog_adv_archive(adv_id):
    adv = db.archive_dog_adv(adv_id, current_user.id)
    if adv:
        flash(Markup(u"Объявление <i>&laquo;%s&raquo;</i> перещено в <a href='%s' target='_self'>архив</a>." % (adv["title"], 
            url_for('account_dog_advs_archived') )), \
            "success")
    return redirect(url_for("account_dog_advs"))


@app.route("/account/cat/<adv_id>/archive/", methods = ['GET'])
@login_required
def account_cat_adv_archive(adv_id):
    adv = db.archive_cat_adv(adv_id, current_user.id)
    if adv:
        flash(Markup(u"Объявление <i>&laquo;%s&raquo;</i> перещено в <a href='%s' target='_self'>архив</a>." % (adv["title"], 
            url_for('account_dog_advs_archived')  )), \
            "success")
    return redirect(url_for("account_cat_advs"))

@app.route("/account/cat/<adv_id>/remove/undo/", methods = ['GET'])
@login_required
def account_cat_adv_remove_undo(adv_id):
    adv = db.undo_remove_cat_adv(adv_id, current_user.id)
    if adv:
        adv_show_url = url_for('cat_adv_show', \
            adv_id = adv.get('_id'))
        flash(Markup(u"Объявление <a target='_blank' href='%s'>&laquo;%s&raquo;</a> вновь опубликовано." % (adv_show_url, adv["title"])), \
            "success")
    return redirect(url_for("account_cat_advs"))

@app.route("/account/cat/<adv_id>/remove/", methods = ['GET'])
@login_required
def account_cat_adv_remove(adv_id):
    adv = db.remove_cat_adv(adv_id, current_user.id)
    if adv:
        undo_url = url_for('account_cat_adv_remove_undo', adv_id = adv.get('_id'))
        flash(Markup(u"Объявление &laquo;%s&raquo; удалено. <a target='_self' title='Восстановить удаленное объявление' href='%s'>Отменить удаление</a>." % (adv["title"], undo_url)), \
            "success")
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
        'breed_id': form.breed.breed_id, \
        'title': form.title.data, \
        'desc': form.desc.data, \
        'photos': filenames, \
        'price' : form.price.data, \
        'update_date' : now, \
        "city_id": form.city.city_id, \
        "region_id" : form.city.region_id, \
        "phone" : form.phone.data, \
        "skype" : form.skype.data, \
        "gender_id": num(form.gender.data),
        "user_id" : str(current_user.id)}

    adv = db.cat_advs.find_and_modify({'_id': ObjectId(adv_id), 
        'user_id' : str(current_user.id)} , 
        {'$set': cat, 
        '$setOnInsert' : {'add_date': now}}, 
        upsert = True, new = True)
    return adv


@app.route("/account/cat/<adv_id>/edit/", methods = ['GET', 'POST'])
@login_required
def account_cat_adv_edit(adv_id):
    cat = db.get_cat_adv_for_user(adv_id, current_user.id)
    if not cat:
        abort(404)

    form = Cat(request.form)
    if request.method == "POST":
        if form.validate():
            adv = save_cat_adv(form, adv_id)
            flash(Markup(u"Объявление <a href='{1}' target='_blank'>&laquo;{0}&raquo;</a> опубликовано.".format(form.title.data, url_for('cat_adv_show', adv_id = adv.get('_id')))), "success")
            return redirect(url_for("account_cat_advs"))
    else:
        form.breed.data = breeds.get_breed_name(cat.get("breed_id"))
        form.title.data = cat.get("title")
        form.desc.data = cat.get('desc')
        form.price.data = num(cat.get('price'))
        form.gender.data = str(num(cat.get('gender_id')) or '')
        form.photos.data = ",".join(cat.get("photos"))
        form.city.data = geo.get_city_region(cat.get("city_id"))
        form.phone.data = cat.get("phone") or current_user.phone
        form.skype.data = cat.get("skype") or current_user.skype
    return render_template("/account/cat/adv_edit.html", form=form, title=u"Редактировать объявление о продаже", btn_name = u"Опубликовать", cat = cat)


@app.route("/account/cat/new/", methods = ['GET', 'POST'])
@login_required
def account_cat_adv_new():
    form = Cat(request.form)
    if request.method == "POST":
        if  form.validate():
            adv = save_cat_adv(form)
            msg =  Markup(u"Объявление <a target='_blank' href='%s'>&laquo;%s&raquo;</a> опубликовано." % (url_for('cat_adv_show', adv_id = adv.get('_id')), form.title.data))
            flash(msg, "success")
            return render_template("/account/cat/adv_edit_success.html", header=msg, title = u"Объявление '%s' опубликовано" % form.title.data)
    else:
        form.city.data = geo.get_city_region(current_user.city_id)
        form.phone.data = current_user.phone
        form.skype.data = current_user.skype
    return render_template("/account/cat/adv_edit.html", form=form, title=u"Новое объявление о продаже кошки")


@app.route("/spravka/")
def help():
    return render_template("/help/index.html", \
        title=u"Справка", header=Markup(u"Справка"))

@app.route("/spravka/privlekatelnost-obyavleniya/")
def help_attraction():
    return render_template("/help/faq_attraction.html", \
        title=u"Привлекательность объявления", header=Markup(u"Привлекательность объявления"))

@app.route("/spravka/preimushhestva-dlja-zavodchikov/")
def help_breeder_benefits():
    return render_template("/help/faq_breeder_benefits.html", \
        title=u"Как мы помогаем продавать ваших собак или кошек?", header=Markup(u"Как мы помогаем продавать ваших собак или кошек?"))

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
        
@app.route('/thumbnail/<filename>')
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
    
@app.route('/photo/<filename>')
def photo(filename):
    height = min(request.args.get('height') or 600, 600)
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
            app.logger.error(e)
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

    if request.method == "POST":
        if form.validate():
            send_from_sale(adv.get("_id"), \
                adv.get('title'), \
                url_for('dog_adv_show', adv_id = adv.get('_id'), _external =True), \
                form.email.data, form.username.data, \
                seller_email, seller_username, \
                (u"Сообщение по объявлению «%s» на Поводочке" % adv.get("title")), \
                form.message.data)
            # if form.sms_alert.data and seller.get('phone') and seller.get('phone_adv_sms'):
            #     send_sms(u"Пользователь сайта Поводочек отправил вам почтовое сообщение.", \
            #         [seller.get('phone')] )
            return render_template("/mail_sent.html", title = u"Сообщение успешно отправлено")
    elif current_user.is_authenticated():
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("/mail.html", form = form, seller_email = seller_email, seller_username = seller_username, title = u"Написать письмо пользователю %s" % seller_username, header=Markup(u"Написать письмо пользователю <small>%s</small>" % seller_username))

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

    if request.method == "POST":
        if form.validate():
            send_from_sale(adv.get('_id'), \
                adv.get('title'), \
                url_for('cat_adv_show', adv_id = adv.get('_id'), _external =True), \
                form.email.data, \
                form.username.data, seller_email, seller_username, \
                (u"Сообщение по объявлению «%s» на Поводочке" % adv.get("title")), \
                form.message.data)
            # if form.sms_alert.data and seller.get('phone') and seller.get('phone_adv_sms'):
            #     send_sms(u"Пользователь сайта Поводочек отправил вам почтовое сообщение.", \
            #         [seller.get('phone')] )
            return render_template("/mail_sent.html", title = u"Сообщение успешно отправлено")
    elif current_user.is_authenticated():
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("/mail.html", form = form, seller_email = seller_email, seller_username = seller_username, title = u"Написать письмо пользователю %s" % seller_username, header=Markup(u"Написать письмо пользователю <small>%s</small>" % seller_username))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'), 
        'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/prodazha-koshek/goroda/')
@app.route('/prodazha-koshek-v-gorodah/')
def cat_advs_by_cities():
    return pet_advs_by_cities(pet_id = pets.CAT_ID) 

@app.route('/prodazha-sobak/goroda/')
@app.route('/prodazha-sobak-v-gorodah/')
def dog_advs_by_cities():
    return pet_advs_by_cities(pet_id = pets.DOG_ID) 

def pet_advs_by_cities(pet_id):
    pet_name = morph_word(pets.get_pet_name(pet_id), ["plur", "gent"]).lower()

    advs = db.get_dog_advs_by_cities() if pet_id == pets.DOG_ID \
        else db.get_cat_advs_by_cities()

    advs_by_cities = [(letter, list(group)) for letter, group in groupby(advs, lambda adv : adv['city_name'][0])]

    return render_template("/advs_by_cities.html", \
        title=u"Объявления о продаже {0} в городах России".format(pet_name), \
        advs_by_cities = advs_by_cities, \
        pet_id = pet_id, \
        pet_name = pet_name)


@app.route('/prodazha-koshek/oblasti/')
@app.route('/prodazha-koshek-v-oblastjah/')
def cat_advs_by_regions():
    return pet_advs_by_regions(pet_id = pets.CAT_ID) 

@app.route('/prodazha-sobak/oblasti/')
@app.route('/prodazha-sobak-v-oblastjah/')
def dog_advs_by_regions():
    return pet_advs_by_regions(pet_id = pets.DOG_ID) 

def pet_advs_by_regions(pet_id):
    pet_name = morph_word(pets.get_pet_name(pet_id), ["plur", "gent"]).lower()

    advs = db.get_dog_advs_by_regions() if pet_id == pets.DOG_ID \
        else db.get_cat_advs_by_regions()

    advs_by_regions = [(letter, list(group)) for letter, group in groupby(advs, lambda adv : adv['region_name'][0])]

    return render_template("/advs_by_regions.html", \
        title=u"Объявления о продаже {0} в областях России".format(pet_name), \
        advs_by_regions = advs_by_regions, \
        pet_id = pet_id, \
        pet_name = pet_name)


@app.route('/tos/')
def tos():
    return render_template("/tos.html", title = u"Пользовательское соглашение")

@app.route('/kontakty/')
def contacts():
    return render_template("/contacts.html", \
        title=u"Контактная информация")


@app.route('/news/<news_id>/', methods = ["GET"])
def news_view(news_id):
    news = db.get_news_by_id(news_id)
    if not news:
        abort(404)

    return render_template('/news/news_view.html', title = Markup(news.get('subject')), news = news, form = Comment(request.form))


@app.route('/news/<news_id>/comment/', methods = ["POST", "GET"])
@login_required
def news_view_comment(news_id):
    news = db.get_news_by_id(news_id)
    if not news:
        abort(404)

    if request.method == "POST":
        form = Comment(request.form)
        if form.validate():
            news = db.comment_news(news_id = news_id, 
                levels = form.levels.data,
                text = form.text.data, 
                author_id = current_user.id)
        
        comment_levels = "_".join([str(level) for level in form.levels.data])
        anchor = "comment_%s" % (
            comment_levels or len(news.get("comments") or ['']) - 1 )
    else:
        anchor = "comment_%s" % len(news.get("comments") or ['']) - 1
    return redirect(url_for('news_view', news_id = news_id, _anchor =  anchor ))

    # return render_template('/news/news_view.html', title = Markup(news.get('subject')), news = news, form = form)
    

@app.route('/news/')
def news():
    news_feed = db.get_news_all()
    total = news_feed.count()
    perpage = 10
    return render_template('/news/index.html', title = Markup(u"Новости проекта"), news_feed = news_feed, total = total, perpage = perpage)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title = u"Запрашиваемая вами страница не найдена"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', title = u"На нашем сервере произошла ошибка"), 500

# admin

from functools import wraps

def admin_requried(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated() or current_user.email not in app.config["ADMIN_EMAILS"]:
            abort(401)
        return func(*args, **kwargs)
    return decorated_view


@app.route('/admin/user/')
@admin_requried
def admin_user():
    page = int(request.args.get("page") or 1)
    total = db.users.count()
    perpage = 1000
    u = [user for user in db.admin_get_users(perpage, \
        (page - 1) * perpage)]

    return render_template('/admin/user.html', title = Markup(u"Админка: пользователи &mdash; %s" % total), users = u, total = total, perpage = perpage, page = page)

@app.route('/admin/sale/')
@admin_requried
def admin_sale():
    page = int(request.args.get("page") or 1)
    total = sales().count()
    perpage = 100
    advs = [adv for adv in sales().find(sort = [('update_date', DESCENDING)], limit = perpage, skip = (page - 1) * perpage)]
    for seller in users.find({'_id':{'$in' : [ObjectId(adv.get('user_id')) for adv in advs if adv.get('user_id') ]}}):
        for adv in [adv for adv in advs if not adv.get('email')]:
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
        flash(u"Объявление &laquo;%s&raquo; добавлено." % form.title.data, "info")
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
        if form.validate():
            sale_save(form, adv_id, moderator = current_user)
            flash(u"Объявление &laquo;%s&raquo; обновлено." % form.title.data, "info")
            return redirect(url_for("admin_sale"))
    else:
        form.breed.data = get_breed_name(adv.get("breed_id"), adv.get("pet_id"))
        form.title.data = adv.get("title")
        form.desc.data = adv.get('desc')
        form.price.data = num(adv.get('price'))
        form.gender.data = str(num(adv.get('gender_id')) or '')
        form.photos.data = ",".join(adv.get("photos"))
        form.city.data = geo.get_city_region(adv.get("city_id"))
        # form.age.data = str(num(adv.get("age_id")))
        form.phone.data = adv.get("phone")
        form.skype.data = adv.get("skype")
        form.email.data = adv.get("email")
        form.username.data = adv.get("username")
    return render_template("/admin/sale_edit.html", form = form, title=u"Админка: редактировать объявление о продаже", btn_name = u"Сохранить", adv = adv)

@app.route('/admin/news/new/', methods = ["POST", "GET"])
@admin_requried
def admin_news_new():
    form = AdminNews(request.form)
    if request.method == "POST" and form.validate():
        news = save_news(news_id = None, form = form)
        flash(u'Новость "%s" сохранена' % news.get('subject'), "success")
        return redirect(url_for('admin_news'))
    else:
        return render_template('/admin/news_edit.html', title = Markup(u"Админка: публикация новости"), form = form)

@app.route('/admin/news/<news_id>/edit/', methods = ["POST", "GET"])
@admin_requried
def admin_news_edit(news_id):

    news = db.get_news_by_id(news_id)
    if not news:
        abort(404)

    form = AdminNews(request.form)
    if request.method == "POST":
        if form.validate():
            news = save_news(news_id = news_id, form = form)
            flash(u'Новость "%s" сохранена' % news.get('subject'), "success")
            return redirect(url_for('admin_news'))
    else:
        form.load_from_db_entity(news)
    return render_template('/admin/news_edit.html', title = Markup(u"Админка: Редактирование новости"), form = form)

def save_news(news_id, form):
    news = db.upsert_news(news_id = news_id, 
                subject = form.subject.data, 
                message = form.message.data, 
                published = form.published.data, 
                summary = form.summary.data, 
                publish_date = form.publish_date.data)        
    if form.email_single.data:
        user = db.get_user_by_email(form.email_single.data)
        mailer.notify_user_of_news(user, news)
    if form.email_everyone.data:
        mailer.notify_users_of_news(db.get_users_activated(), news)
    return news

@app.route('/admin/news/')
@admin_requried
def admin_news():
    news_feed = db.get_news_all()
    total = news_feed.count()
    perpage = 1000
    return render_template('/admin/news.html', title = Markup(u"Админка: новости"), news_feed = news_feed, total = total, perpage = perpage)

@app.route('/admin/news/<news_id>/remove/')
@admin_requried
def admin_news_remove(news_id):
    db.remove_news(news_id)
    flash(u"Новость '%s' удалена." % news_id, 'success')
    return redirect(url_for('admin_news'))
    
@app.route('/test/parser/avito/')
def test_parser_avito():
    response = make_response(render_template('/test/parser_avito.html', title = u"Parsing from avito"))
    response.headers['Access-Control-Allow-Origin'] = "*"
    return response


@app.route('/sitemap.xml')
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])


def get_pet_advs_for_mosaic(skip, limit = 10, pet_id = pets.DOG_ID):
    if pet_id == pets.DOG_ID:
        return [{"src":url_for('thumbnail', \
            filename = adv.get('photos')[0], width= 300), \
        'url' : url_for('dog_adv_show', adv_id = adv.get('_id')), \
        'id': str(adv.get('_id')), \
        'p' : adv.get('price'), \
        'b' : breeds.get_breed_name(adv.get('breed_id')), \
        's' : {'h':100, 'w':150}, 
        't' : Markup.escape(adv.get('title'))}
        for adv in db.get_dog_advs_for_mosaic(skip, limit)]
    elif pet_id == pets.CAT_ID:
        return  [{"src":url_for('thumbnail', \
            filename = adv.get('photos')[0], width= 300), \
        'url' : url_for('cat_adv_show', adv_id = adv.get('_id')), \
        'id': str(adv.get('_id')), \
        'p' : adv.get('price'), \
        'b' : breeds.get_breed_name(adv.get('breed_id')), \
        's' : {'h':100, 'w':150}, 
        't' : adv.get('title')}
        for adv in db.get_cat_advs_for_mosaic(skip, limit)]
    else:
       return None

@app.route("/ajax/mosaic/showmore/<int:pet>/", methods = ["GET"], defaults= {"limit":10, 'skip': 0})
@app.route("/ajax/mosaic/showmore/<int:pet>/<int:skip>/", methods = ["GET"], defaults= {"limit":10})
@app.route("/ajax/mosaic/showmore/<int:pet>/<int:skip>/<int:limit>/", methods = ["GET"])
def ajax_mosaic_showmore(pet, skip, limit):
    advs = get_pet_advs_for_mosaic(skip, limit = limit, pet_id = pet)
    return jsonify(advs = advs)

@app.route("/ajax/main/fresh/dog/", methods = ["GET"])
def ajax_main_fresh_dog():
    fresh_advs = db.get_dog_advs_for_fresh(0, 12)
    return render_template("main/fresh.html", advs = fresh_advs, pet = pets.DOG_ID)

@app.route("/ajax/main/fresh/cat/", methods = ["GET"])
def ajax_main_fresh_cat():
    fresh_advs = db.get_cat_advs_for_fresh(0, 12)
    return render_template("main/fresh.html", advs = fresh_advs, pet = pets.CAT_ID)

@app.route("/ajax/main/news/", methods = ["GET"])
def ajax_main_news():
    news_feed = db.get_news_all(limit = 5, published = True)
    return render_template("main/news.html", news_feed = news_feed)

@app.route("/ajax/main/popular/breed/dog/", methods = ["GET"])
def ajax_main_popular_breed_dog():
    breed_rating = db.get_dog_breeds_rating(limit = 10)
    return render_template("main/popular.html", breed_rating = breed_rating)

@app.route("/ajax/metro/stations/", methods = ["GET"])
def ajax_metro_stations():
    stations = None
    city_name = request.args.get("city_name")
    city = db.get_city_by_name(city_name)
    if city:
        stations = metro.get_stations_by_city(city.get('geo_id'))

    if stations:
        stations = sorted(stations.values())

    return jsonify(stations = stations)




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
