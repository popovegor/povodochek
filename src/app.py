#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, flash, redirect, url_for, session, send_from_directory, send_file, abort, jsonify, Markup, make_response)
from flask_login import (LoginManager, current_user,
                            login_user, logout_user, login_required, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

from wtforms import (Form, BooleanField, TextField, PasswordField, validators)
from forms import (SignUp, SignIn, Sale, Contact, Activate,ResetPassword, ChangePassword, SaleSearch, get_city_by_city_field, SendMail, ChangeEmail, SignUpBasic)
from pymongo import (MongoClient, ASCENDING, DESCENDING)
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
from itertools import groupby

from flaskext.uploads import (UploadSet, configure_uploads, IMAGES,
                              UploadNotAllowed)

from security import hash_password, check_password

from flask_mail import (Mail, Message)
from threading import Thread
from momentjs import MomentJS
from helpers import (num, create_thumbnail, get_thumbnail_filename, resize_image, save_photo, get_photo, get_photo_size, qoute_rus, morph_word)

from smsgate import send_sms

from dic.ages import ages
from dic.genders import genders
from dic.pets import (pets, get_pet_name, DOG_ID, CAT_ID)
from dic.breeds import (dogs, get_breed_name, get_composite_breed, cats, get_breed_by_name)
from dic.cities import (get_city_region, get_city, get_city_name, format_city_region)

from flaskext.markdown import Markdown
from flask.ext.assets import Environment, Bundle
from advs_parser import parse_avito_adv

photos = UploadSet('photos', IMAGES)

db = MongoClient().povodochek

def users():
    return db.users

def sales():
    return db.sales

def pets_by_cities():
    return db.pets_by_cities

def top_breeds():
    return db.top_breeds

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
    name = u"Anonymous"
    username = u""
    email = u""

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
    'js/jquery.validate.min.js', \
    'js/jquery.validate.ru.js', \
    'js/jquery.inputmask.min.js', \
    'js/jquery.textareaCounter.plugin.js', \
    'js/moment.min.js', \
    'js/moment.min.ru.js', \
    'js/jquery.nouislider.min.js', \
    'js/jquery.flexslider.min.js', \
    'js/jquery.touch-punch.min.js', \
    'js/jquery.shapeshift.js', \
    'js/jquery.mosaicflow.min.js', \
    'js/bootstrap3-typeahead.min.js', \
    'js/holder.min.js', \
    'js/bootstrap.min.js', \
    'js/jquery.carouFredSel.min.js', \
    'js/povodochek.js', \
    filters='rjsmin', \
    output='gen/js.js')
assets.register('js_all', js)

css = Bundle('css/bootstrap.min.css', \
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

app.jinja_env.filters['format'] = jinja_format

app.jinja_env.filters['pet_name'] = get_pet_name

app.jinja_env.filters['breed_name'] = get_breed_name
app.jinja_env.filters['composite_breed'] = get_composite_breed

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
    return User(user.get('login'), user.get("_id"), active = user.get("activated"), username = user.get("username"), email = user.get("email"), new_email = user.get("new_email"), city_id = user.get("city_id"), phone= user.get("phone"), skype = user.get("skype") ) if user else Anonymous

@app.route("/")
def index():
    mosaic_advs = get_sales_for_mosaic(0, 6)
    top_dogs = [adv for adv in top_breeds().find({'pet_id':1}, sort = [('count', DESCENDING)], limit = 10)]
    top_cats = [adv for adv in top_breeds().find({'pet_id':2}, sort = [('count', DESCENDING)], limit = 10)]
    tmpl = render_template('index1.html', \
        pet_search_form = SaleSearch(), \
        top_cats = top_cats, \
        top_dogs = top_dogs, 
        title = u"Продажа породистых собак и кошек", mosaic_advs = [adv for adv in mosaic_advs])
    return tmpl

@app.route("/signin/", methods = ["POST", "GET"])
def signin():
    form = SignIn(request.form)
    if request.method == "POST" and form.validate():
        (login, password, remember) = (form.login.data, form.password.data, form.remember.data)
        matcher = re.compile("^" + re.escape(login) + "$", re.IGNORECASE)
        user = users().find_one({'login': {'$regex':matcher}})
        if user and check_password(user.get("pwd_hash"), password):
            if True or user.get("activated"):
                if login_user(User(login, user["_id"]), remember=remember):
                    return redirect(request.args.get("next") or url_for("account_contact"))
                else:
                    flash(u"Извините, но вы не можете войти.", "error")
            else:
                print('disactivated')
                flash(Markup(u"Вы не можете войти на сайт, так как регистрация не подтверждена. Проверьте, пожалуйста, электронную почту или отправьте <a target='_blank' href='{0}'>ссылку на активацию</a> повторно.".format(url_for('activate', confirm=''))), "error")
        else:
            flash(u"Неправильный логин или пароль.", "error")
    return render_template("signin.html", form=form, title=u"Вход на сайт")

@app.route("/ajax/activate/remember/later/")
@login_required
def ajax_activate_remember_later():
    later = session["activate_remember_later"] = True
    return "success"


@app.route("/ajax/typeahead/location/prefetch.json", methods = ["GET"])
def ajax_location_prefetch():
    locations = [ city.get("city_region") for city in db.cities.find(fields=["city_region"])]
    return jsonify(items = locations ) 

@app.route("/ajax/typeahead/location/", methods = ["GET"])
def ajax_typeahead_location():
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    matcher = re.compile("^" + re.escape(query), re.IGNORECASE)
    locations = [ city.get("city_region") \
        for city in db.cities.find({'city_region': {"$regex": matcher}}, limit=limit, fields=["city_region"])]
    return jsonify(items = locations )    

@app.route("/ajax/typeahead/breed/", defaults={'pet_id':None}, methods = ["GET"])
@app.route("/ajax/typeahead/breed/<int:pet_id>/", methods = ["GET"])
def ajax_typeahead_breed(pet_id = None):
    # print(str(request.args.get("query")))
    query = (request.args.get("query") or u"").strip()
    limit = max(int(request.args.get("limit") or 8), 8)
    matcher = query.lower()
    breeds = []
    if not pet_id or pet_id == DOG_ID:
        breeds = breeds + [u"{0}{1}".format(dog, u", Собаки") for dog in dogs.values() if matcher in dog.lower() ] 
    if not pet_id or pet_id == CAT_ID:
        breeds = breeds + [u"{0}{1}".format(cat, u", Кошки") for cat in cats.values() if matcher in cat.lower() ]
    return jsonify(items = breeds )  

def url_for_sale_show(pet_id, adv_id, **kwargs):
    return url_for('sale_show_dog', id = adv_id, **kwargs) if pet_id == 1 else url_for('sale_show_cat', id = adv_id, **kwargs)

app.jinja_env.globals['url_for_sale_show'] = url_for_sale_show

def get_sales_for_mosaic(skip, limit = 36, pet_id = None):
    query = {"photos": {"$nin": [None, []]} }
    if pet_id:
        query["pet_id"] = pet_id
    advs = [{"src":url_for('thumbnail', \
            filename = adv.get('photos')[0], width= 300), \
        'url' : url_for_sale_show( pet_id = adv.get('pet_id'), adv_id = adv.get('_id')), \
        'id': str(adv.get('_id')), \
        'p' : adv.get('price'), \
        'b' : get_breed_name(adv.get('breed_id'), adv.get('pet_id')), \
        's' : {'h':100, 'w':150}}
        for adv in sales().find(
            query, \
            skip = skip, \
            fields = ["_id", "photos", "title", "pet_id", "price", "breed_id", "pet_id"], \
            limit = limit, \
            sort = [('update_date', -1)]) ]
    return advs


@app.route("/ajax/sales/showmore/<int:pet>/", methods = ["GET"], defaults= {"limit":36, 'skip': 0})
@app.route("/ajax/sales/showmore/<int:pet>/<int:skip>/", methods = ["GET"], defaults= {"limit":36})
@app.route("/ajax/sales/showmore/<int:pet>/<int:skip>/<int:limit>/", methods = ["GET"])
def ajax_sales_showmore(pet, skip, limit):
    print(pet)
    advs = get_sales_for_mosaic(skip, limit = limit, pet_id = pet)
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

def send_from_sale(email, username, sale_id, seller_email, seller_username, subject, message):
    adv = sales().find_one(ObjectId(sale_id))
    if adv and seller_email:
        msg = Message(subject, recipients=[seller_email])
        msg.html = render_template("email/from_sale.html", \
            subject = subject, \
            message = message, \
            adv = adv, \
            seller_email = seller_email, \
            seller_username = seller_username, \
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
        seller = users().find_one(ObjectId(adv.get('user_id'))), \
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
    title=u"Активация нового пароля"
    if user:
        users().update({'_id': user["_id"]}, \
            {"$set": {'asign': '', 'pwd_hash': user['asign_pwd_hash'], 'asign_pwd_hash': ''} })
        if login_user(User(user.get("login"), user.get("_id"))):
            return render_template("asignin_success.html", title = title)
    return render_template("asignin_failed.html", title=title)

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
def signup_basic():
    form = SignUpBasic(request.form)
    if request.method == "POST" and form.validate():
        (login, email, password, confirm, username) = (form.login.data, form.email.data, form.password.data, str(uuid4()), "Пользователь")
        user_id = users().insert({'login': login, 'email': email, 'pwd_hash': hash_password(password), 'username': username, 'confirm': confirm, 'activated': False, 'signup_date': datetime.utcnow()})
        send_signup(username, login, email, password, confirm)
        flash(u"Для того чтобы подтвердить регистрацию, перейдите по ссылке в отправленном Вам письме.", "info")
        if login_user(User(login, user_id), remember = True):
            return redirect(request.args.get('next') or url_for('account_contact'))
        else:
            return redirect(url_for('signin'))
    return render_template('signup_basic.html', form=form, title=u"Регистрация")

@app.route("/registracija/", methods = ["POST", "GET"])
def signup():
    form = SignUp(request.form)
    if request.method == "POST" and form.validate():
        (login, email, password, confirm, username) = (form.login.data, form.email.data, form.password.data, str(uuid4()), form.username.data)
        user_id = users().insert({'login': login, 'email': email, 'pwd_hash': hash_password(password), 'username': username, 'confirm': confirm, 'activated': False, 'signup_date': datetime.utcnow()})
        send_signup(username, login, email, password, confirm)
        flash(u"Для того чтобы подтвердить регистрацию, перейдите по ссылке в отправленном Вам письме.", "info")
        if login_user(User(login, user_id), remember = True):
            return redirect(request.args.get('next') or url_for('account_contact'))
        else:
            return redirect(url_for('signin'))
    return render_template('signup.html', form=form, title=u"Регистрация")

@app.route("/reset-password/", methods = ["GET", "POST"])
def reset_password():
    form = ResetPassword(request.form)
    title = u"Сброс пароля"
    if request.method == "POST" and form.validate():
        email_or_login = form.email_or_login.data
        password = str(hash(str(uuid1())) % 10000000)
        asign = str(uuid4())
        user = users().find_and_modify({'$or' : [{'email': email_or_login}, {'login': email_or_login}]}, \
            {"$set": {'asign_pwd_hash': hash_password(password), 'asign': asign}})
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


def cities_near(city = None, distance = None):
    cities = []
    if city:
        search_city = db.cities.find_one({'city_id': city.get('city_id')})
        if search_city and distance and search_city.get("location"):
            location = search_city.get("location")
            geoNear = db.command(SON([("geoNear",  "cities"), ("near", location) ,( "spherical", True ), ("maxDistance", distance * 1000), ("limit", 5000)]))
            cities = [(geo["obj"], geo["dis"]) for geo in geoNear.get("results")]
    return cities


def sale_find(pet_id = None, gender_id = None, breed_id = None, city = None, distance = None, photo = False, price_from = None, price_to = None, sort = None, skip = None, limit = None):

    _filter = {}
    extend_filter = lambda k,v: _filter.update({k:v}) if v else None
    extend_filter("pet_id", num(pet_id))
    if num(gender_id):
        extend_filter('$or', [{'gender_id' : num(gender_id)}, {'gender_id' : {'$exists': False}}])

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
        extend_filter("city_id", {"$in": [city.get("city_id") for city, dis in near_cities]})

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
            (near_city, dist) = next( ((city, dist) for city, dist in near_cities if city["city_id"] == adv_city_id), (None, None))
            adv["distance"] = int(round(dist / 1000, 0))

    return (advs, count, total)


def sale_find_header(form, pet_id, breed_id):
    # generate title
    header = u"Купить <small>(Продают)</small> {0}{1}{2}"
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
        breed_header = Markup(u" породы %s" % breed.lower() )
        breed_title = Markup(u" породы {0}".format(breed.lower()))

    city = get_city_name(form.city.city_id, "i") if form.city.city_id else u''
    if city:
        city = u" в г. {0}".format(city)
        # if form.distance.data:
            # city = u"{0}(+ {1} км)".format(city, form.distance.data) 

    return (header.format(pet, breed_header, city), title.format(pet, breed_title, morph_word(pet, {"gent", "plur"}), city), pet, breed) 

@app.route("/kupit-sobaku-koshku/")
def kupit_sobaku_koshku():
    form = SaleSearch()
    form = SaleSearch(request.args)
    return sale(form)


@app.route("/prodazha-sobak/")
def sale_dogs():
    form = SaleSearch()
    form = SaleSearch(request.args)
    return sale(form, DOG_ID)

@app.route("/prodazha-koshek/")
def sale_cats():
    form = SaleSearch()
    form = SaleSearch(request.args)
    return sale(form, CAT_ID)

@app.route("/prodazha-koshek-sobak/")
def sale(sale_search_form = None, pet = None):
    form = sale_search_form or SaleSearch(request.args)
    city = get_city_by_city_field(form.city)
    (form.city.data, form.city.city_id) = \
        (format_city_region(city), city.get("city_id")) if city else (None, None)
    (breed_id, pet_id) = get_breed_by_name(form.breed.data)
    pet_id = pet_id or pet
    # sort
    session["sale_sort"] = form.sort.data or session.get("sale_sort") or 3
    
    (advs, count, total) = sale_find(pet_id = pet_id, \
        breed_id = breed_id, \
        gender_id = form.gender.data, \
        city = city, \
        distance = form.distance.data + 0.01, \
        photo = form.photo.data, \
        price_from = form.price_from.data  * 1000, \
        price_to = (form.price_to.data if num(form.price_to.data) < 100 else 0) * 1000, \
        sort = session.get("sale_sort"),
        skip = (form.page.data - 1) * form.perpage.data, \
        limit = form.perpage.data
        )

    (header, title, pet_name, breed_name) = sale_find_header(form, pet_id, breed_id)

    tmpl = render_template("sale.html", header=Markup(header), \
      title=title, form = form, advs = advs, \
      pet = pet_name, pet_id = pet_id, \
      breed = breed_name, breed_id = breed_id, \
      sort = session.get("sale_sort"), \
      count = count, total = total )
    return tmpl


def url_for_sale(pet_id, **kwargs):
    return url_for('sale_dogs', **kwargs) if pet_id == 1 else url_for('sale_cats', **kwargs)

app.jinja_env.globals['url_for_sale'] = url_for_sale

@app.route('/prodazha-sobak/<id>/')
def sale_show_dog(id):
    return sale_show(id)

@app.route('/prodazha-koshek/<id>/')
def sale_show_cat(id):
    return sale_show(id)

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
    seller = users().find_one(ObjectId(adv.get("user_id")))
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
    user = users().find_one(current_user.id)
    form = Contact(request.form)
    if request.method == "POST":
        if form.validate():
            users().update({"_id": current_user.id}, {"$set":
                {"username": form.username.data, \
                "city_id": form.city.city_id if form.city.data else None, \
                "phone": form.phone.data, \
                "phone_adv_sms" : form.phone_adv_sms.data if form.phone.data else None, \
                "phone_adv_hide": form.phone_adv_hide.data if form.phone.data else None, \
                'skype' : form.skype.data, \
                'skype_adv_hide': form.skype_adv_hide.data if form.skype.data else None, \
                'city_adv_hide': form.city_adv_hide.data if form.city.data else None}})
            flash(u"Контактная информация обновлена.", "info")
            return redirect(url_for("account_contact"))
    else:
        form.city.data = get_city_region(user.get("city_id"))
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
        {'user_id': {'$in' : [str(current_user.id), current_user.id]} },\
        sort = [("update_date", DESCENDING)])

    tmpl = render_template("account/sale.html", \
        title=u"Мои объявления о продаже", \
        advs = [dict(adv, **{'active_date': adv.get('update_date') + timedelta(days=14)}) for adv in advs])
    return tmpl


def sale_save(form, id = None, moderator = None):
    filenames = []
    if form.photos.data:
        filenames = form.photos.data.split(',')
        filenames = filter(lambda x: x and len(x) > 0, filenames)
        for filename in filenames:
            if os.path.exists(photos.path(filename)):
                with open(photos.path(filename)) as file:
                    save_photo(db, file)

    now = datetime.utcnow()
    sale = {
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
        sale['username'] = form.username.data
        sale['email'] = form.email.data
        sale['moderator_id'] = str(moderator.id)
        sale['moderate_date'] = now
    else:
        sale['user_id'] = str(current_user.id)
    if id:
        sales().update(
            {'_id': ObjectId(id)} 
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
        'user_id': {'$in': [current_user.id, str(current_user.id)]}})
    if adv:
        sales().update({"_id": adv["_id"]}, {"$set": {"update_date": datetime.utcnow()}})
        flash(u"Объявление '%s' продлено на две недели." % adv["title"], "info")
    return redirect(url_for("account_sale"))



@app.route("/account/sale/<id>/remove", methods = ['GET'])
@login_required
def account_sale_remove(id):
    adv = sales().find_one(
        {'_id': {'$in':[id, ObjectId(id)]}, 
        'user_id': {'$in': [current_user.id, str(current_user.id)]}})
    if adv:
        sales().remove(adv)
        flash(u"Объявление '%s' удалено." % adv["title"], "info")
    return redirect(url_for("account_sale"))
    

@app.route("/account/sale/<id>/", methods = ['GET', 'POST'])
@login_required
def account_sale_edit(id):
    adv = sales().find_one(
        {'_id': {'$in':[id, ObjectId(id)]}, 
        'user_id': {'$in': [current_user.id, str(current_user.id)]}})
    if not adv:
        abort(404)

    form = Sale(request.form)
    if request.method == "POST":
        if form.validate():
            sale_save(form, id)
            flash(u"Объявление '%s' обновлено." % form.title.data, "info")
            return redirect(url_for("account_sale"))
    else:
        form.breed.data = get_breed_name(adv.get("breed_id"), adv.get("pet_id"))
        form.title.data = adv.get("title")
        form.desc.data = adv.get('desc')
        form.price.data = num(adv.get('price'))
        form.gender.data = str(num(adv.get('gender_id')) or '')
        form.photos.data = ",".join(adv.get("photos"))
        form.city.data = get_city_region(adv.get("city_id"))
        form.phone.data = adv.get("phone") or current_user.phone
        form.skype.data = adv.get("skype") or current_user.skype
    return render_template("/account/sale_edit.html", form=form, title=u"Редактировать объявление о продаже", btn_name = u"Сохранить", adv = adv)


@app.route("/account/sale/new/", methods = ['GET', 'POST'])
@login_required
def account_sale_add():
    form = Sale(request.form)
    if request.method == "POST":
        if  form.validate():
            id = sale_save(form)
            flash(u"Объявление '%s' добавлено." % form.title.data, "info")
            return redirect(url_for('account_sale'))
    else:
        form.city.data = get_city_region(current_user.city_id)
        form.phone.data = current_user.phone
        form.skype.data = current_user.skype
    return render_template("/account/sale_edit.html", form=form, title=u"Новое объявление о продаже", btn_name = u"Добавить")

@app.route("/poleznoe/")
def advice():
    return render_template("/advice.html", title=u"Полезные статьи о животных")

@app.route("/poleznoe/10-oshibok-kotoryx-sleduet-izbegat-pokupaya-porodistogo-shhenka")
def advice_article_1():
    return render_template("/advice/10-oshibok-kotoryx-sleduet-izbegat-pokupaya-porodistogo-shhenka.html", \
        title = u"Десять ошибок, которых следует избегать, покупая породистого щенка")


@app.route("/poleznoe/kalendar-sobachej-beremennosti")
def advice_article_2():
    return render_template("/advice/kalendar-sobachej-beremennosti.html", title = u"Календарь собачьей беременности")

# @app.route("/acount/stud/add", methods = ["POST", "GET"])
# @login_required
# def account_stud_add():
#     form = Stud(request.form)
#     if request.method == "POST" and form.validate():
#         print(request.form)
#         id = sales().insert({'user_id': current_user.id, 'pet': form.pet.data, 'breed': form.breed.data, 'title':form.title.data, 'desc': form.desc.data, 'ps': form.photos.data.split(",")})
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
            _name = create_thumbnail(file, photos.path(name), app.config['UPLOADED_PHOTOS_DEST'])
        else:
            if os.path.exists(photos.path(filename)):
                with open(photos.path(filename)) as f:
                    create_thumbnail(f.read(), photos.path(filename), app.config['UPLOADED_PHOTOS_DEST'])

    return send_file(path)
    
@app.route('/photo/<filename>/', defaults = {'width': None})
# @app.route('/photo/<filename>/<int:width>/')
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

@app.route("/pochta/prodazha/<id>/", methods = ["POST", "GET"])
def mail_sale(id):
    form = SendMail(request.form)
    adv = sales().find_one(ObjectId(id))
    
    if not adv:
        abort(404)

    seller = users().find_one(ObjectId(adv.get("user_id")))
    if not seller and not adv.get('email'):
        abort(404)
    seller_email = adv.get('email') or seller.get('email')
    seller_username = adv.get('username') or seller.get('username') 
    print("seller_username", seller_username)

    if request.method == "POST":
        if form.validate():
            send_from_sale(form.email.data, form.username.data, adv.get('_id'), seller_email, seller_username, u"Сообщение от пользователя сайта Поводочек", form.message.data)
            # if form.sms_alert.data and seller.get('phone') and seller.get('phone_adv_sms'):
            #     send_sms(u"Пользователь сайта Поводочек отправил вам почтовое сообщение.", \
            #         [seller.get('phone')] )
            return render_template("/mail_sale_sent.html", title = u"Сообщение успешно отправлено")
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
    return sale_pets_cities(pet_id = 2) 

@app.route('/prodazha-sobak/goroda/')
def sale_dogs_cities():
    return sale_pets_cities(pet_id = 1) 

def sale_pets_cities(pet_id):
    pet_name = morph_word(get_pet_name(pet_id), ["plur", "gent"]).lower()
    advs = sorted([adv for adv in pets_by_cities().find({'pet_id':pet_id})], \
        key = lambda x : x['city_name'])

    breeds_by_cities = [(letter, list(group)) for letter, group in groupby(advs, lambda adv : adv['city_name'][0])]

    return render_template("/sale_cities.html", \
        title=u"Объявления о продаже {0} по городам".format(pet_name), \
        breeds_by_cities = breeds_by_cities)


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

    # if app.current_user:
    #     abort(401)
    # return func(*args, **kwargs)


@app.route('/admin/sale/')
@admin_requried
def admin_sale():
    page = int(request.args.get("page") or 1)
    total = sales().count()
    perpage = 100
    advs = [adv for adv in sales().find(sort = [('update_date', DESCENDING)], limit = perpage, skip = (page - 1) * perpage)]
    for seller in users().find({'_id':{'$in' : [ObjectId(adv.get('user_id')) for adv in advs if adv.get('user_id') ]}}):
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


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
