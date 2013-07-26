#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, flash, redirect, url_for, session, send_from_directory, send_file, abort, jsonify, Markup, make_response)
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

from wtforms import (Form, BooleanField, TextField, PasswordField, validators)
from forms import (SignUp, SignIn, Sale, Contact, Activate,ResetPassword, ChangePassword, SaleSearch, get_city_by_city_and_region, SendMail, ChangeEmail)
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.son import SON
from gridfs import GridFS
from werkzeug.datastructures import MultiDict, ImmutableMultiDict

from werkzeug.utils import secure_filename
import os
from uuid import uuid4, uuid1
from datetime import datetime, date, timedelta
import time
import re
import base64
from sys import maxint

from flaskext.uploads import (UploadSet, configure_uploads, IMAGES,
                              UploadNotAllowed)

from security import hash_password, check_password

from flask_mail import (Mail, Message)
from threading import Thread
from momentjs import MomentJS
from pymorphy2 import MorphAnalyzer
from helpers import (num, create_thumbnail, get_thumbnail_filename, resize_image, save_photo, get_photo, get_photo_size, qoute_rus)

from smsgate import send_sms

from dic.ages import ages
from dic.genders import genders
from dic.pets import pets, get_pet_name


morph = MorphAnalyzer()

# from pymorphy import 

photos = UploadSet('photos', IMAGES)

db = MongoClient()['povodochek']

def users():
    return db.users

def sales():
    return db.sales


def breeds():
    return db.breeds

def cities():
    return db.cities
    # return cities.cities

class User(UserMixin):
    def __init__(self, login, id, active = True, username = None, email = None, new_email = None):
        self.name = login
        self.username = username
        self.id = id
        self.active = active
        self.email = email
        self.new_email = new_email

    def is_signed(self):
        return True

    def is_active(self):
        return True


class Anonymous(AnonymousUser):
    name = u"Anonymous"
    username = u""
    email = u""

    def is_signed(self):
        return False

app = Flask(__name__)

config = os.path.join(app.root_path, 'config.py')
app.config.from_pyfile(config)

mail = Mail(app)

configure_uploads(app, (photos))

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "/signin"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

login_manager.setup_app(app)

# jinja custom filters

app.jinja_env.globals['momentjs'] = MomentJS

def jinja_format_datetime(value, format='%H:%M, %d.%m.%y'):
    return value.strftime(format) if value  else ""

app.jinja_env.filters['format_datetime'] = jinja_format_datetime

def jinja_date(value):
    return datetime.date(value) if value else ""

app.jinja_env.filters['date'] = jinja_date

def jinja_format_price(value, template=u"{0:,}"):
    return Markup((template.format(value) if value else u"").replace(u",", u"&nbsp;"))

app.jinja_env.filters['format_price'] = jinja_format_price

def jinja_format(value, template=u"{0}"):
    return template.format(value)

app.jinja_env.filters['format'] = jinja_format

app.jinja_env.filters['pet_name'] = get_pet_name

# todo: add caching layer
def get_breed_name(breed_id):
    breed = breeds().find_one({"id": num(breed_id)}) if breed_id else None
    return breed.get("name") if breed else u""

app.jinja_env.filters['breed_name'] = get_breed_name

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

# todo: add caching layer 
def get_city_region(city_id):
    city = cities().find_one({"id": num(city_id)}, fields=["city_region"]) if city_id else None
    return city.get("city_region") if city else u""

app.jinja_env.filters['city_region'] = get_city_region


def get_city_name(city_id):
    city_name = None
    city = cities().find_one({"id": num(city_id)}, fields=["city_name"]) if city_id else None
    return city.get("city_name") if city else u""

app.jinja_env.filters['city_name'] = get_city_name

def morph_restore_register(morphed_word, word):
    """ Восстановить регистр слова """
    if '-' in word:
        parts = zip(morphed_word.split('-'), word.split('-'))
        return '-'.join(morph_restore_register(*p) for p in parts)
    if word.isupper():
        return morphed_word.upper()
    elif word.islower():
        return morphed_word.lower()
    elif word.istitle():
        return morphed_word.title()
    else:
        return morphed_word.lower()

def morph_word(word, grammemes = None, count = None):
    morphed_word = word
    if word:
        parts = re.findall(u"[а-яА-Я-]+", word, re.U | re.I)
        for part in filter(lambda x: len(x) > 2, parts):
            parse = morph.parse(part)
            morphed_part = part
            if grammemes:
                grammemes = set(grammemes)
                inflect_word = parse[0].inflect(grammemes) if parse[0] else None
                morphed_part = inflect_word.word if inflect_word else part
            elif count >= 0:
                morphed_part = parse[0].make_agree_with_number(count).word if parse[0] else part
            morphed_part = morph_restore_register(morphed_part, part)
            morphed_word = morphed_word.replace(part, morphed_part)
    return morphed_word

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

def jinja_shorten_mongoid(id):
    return int(time.mktime(id.generation_time.timetuple()))

app.jinja_env.filters['shorten_mongoid'] = jinja_shorten_mongoid

def jinja_utcnow():
    return datetime.utcnow()

app.jinja_env.globals['utcnow'] = jinja_utcnow

def debug_write(msg):
    print("DEBUG INFO: %s" % msg)

@login_manager.user_loader
def load_user(id):
    # print("user id = %s" % str(id))
    user = users().find_one({'_id':ObjectId(id)})
    return User(user.get('login'), user.get("_id"), active = user.get("activated"), username = user.get("username"), email = user.get("email"), new_email = user.get("new_email")  ) if user else Anonymous

@app.route("/")
def index():
    advs = get_sales_for_index(0, 40)
    tmpl = render_template('index5.html', \
        pet_search_form = SaleSearch(), \
        title = u"Продажа породистых собак и кошек", advs = [adv for adv in advs])
    return tmpl

@app.route("/signin/", methods = ["POST", "GET"])
def signin():
    form = SignIn(request.form)
    form.password.description = Markup(u"<a class='' href='%s'>Напомнить пароль</a>" % (url_for("reset_password")))
    if request.method == "POST" and form.validate():
        (login, password, remember) = (form.login.data, form.password.data, form.remember.data)
        user = users().find_one({'login': login})
        if user and check_password(user.get("pwd_hash"), password):
            if True or user.get("activated"):
                if login_user(User(login, user["_id"]), remember=remember):
                    return redirect(request.args.get("next") or url_for("account_sale"))
                else:
                    flash(u"Извините, но вы не можете войти.", "error")
            else:
                print('disactivated')
                flash(Markup(u"Вы не можете войти на сайт, так как регистрация не подтверждена. Проверьте, пожалуйста, электронную почту или отправьте <a target='_blank' href='{0}'>ссылку на активацию</a> повторно.".format(url_for('activate', confirm=''))), "error")
        else:
            flash(u"Неправильный логин или пароль.", "error")
    return render_template("signin.html", form=form, title=u"Вход на сайт")

@app.route("/ajax/location/prefetch.json", methods = ["GET"])
def ajax_location_prefetch():
    locations = [ city.get("city_name") for city in cities().find(fields=["city_name"])]
    return jsonify(items = locations ) 

@app.route("/ajax/location/typeahead/", methods = ["GET"])
def ajax_location_typeahead():
    # print(str(request.args.get("query")))
    query = (request.args.get("query") or u"").strip()
    limit = int(request.args.get("limit") or 8)
    matcher = re.compile("^" + re.escape(query), re.IGNORECASE)
    locations = [ city.get("city_region") \
        for city in cities().find({'city_region': {"$regex": matcher}}, limit=limit, fields=["city_region"])]
    return jsonify(items = locations )    


def get_sales_for_index(skip, limit = 50, pet_id = None):
    query = {"photos": {"$nin": [None, []]} }
    if pet_id:
        query["pet_id"] = pet_id
    advs = [{"src":url_for('photo', \
            filename = adv.get('photos')[0], width= 300), \
        'url' : url_for('sale_show', id = adv.get('_id')), \
        't' : adv.get('title'), \
        'id': str(adv.get('_id')),
        's': get_photo_size(db, adv.get('photos')[0], width = 300) } 
        for adv in sales().find(
            query, \
            skip = skip, \
            fields = ["_id", "photos", "title"], \
            limit = limit, \
            sort = [('update_date', -1)]) ]
    return advs


@app.route("/ajax/sales/showmore/<int:pet>/", methods = ["GET"], defaults= {"limit":30, "pet": None, 'skip': 0})
@app.route("/ajax/sales/showmore/<int:pet>/<int:skip>/", methods = ["GET"], defaults= {"limit":30, "pet": None})
@app.route("/ajax/sales/showmore/<int:pet>/<int:skip>/<int:limit>/", methods = ["GET"])
def ajax_sales_showmore(skip, limit, pet):
    advs = get_sales_for_index(skip, limit = limit, pet_id = pet)
    return jsonify(advs = advs)

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

def send_from_sale(email, username, sale_id, seller, subject, message):
    adv = sales().find_one(ObjectId(sale_id))
    if adv and seller and seller.get('email'):
        msg = Message(subject, recipients=[seller.get('email')], cc = [email])
        msg.html = render_template("email/from_sale.html", \
            subject = subject, \
            message = message, \
            adv = adv, \
            seller = seller, \
            email = email, \
            username = username, \
            date = datetime.now().date())
        mail.send(msg)

    
@app.route("/test/email/from_sale")
def test_email_from_sale():
    msg = Message(u"Сообщение от %s сайта Поводочек" % (u'пользователя' if current_user.is_signed() else u'гостя'), \
        recipients=["popovegor@gmail.com"])
    adv = sales().find(limit=1)[0]
    msg.html = render_template("email/from_sale.html", \
        subject = u"Сообщение от пользователя сайта Поводочек", \
        message = u"Некоторое тестовое сообщение.", \
        adv = adv, \
        username = u'Егор Попов АТИ', \
        email = u'popovegor@gmail.com', \
        seller = users().find_one(ObjectId(adv.get('user'))), \
        date = datetime.now().date())
    # mail.send(msg)
    return msg.html

@app.route("/activate/", defaults={'confirm': None}, methods=["GET", "POST"])
@app.route("/activate/<confirm>", methods = ["GET", "POST"])
def activate(confirm):
    form = Activate(request.form)
    if request.method == "POST":
        if form.validate():
            email = form.email.data
            user = users().find_one({"email": email})
            if user:
                new_confirm = str(uuid4()) 
                users().update({'_id': user['_id']}, {"$set": {"confirm": new_confirm}})
                send_activate(email, new_confirm)
                flash(u"Ссылка на активацию регистрации успешно отправлена. Проверьте электронную почту '%s', чтобы подтвердить регистрацию." %email, "info")
        return render_template("activate.html", form = form, title = u"Активация регистрации")
    else:
        user = users().find_one({'confirm': confirm})
        if user:
            users().update({'_id': user['_id']}, {"$set": {"activated": True, "activate_date" : datetime.utcnow(), "confirm" : ''}})
        return render_template("activate.html", user = user, form = form, title = u"Активация регистрации")


@app.route("/asignin/<asign>/", methods = ["GET"])
def asignin(asign):
    user = users().find_one({'asign': asign})
    if user:
        users().update({'_id': user["_id"]}, \
            {"$set": {'asign': '', 'pwd_hash': user['asign_pwd_hash'], 'asign_pwd_hash': ''} })
        if login_user(User(user.get("login"), user.get("_id"))):
            flash(u"Новый пароль был успешно активирован", "info")
            return redirect(url_for("account_change_password"))
    flash(u"Не удалось выполнить автоматический вход на сайт под новым паролем, обратитесь в техподдержку сайта или попробуйте выслать ссылку на смену пароля еще раз.", "error")
    return redirect(url_for("index"))

@app.route("/account/change-password/", methods = ["GET", "POST"])
@login_required
def account_change_password():
    form = ChangePassword(request.form)
    form.current_user = current_user
    if request.method == "POST" and form.validate():
        users().find_and_modify({"_id": ObjectId(current_user.id)}, \
            {"$set": {"pwd_hash": hash_password(form.new_password.data)}})
        flash(u"Пароль успешно изменен.", "info")
    return render_template("account/change_password.html", title=u"Смена пароля", form = form)


@app.route("/account/confirm-email/<base64_email>/")
@login_required
def account_confirm_email(base64_email):
    new_email = base64.b64decode(base64_email)
    if new_email and current_user.new_email == new_email:
        users().update({"_id": ObjectId(current_user.id)}, {"$set": {'new_email': None, "email": new_email}})
        flash(u"Новый почтовый адрес подтвержден.", "info")
    else:
        flash(u"Новый почтовый адрес не удалось подтвердить!", "error")
    return redirect(url_for('account_change_email'))


@app.route("/account/change-email/", methods = ["GET", "POST"])
@login_required
def account_change_email():
    form = ChangeEmail(request.form)
    form.current_user = current_user
    if request.method == "POST" and form.validate():
        users().find_and_modify({"_id": ObjectId(current_user.id)}, \
            {"$set": {"new_email": form.new_email.data}})
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
def signup():
    form = SignUp(request.form)
    if request.method == "POST" and form.validate():
        (login, email, password, confirm, username) = (form.login.data, form.email.data, form.password.data, str(uuid4()), form.username.data)
        print(login, email, password)
        user_id = users().insert({'login': login, 'email': email, 'pwd_hash': hash_password(password), 'username': username, 'confirm': confirm, 'activated': False, 'signup_date': datetime.utcnow()})
        send_signup(username, login, email, password, confirm)
        flash(u"Для того чтобы подтвердить регистрацию, перейдите по ссылке в отправленном Вам письме.", "info")
        if login_user(User(login, user_id), remember = True):
            print(login)
            return redirect(request.args.get('next') or url_for('account_contact'))
        else:
            return redirect(url_for('signin'))
    return render_template('signup.html', form=form, title=u"Регистрация")

@app.route("/reset-password/", methods = ["GET", "POST"])
def reset_password():
    form = ResetPassword(request.form)
    if request.method == "POST" and form.validate():
        email_or_login = form.email_or_login.data
        password = str(hash(str(uuid1())) % 10000000)
        asign = str(uuid4())
        user = users().find_and_modify({'$or' : [{'email': email_or_login}, {'login': email_or_login}]}, \
            {"$set": {'asign_pwd_hash': hash_password(password), 'asign': asign}})
        if user:
            send_reset_password(user.get('email'), user.get("login"), asign, password)
            flash(u"Ссылка на смену пароля была успешна отправлена на электронную почту '%s'" %user.get('email') , "info")
    return render_template("reset_password.html", title=u"Сброс пароля", form = form)

@app.route("/signout/")
@login_required
def signout():
    logout_user()
    url = request.args.get("url")
    return redirect( url if url else url_for('index'))


def cities_near(city = None, distance = None):
    cities = []
    if city and distance and city.get("location"):
        location = city.get("location")
        geoNear = db.command(SON([("geoNear",  "cities"), ("near", location) ,( "spherical", True ), ("maxDistance", distance * 1000), ("limit", 5000)]))
        cities = [(geo["obj"], geo["dis"]) for geo in geoNear.get("results")]
    return cities


def sale_find(pet_id = None, gender_id = None, age_id=None, breed_id = None, city = None, distance = None, photo = False, price_from = None, price_to = None, sort = None, skip = None, limit = None):

    _filter = {}
    extend_filter = lambda k,v: _filter.update({k:v}) if v else None
    extend_filter("pet_id", num(pet_id))
    extend_filter("gender_id", num(gender_id))
    extend_filter("age_id", num(age_id))
    extend_filter("breed_id", num(breed_id))

    price_form = num(price_from)
    price_to = num(price_to)
    if price_from or price_to:
        extend_filter("price", \
            {"$gte" : price_from if price_from > 0 else 0,\
             "$lt" : price_to if price_to else maxint })
    near_cities = []
    if city and distance:
        near_cities = cities_near(city, distance)
        extend_filter("city_id", {"$in": [city.get("id") for city, dis in near_cities]})

    if photo:
        extend_filter("photos", {"$nin": [None, []]})
    sortby = [("update_date", -1)]
    if sort == 1:
        sortby = [("price", -1)]
    elif sort == 2:
        sortby = [("price", 1)]
    else:
        sortby = [("update_date", -1)]
    print("filter %s" % _filter)
    print("sort %s" % sortby)
    print(limit)
    total = sales().count()
    query = sales().find(SON(_filter),\
        limit = limit or total,\
        skip = skip or 0,\
        sort = sortby)
    count = query.count()
    advs = [adv for adv in query]

    if near_cities:
        for adv in advs:
            adv_city_id = adv.get("city_id")
            (near_city, dist) = next( ((city, dist) for city, dist in near_cities if city["id"] == adv_city_id), (None, None))
            adv["distance"] = int(round(dist / 1000, 0))

    return (advs, count, total)


def sale_find_header(form):
    # generate title
    header = u"Купить <span class='muted'>(продают)</span> {0}{1}{2}"
    title = u"Купить {0}{1}{3}: Продажа {2}{1}{3}"
    pet = u"собаку или кошку"
    (pet_id, breed_id) = form.breed.data.split('_') if form.breed.data and len(form.breed.data.split("_")) > 1 else (None, None)

    if (pet_id or form.pet.data) == "1":
        pet = u"собаку/щенка"
    elif (pet_id or form.pet.data) == "2":
        pet = u"кошку/котенка"

    breed = get_breed_name(breed_id)
    if breed:
        # breed = u" {0}".format(morph_word(breed, {"gent"}).lower())
        breed = Markup(u" породы {0}".format(breed).lower())

    city = get_city_name(form.city.city_id) if form.city.city_id else u''
    if city:
        city = u" в {0}".format(morph_word(city, ["loct", "sing"]) )
        # if form.distance.data:
            # city = u"{0}(+ {1} км)".format(city, form.distance.data) 

    return (header.format(pet, breed, city), title.format(pet, breed, morph_word(pet, {"gent", "plur"}), city), pet, breed) 


@app.route("/kupit-sobaku/")
def kupit_sobaku():
    form = SaleSearch()
    args = MultiDict([(form.pet.name, 1)] + [(name, value) for name, value in request.args.iteritems()])
    form = SaleSearch(args)
    return sale(form)

@app.route("/kupit-koshku/")
def kupit_koshku():
    form = SaleSearch()
    args = MultiDict([(form.pet.name, 2)] + [(name, value) for name, value in request.args.iteritems()])
    form = SaleSearch(args)
    return sale(form)

@app.route("/kupit-sobaku-koshku/")
def kupit_sobaku_koshku():
    return sale()

@app.route("/sale/")
def sale(sale_search_form = None):
    form = sale_search_form or SaleSearch(request.args)
    city = get_city_by_city_and_region(form.city.data)
    form.city.city_id = city["id"] if city else None
    (pet_id, breed_id) = form.breed.data.split("_") if form.breed.data and len(form.breed.data.split("_")) > 1 else (None, None)

    # sort
    print(form.price_from.data, form.price_to.data)
    session["sale_sort"] = form.sort.data or session.get("sale_sort") or 3
    
    (advs, count, total) = sale_find(pet_id = pet_id or form.pet.data, \
        breed_id = breed_id, \
        age_id = form.age.data, \
        gender_id = form.gender.data, \
        city = city, \
        distance = form.distance.data, \
        photo = form.photo.data, \
        price_from = form.price_from.data  * 1000, \
        price_to = (form.price_to.data if num(form.price_to.data) < 100 else 0) * 1000,\
        sort = session.get("sale_sort"),
        skip = (form.page.data - 1) * form.perpage.data, \
        limit = form.perpage.data
        )

    (header, title, pet_name, breed_name) = sale_find_header(form)

    tmpl = render_template("sale.html", header=Markup(header), \
      title=title, form= form, advs = advs, \
      pet = pet_name, breed = breed_name, \
      sort = session.get("sale_sort"), \
      count = count, total = total )
    return tmpl


@app.route('/sale/<id>/')
def sale_show(id):
    adv = sales().find_one({'_id': ObjectId(id)}) if id else None
    name = u"Продам {0} породы {1} в {2}".format( \
        morph_word(get_pet_name(adv.get("pet_id")), {"accs"}).lower(), \
        get_breed_name(adv.get("breed_id")).lower(),\
        morph_word(get_city_name(adv.get("city_id")), {"loct"})
     )
    header =  Markup(u"{0} &#8212; {1}".format(name, \
        u"<abbr class='price' title='Цена'>{0}&nbsp;{1}</abbr>".format(jinja_format_price(adv.get("price")), morph_word(u"рубль", count=adv.get("price"))))) 
    title = u"{0} - {1}".format(name, \
        u"{0} {1}".format(u"{0:,}".format(adv.get("price")).replace(","," "), morph_word(u"рубль", count=adv.get("price"))))
    seller = users().find_one(ObjectId(adv.get("user")))
    return render_template("sale_show.html", \
        header = name,
        title = title,
        adv = adv,
        seller = seller)



@app.route("/account/")
@login_required
def account():
    tmpl = render_template("account/sale.html", title=u"Кабинет")
    return tmpl


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


def get_city_and_region(city_id):
    city = cities().find_one({'id': city_id})
    return city["city_region"] if city else ""

@app.route("/account/contact/", methods = ["GET", "POST"])
@login_required
def account_contact():
    user = users().find_one(current_user.id)
    form = Contact(request.form)
    if request.method == "POST":
        if form.validate():
            users().update({"_id": current_user.id}, {"$set":
                {"username": form.username.data, \
                "city_id": form.city.city_id, \
                "phone": form.phone.data, \
                "phone_adv_sms" : form.phone_adv_sms.data if form.phone.data else None, \
                "phone_adv_hide": form.phone_adv_hide.data if form.phone.data else None, \
                'skype' : form.skype.data, \
                'skype_adv_hide': form.skype_adv_hide.data if form.skype.data else None, \
                'city_adv_hide': form.city_adv_hide.data if form.city.data else None}})
            flash(u"Контактная информация обновлена.", "info")
            return redirect(url_for("account_contact"))
    else:
        form.city.data = get_city_and_region(user.get("city_id"))
        form.city_adv_hide.data = user.get("city_adv_hide")
        form.username.data = user.get("username")
        form.phone.data = user.get("phone") 
        form.phone_adv_hide.data = user.get("phone_adv_hide")
        form.phone_adv_sms.data = user.get("phone_adv_sms")
        form.skype.data = user.get("skype")
        form.skype_adv_hide.data = user.get("skype_adv_hide")

    tmpl = render_template("account/contact.html", title=u"Контактная информация", form = form)
    return tmpl

@app.route("/account/adoption/")
@login_required
def account_adoption():
    tmpl = render_template("account/adoption.html", title=u"Отдам даром")
    return tmpl


@app.route("/account/sale/")
@login_required
def account_sale():
    sort = lambda adv: adv.get("update_date") or adv.get("add_date")
    advs = sales().find(
        {'user': {'$in' : [str(current_user.id), current_user.id]} },\
        sort = [("update_date", -1)])

    tmpl = render_template("account/sale.html", \
        title=u"Мои объявления о продаже", \
        advs = [dict(adv, **{'active_date': adv.get('update_date') + timedelta(days=14)}) for adv in advs])
    return tmpl


def sale_save(form, id = None):
    filenames = []
    if form.photos.data:
        filenames = form.photos.data.split(',')
        filenames = filter(lambda x: x and len(x) > 0, filenames)
        for filename in filenames:
            if os.path.exists(photos.path(filename)):
                with open(photos.path(filename)) as file:
                    save_photo(db, file)

    (pet_id, breed_id) = form.breed.data.split("_")
    now = datetime.utcnow()
    sale = {'user': str(current_user.id), 'pet_id': num(pet_id), 'breed_id': num(breed_id), 'title':form.title.data, 'desc': form.desc.data, 'photos': filenames, 'price': form.price.data, 'gender_id': num(form.gender.data), 'update_date':now, "city_id": form.city.city_id, 'age_id': num(form.age.data)}
    if id:
        sales().update(
            {'_id': ObjectId(id), 'user': {'$in': [current_user.id, str(current_user.id)]} } 
            , {'$set': sale}, upsert=True)
    else:
        sale["add_date"] = now
        id = sales().insert(sale)
    return id

@app.route("/account/sale/<id>/extend", methods = ['GET'])
@login_required
def account_sale_extend(id):
    adv = sales().find_one(
        {'_id': {'$in':[id, ObjectId(id)]}, 
        'user': {'$in': [current_user.id, str(current_user.id)]}})
    if adv:
        sales().update({"_id": adv["_id"]}, {"$set": {"update_date": datetime.utcnow()}})
        flash(u"Объявление '%s' продлено на две недели." % adv["title"], "info")
    return redirect(url_for("account_sale"))



@app.route("/account/sale/<id>/remove", methods = ['GET'])
@login_required
def account_sale_remove(id):
    adv = sales().find_one(
        {'_id': {'$in':[id, ObjectId(id)]}, 
        'user': {'$in': [current_user.id, str(current_user.id)]}})
    if adv:
        # sales().remove({"_id": adv["_id"]  })
        flash(u"Объявление '%s' удалено." % adv["title"], "info")
    return redirect(url_for("account_sale"))
    

@app.route("/account/sale/<id>", methods = ['GET', 'POST'])
@login_required
def account_sale_edit(id):
    adv = sales().find_one(
        {'_id': {'$in':[id, ObjectId(id)]}, 
        'user': {'$in': [current_user.id, str(current_user.id)]}})
    if not adv:
        abort(404)

    form = Sale(request.form)
    if request.method == "POST":
        print(form.price.data)
        if form.validate():
            print(form.city.city_id)
            sale_save(form, id)
            flash(u"Объявление '%s' обновлено." % form.title.data, "info")
            return redirect(url_for("account_sale"))
    else:
        form.pet.data = str(num(adv.get("pet_id")))
        form.breed.data = u"{0}_{1}".format(num(adv.get("pet_id")), num(adv.get("breed_id")))
        form.title.data = adv.get("title")
        form.desc.data = adv.get('desc')
        form.price.data = num(adv.get('price'))
        form.gender.data = str(num(adv.get('gender_id')) or '')
        form.photos.data = ",".join(adv.get("photos"))
        form.city.data = get_city_and_region(adv.get("city_id"))
        form.age.data = str(num(adv.get("age_id")))
    return render_template("/account/sale_edit.html", form=form, title=u"Редактировать объявление о продаже", btn_name = u"Сохранить", adv = adv)


@app.route("/account/sale/add/", methods = ['GET', 'POST'])
@login_required
def account_sale_add():
    form = Sale(request.form)
    if request.method == "POST" and form.validate():
        print(request.form)
        (pet, breed) = form.breed.data.split('_')
        id = sale_save(form)
        flash(u"Объявление '%s' добавлено." % form.title.data, "info")
        return redirect(url_for('account_sale'))
    return render_template("/account/sale_edit.html", form=form, title=u"Новое объявление о продаже", btn_name = u"Добавить")

# @app.route("/sovety/")
@app.route("/advice/")
def advice():
    return ""

@app.route("/ajax/")
def ajax():
    pass

# @app.route("/acount/stud/add", methods = ["POST", "GET"])
# @login_required
# def account_stud_add():
#     form = Stud(request.form)
#     if request.method == "POST" and form.validate():
#         print(request.form)
#         id = sales().insert({'user': current_user.id, 'pet': form.pet.data, 'breed': form.breed.data, 'title':form.title.data, 'desc': form.desc.data, 'ps': form.photos.data.split(",")})
#         flash(u"Объявление %s добавлено." % str(id), "info")
#         return redirect(url_for('account_sale'))
#     return render_template("/account/sale_adv.html", form=form, title=u"Новое объявление")



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
        (name, file) = get_photo(db, filename)
        if name and file:
            create_thumbnail(file, photos.path(name))
        else:
            if os.path.exists(photos.path(filename)):
                with open(photos.path(filename)) as f:
                    create_thumbnail(f.read(), photos.path(filename))

    return send_file(path)
    
@app.route('/photo/<filename>/', defaults = {'width': None})
@app.route('/photo/<filename>/<int:width>/')
def photo(filename, width):
    if width:
        (name, ext) = os.path.splitext(filename)
        path = photos.path(name + str(width) + ext)
    else:
        path = photos.path(filename) 
    if not os.path.exists(path):
        try:
            (name, file) = get_photo(db, filename)
            if name and file:
                with open(path, 'w') as f:
                    f.write(file)
            if width:
                resize_image(path, width = width)    
        except Exception, e:
            print(e)
            os.remove(path)
        

    return send_file(path)

@app.route("/mail/sale/<id>/", methods = ["POST", "GET"])
def mail_sale(id):
    form = SendMail(request.form)
    adv = sales().find_one(ObjectId(id))
    if not adv:
        abort(404)

    seller = users().find_one(ObjectId(adv.get("user")))
    if not seller:
        abort(404)

    if request.method == "POST":
        if form.validate():
            send_from_sale(form.email.data, form.username.data, adv.get('_id'), seller, form.subject.data, form.message.data)
            if form.sms_alert.data and seller.get('phone') and seller.get('phone_adv_sms'):
                send_sms(u"Пользователь сайта Поводочек отправил вам почтовое сообщение.", \
                    [seller.get('phone')] )
            return render_template("/mail_sale.html", title = u"Сообщение успешно отправлено")
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("/mail_sale.html", form = form, seller = seller, title=u"Написать письмо")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/img'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
