#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, flash, redirect, url_for, session, send_from_directory, abort, jsonify, Markup)
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

from wtforms import (Form, BooleanField, TextField, PasswordField, validators)
from forms import (SignUp, SignIn, Sale, Test, Contact, Activate,ResetPassword, ChangePassword, SaleSearch, get_city_by_city_and_region)
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.son import SON

from werkzeug.utils import secure_filename
import os
from uuid import uuid4, uuid1
from datetime import datetime, date
import re
from sys import maxint

from flaskext.uploads import (UploadSet, configure_uploads, IMAGES,
                              UploadNotAllowed)

from security import hash_password, check_password

from flask_mail import (Mail, Message)
from threading import Thread
from momentjs import MomentJS
from pymorphy2 import MorphAnalyzer
from helpers import num

morph = MorphAnalyzer()

# from pymorphy import 

photos = UploadSet('photos', IMAGES)


def mongo():
    return MongoClient().povodochek

def users():
    return mongo().users

def sales():
    return mongo().sales

def pets():
    return mongo().pets

def breeds():
    return mongo().breeds

def genders():
    return mongo().genders

def cities():
    return mongo().cities

def ages():
    return mongo().ages

class User(UserMixin):
    def __init__(self, name, id, active=True):
        self.name = name
        self.id = id
        self.active = active

    def is_active(self):
        return self.active


class Anonymous(AnonymousUser):
    name = u"Anonymous"

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
    return Markup((template.format(value) if value else u"").replace(u",", u"<span style='letter-spacing:-3px'> </span>"))

app.jinja_env.filters['format_price'] = jinja_format_price

def jinja_format(value, template=u"{0}"):
    return template.format(value)

app.jinja_env.filters['format'] = jinja_format

# todo: add caching layer 
def get_pet_name(pet_id):
    pet = pets().find_one({"id": num(pet_id)}) if pet_id else None
    return pet.get("name") if pet else u""

app.jinja_env.filters['pet_name'] = get_pet_name

# todo: add caching layer
def get_breed_name(breed_id):
    breed = breeds().find_one({"id": num(breed_id)}) if breed_id else None
    return breed.get("name") if breed else u""

app.jinja_env.filters['breed_name'] = get_breed_name

# todo: add caching layer 
def get_gender_name(gender_id):
    gender = genders().find_one({"id": num(gender_id)}) if gender_id else None
    return gender.get("name") if gender else u""

app.jinja_env.filters['gender_name'] = get_gender_name

# todo: add caching layer 
def get_age_name(age_id):
    age = ages().find_one({"id": num(age_id)}) if age_id else None
    return age.get("name") if age else u""

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
        for part in filter(lambda x: len(x) > 0, parts):
            parse = morph.parse(part)
            morphed_part = part
            if grammemes:
                grammemes = set(grammemes)
                inflect_word = parse[0].inflect(grammemes) if parse[0] else None
                if inflect_word:
                    morphed_part = parse[0].inflect(grammemes).word if parse[0] else part
            elif count >= 0:
                morphed_part = parse[0].make_agree_with_number(count).word if parse[0] else part
            morphed_part = morph_restore_register(morphed_part, part)
            morphed_word = morphed_word.replace(part, morphed_part)
    return morphed_word

app.jinja_env.filters['morph_word'] = morph_word

def debug_write(msg):
    print("DEBUG INFO: %s" % msg)

@login_manager.user_loader
def load_user(id):
    # print("user id = %s" % str(id))
    user = users().find_one({'_id':ObjectId(id)})
    return User(user.get("email"), user.get("_id"), user.get("activated")) if user else Anonymous

@app.route("/")
def index():
    tmpl = render_template('index.html')
    return tmpl

@app.route("/signin/", methods = ["POST", "GET"])
def signin():
    form = SignIn(request.form)
    if request.method == "POST" and form.validate():
        (email, password, remember) = (form.email.data, form.password.data, form.remember.data)
        user = users().find_one({'email': email})
        if user and check_password(user.get("pwd_hash"), password):
            if user.get("activated"):
                if login_user(User(email, user["_id"]), remember=remember):
                    return redirect(request.args.get("next") or url_for("account_sale"))
                else:
                    flash(u"Извините, но вы не можете войти.", "error")
            else:
                print('disactivated')
                flash(Markup(u"Вы не можете войти на сайт, так регистрация не подтверждена. Проверьте, пожалуйста, эл. почту или отправьте <a target='_blank' href='{0}'>ссылку на активацию</a> повторно.".format(url_for('activate', confirm=''))), "error")
        else:
            flash(u"Адрес электронной почты или пароль неправильный.", "error")
    return render_template("signin.html", form=form, title=u"Вход на сайт")

@app.route("/ajax/location/prefetch.json", methods = ["GET"])
def ajax_location_prefetch():
    locations = [ city.get("city_name") for city in cities().find(fields=["city_name"])]
    return jsonify(items = locations ) 

@app.route("/ajax/location/typeahead/", methods = ["GET"])
def ajax_location_typeahead():
    print(request.args.get("query"))
    query = (request.args.get("query") or "").strip()
    limit = int(request.args.get("limit") or 8)
    matcher = re.compile("^" + re.escape(query), re.IGNORECASE)
    locations = [ city.get("city_region") \
        for city in cities().find({'city_region': {"$regex": matcher}}, limit=limit, fields=["city_region"])]
    return jsonify(items = locations )     

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

def send_signup(username, email, password, confirm):
    msg = Message(u"Регистрация на сайте Поводочек", recipients=[email])
    msg.html = render_template("email/signup.html", username=username, email = email, password = password, confirm = confirm)
    mail.send(msg)

def send_reset_password(email, asign, password):
    msg = Message(u"Сброс пароля для сайта Поводочек", recipients=[email])
    msg.html = render_template("email/reset_password.html", email = email, password = password, asign = asign)
    mail.send(msg)
    
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
                flash(u"Ссылка на активацию регистрации успешно отправлена. Проверьте электронную почту '%s', чтобы подтвердить регистрацию." %email, "success")
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
        if login_user(User(user["email"], user["_id"])):
            flash(u"Новый пароль был успешно активирован", "success")
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
        flash(u"Пароль успешно изменен.", "success")
    return render_template("account/change_password.html", title=u"Смена пароля", form = form)


@app.route("/test/email/signup/")
def test_email_signup():
    msg = Message("Регистрация на сайте Поводочек", recipients=["popovegor@gmail.com"])
    msg.html = render_template("email/signup.html", username=u"Егор", password = u"sdfhk434988", email = u"popovegor@gmail.com", confirm=u"nab4eae954386beb2955e49c1ad50a51e")
    # mail.send(msg)
    return msg.html

@app.route("/test/email/reset-password/")
def test_email_reset_password():
    return render_template("email/reset_password.html", password = u"sdfhk434988", email = u"popovegor@gmail.com", asign=u"nab4eae954386beb2955e49c1ad50a51e")

@app.route("/test/email/activate/")
def test_email_activate():
    return render_template("email/activate.html", confirm = "1")


@app.route("/signup/", methods = ["POST", "GET"])
def signup():
    form = SignUp(request.form)
    if request.method == "POST" and form.validate():
        (email, password, confirm, username) = (form.email.data, form.password.data, str(uuid4()), form.username.data)
        print(email, password)
        users().insert({'email': email, 'pwd_hash': hash_password(password), 'username': username, 'confirm': confirm, 'activated': False, 'signup_date': datetime.utcnow()})
        send_signup(username, email, password, confirm)
        flash(u"Регистрация почти завершена. Проверьте электронную почту '%s', чтобы подтвердить регистрацию." %email, "success")
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form, title=u"Регистрация")

@app.route("/reset-password/", methods = ["GET", "POST"])
def reset_password():
    form = ResetPassword(request.form)
    if request.method == "POST" and form.validate():
        email = form.email.data
        password = str(hash(str(uuid1())) % 10000000)
        asign = str(uuid4())
        user = users().find_and_modify({'email': email}, {"$set": {'asign_pwd_hash': hash_password(password), 'asign': asign}})
        if user:
            send_reset_password(email, asign, password)
            flash(u"Ссылка на смену пароля была успешна отправлена на эл. почту '%s'" %email , "success")
    return render_template("reset_password.html", title=u"Сброс пароля", form = form)

@app.route("/signout/")
@login_required
def signout():
    logout_user()
    return redirect(url_for("index"))


def cities_near(city = None, distance = None):
    cities = []
    if city and distance and city.get("location"):
        location = city.get("location")
        geoNear = mongo().command(SON([("geoNear",  "cities"), ("near", location) ,( "spherical", True ), ("maxDistance", distance * 1000), ("limit", 5000)]))
        cities = [(geo["obj"], geo["dis"]) for geo in geoNear.get("results")]
    return cities


def sale_find(pet_id = None, gender_id = None, age_id=None, breed_id = None, city = None, distance = None, photo = False, price_from = None, price_to = None, sort = None):
    add_to_query = lambda k,v: query.update({k:v}) if v else None
    query = {}
    add_to_query("pet_id", num(pet_id))
    add_to_query("gender_id", num(gender_id))
    add_to_query("age_id", num(age_id))
    add_to_query("breed_id", num(breed_id))

    price_form = num(price_from)
    price_to = num(price_to)
    if price_from or price_to:
        add_to_query("price", \
            {"$gte" : price_from if price_from else 0,\
             "$lt" : price_to if price_to else maxint })
    near_cities = []
    if city and distance:
        near_cities = cities_near(city, distance)
        add_to_query("city_id", {"$in": [city.get("id") for city, dis in near_cities]})

    if photo:
        add_to_query("photos", {"$nin": [None, []]})
    sortby = [("update_date", -1)]
    if sort == 1:
        sortby = [("price", -1)]
    elif sort == 2:
        sortby = [("price", 1)]
    else:
        sortby = [("update_date", -1)]
    print("sale query %s" % query)
    print("sale sort %s" % sortby)
    advs = [adv for adv in sales().find(SON(query), sort = sortby)]

    if near_cities:
        for adv in advs:
            adv_city_id = adv.get("city_id")
            (near_city, dist) = next( ((city, dist) for city, dist in near_cities if city["id"] == adv_city_id), (None, None))
            adv["distance"] = int(round(dist / 1000, 0))

    return advs


def sale_find_header(form):
    # generate title
    header = u"Купить <small><i class='muted'>(Продают)</i></small> {0}{1}{2}"
    title = u"Купить {0}{1}: Продажа {2}{1}"
    pet = u"собаку или кошку"
    if form.pet.data == "1":
        pet = u"собаку (щенка)"
    elif form.pet.data == "2":
        pet = u"кошку (котенка)"

    (pet_id, breed_id) = form.breed.data.split('_') if form.breed.data and len(form.breed.data.split("_")) > 1 else (None, None)
    breed = get_breed_name(breed_id)
    if breed:
        # breed = u" {0}".format(morph_word(breed, {"gent"}).lower())
        breed = u" породы {0}".format(breed).lower()

    return (header.format(pet, breed, u""), title.format(pet, breed, morph_word(pet, {"gent", "plur"}) ), pet, breed) 

@app.route("/sale/")
def sale():
    form = SaleSearch(request.args)
    city = get_city_by_city_and_region(form.city.data)
    form.city.city_id = city["id"] if city else None
    (pet_id, breed_id) = form.breed.data.split("_") if form.breed.data and len(form.breed.data.split("_")) > 1 else (None, None)

    # sort
    session["sale_sort"] = form.sort.data or session.get("sale_sort") or 3
    
    advs = sale_find(pet_id = form.pet.data, \
        breed_id = breed_id,\
        age_id = form.age.data,\
        gender_id = form.gender.data,\
        city = city, \
        distance = form.distance.data, \
        photo = form.photo.data, \
        price_from = form.price_from.data, \
        price_to = form.price_to.data if num(form.price_to.data) < 100000 else None,\
        sort = session.get("sale_sort")
        )

    (header, title, pet_name, breed_name) = sale_find_header(form)

    tmpl = render_template("sale.html", header=Markup(header), title=title, form= form, advs = advs, pet = pet_name, breed = breed_name, sort = session.get("sale_sort"))
    return tmpl

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
            users().update({"_id": current_user.id}, {"$set":\
                {"username": form.username.data, "city_id": form.city.city_id, "phone": form.phone.data}})
            flash(u"Контактная информация обновлена.", "success")
            return redirect(url_for("account_contact"))
    else:
        form.city.data = get_city_and_region(user.get("city_id"))
        form.username.data = user.get("username")
        form.phone.data = user.get("phone") 
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

    tmpl = render_template("account/sale.html", title=u"Мои объявления о продаже", advs = advs)
    return tmpl


def sale_save(form, id = None):
    photos = []
    if form.photos.data:
        photos = form.photos.data.split(',')
        photos = filter(lambda x: x and len(x) > 0, photos)
    (pet_id, breed_id) = form.breed.data.split("_")
    now = datetime.utcnow()
    sale = {'user': str(current_user.id), 'pet_id': num(pet_id), 'breed_id': num(breed_id), 'title':form.title.data, 'desc': form.desc.data, 'photos': photos, 'price': form.price.data, 'gender_id': num(form.gender.data), 'update_date':now, "city_id": form.city.city_id, 'age_id': num(form.age.data)}
    if id:
        sales().update(
            {'_id': ObjectId(id), 'user': {'$in': [current_user.id, str(current_user.id)]} } 
            , {'$set': sale}, upsert=True)
    else:
        sale["add_date"] = now
        id = sales().insert(sale)
    return id


@app.route("/account/sale/<id>/remove", methods = ['GET'])
@login_required
def account_sale_remove(id):
    adv = sales().find_one(
        {'_id': {'$in':[id, ObjectId(id)]}, 
        'user': {'$in': [current_user.id, str(current_user.id)]}})
    if adv:
        # sales().remove({"_id": adv["_id"]  })
        flash(u"Объявление '%s' удалено." % adv["title"], "success")
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
            flash(u"Объявление '%s' обновлено." % form.title.data, "success")
            return redirect(url_for("account_sale"))
    else:
        form.pet.data = str(adv.get("pet_id"))
        form.breed.data = u"{0}_{1}".format(adv.get("pet_id"), adv.get("breed_id"))
        form.title.data = adv.get("title")
        form.desc.data = adv.get('desc')
        form.price.data = adv.get('price')
        form.gender.data = str(adv.get('gender_id') or '')
        form.photos.data = ",".join(adv.get("photos"))
        form.city.data = get_city_and_region(adv.get("city_id"))
        form.age.data = str(adv.get("age_id"))
    return render_template("/account/sale_edit.html", form=form, title=u"Редактировать объявление", btn_name = u"Сохранить", adv = adv)


@app.route("/account/sale/add/", methods = ['GET', 'POST'])
@login_required
def account_sale_add():
    form = Sale(request.form)
    if request.method == "POST" and form.validate():
        print(request.form)
        (pet, breed) = form.breed.data.split('_')
        id = sale_save(form)
        flash(u"Объявление '%s' добавлено." % form.title.data, "success")
        return redirect(url_for('account_sale'))
    return render_template("/account/sale_edit.html", form=form, title=u"Новое объявление", btn_name = u"Добавить")

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
#         flash(u"Объявление %s добавлено." % str(id), "success")
#         return redirect(url_for('account_sale'))
#     return render_template("/account/sale_adv.html", form=form, title=u"Новое объявление")



# upload files
# 

@app.route('/upload/', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    print(file)
    if file:
        filename = photos.save(file, name=str(uuid4()) + ".")
        # filename = photos.save(file)
        return filename
        

@app.route('/photo/<filename>')
def photo(filename):
    photo = send_from_directory(app.config["UPLOADED_PHOTOS_DEST"], filename)
    return photo

@app.route('/test', methods = ["GET", "POST"])
def test():
    form = Test(request.form)
    if request.method == "POST" and form.validate():
        return render_template('/test.html', form = form)
    return render_template('/test.html', form = form)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
