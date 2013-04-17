#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, flash, redirect, url_for, session, send_from_directory, abort)
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

from wtforms import Form, BooleanField, TextField, PasswordField, validators
from forms import SignUp, SignIn, Sale, Test
from pymongo import MongoClient
from bson.objectid import ObjectId

from werkzeug.utils import secure_filename
import os
import uuid


from flaskext.uploads import (UploadSet, configure_uploads, IMAGES,
                              UploadNotAllowed)

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


UPLOADED_PHOTOS_DEST = '/tmp'
SECRET_KEY = "yeah, not actually a secret"

app.config.from_object(__name__)

configure_uploads(app, (photos))

login_manager = LoginManager()

login_manager.anonymous_user = Anonymous
login_manager.login_view = "/signin"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"

login_manager.setup_app(app)

def debug_write(msg):
    print("DEBUG INFO: %s" % msg)

@login_manager.user_loader
def load_user(id):
    print("user id = %s" % str(id))
    user = users().find_one({'_id':ObjectId(id)})
    print(user)
    return User(user["email"], user["_id"])

@app.route("/")
def index():
    tmpl = render_template('index.html')
    return tmpl

@app.route("/signin", methods = ["POST", "GET"])
def signin():
    form = SignIn(request.form)
    if request.method == "POST" and form.validate():
        (email, password, remember) = (form.email.data, form.password.data, form.remember.data)
        print("email, password = %s, %s" % (email, password))
        user = users().find_one({'email': email, 'pwd': password})
        if user:
            if login_user(User(email, user["_id"]), remember=remember):
                return redirect(request.args.get("next") or url_for("account"))
            else:
                flash(u"Извините, но вы не можете войти.", "error")
        else:
            flash(u"Адрес электронной почты или пароль неправильный.", "error")
            print(u'Wrong password or email (%s, %s)' % (email, password))
    # debug_write(errors)
    return render_template("signin.html", form=form, page_title=u"Войти на сайт")
    

@app.route("/signup", methods = ["POST", "GET"])
def signup():
    form = SignUp(request.form)
    if request.method == "POST" and form.validate():
        (email, password) = (form.email.data, form.password.data)
        print(email, password)
        users().insert({'email': email, 'pwd': password})
        flash(u"Регистрация прошла успешно. Проверьте электронную почту %s." %email, "success")
        return redirect(url_for('signin'))
    return render_template('signup.html', form=form, page_title=u"Регистрация")

@app.route("/remember")
def remember():
    debug_write(current_user.name)
    tmpl = render_template("remember.html", page_title=u"Сброс пароля")
    return tmpl

@app.route("/signout")
def signout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/sale")
def sale():
    tmpl = render_template("sale.html", page_title=u"Объявления о продаже")
    return tmpl

@app.route("/account")
@login_required
def account():
    tmpl = render_template("account/sale.html", page_title=u"Кабинет")
    return tmpl


@app.route("/account/stud")
@login_required
def account_stud():
    tmpl = render_template("account/stud.html", page_title=u"Повязать")
    return tmpl


@app.route("/account/wanted")
@login_required
def account_wanted():
    tmpl = render_template("account/wanted.html", page_title=u"Розыскиваю")
    return tmpl


@app.route("/account/user")
@login_required
def account_user():
    tmpl = render_template("account/user.html", page_title=u"Учетные данные")
    return tmpl


@app.route("/account/contact")
@login_required
def account_contact():
    tmpl = render_template("account/contact.html", page_title=u"Контактная информация")
    return tmpl

@app.route("/account/adoption")
@login_required
def account_adoption():
    tmpl = render_template("account/adoption.html", page_title=u"Отдам даром")
    return tmpl


@app.route("/account/sale")
@login_required
def account_sale():
    advs = sales().find({'user': current_user.id })
    print(advs)
    tmpl = render_template("account/sale.html", page_title=u"Мои объявления о продаже", advs = advs)
    return tmpl


@app.route("/account/sale/<id>", methods = ['GET', 'POST'])
@login_required
def acount_sale_edit(id):
    adv = sales().find_one({'_id': ObjectId(id), 'user': ObjectId(current_user.id)})
    # print(adv)
    if not adv:
        abort(404)

    form = Sale(request.form)
    if request.method == "POST":
        if form.validate():
            photos = []
            print(photos)
            if form.photos.data:
                photos = form.photos.data.split(',')
                photos = filter(lambda x: x and len(x) > 0, photos)
            print("photos: ", photos)
            (pet, breed) = form.breed.data.split("_")
            sales().update({'user': ObjectId(current_user.id), '_id': ObjectId(id)} , {'$set': {'pet': pet, 'breed': breed, 'title':form.title.data, 'desc': form.desc.data, 'photos': photos, 'price': form.price.data}})
            flash(u"Объявление %s обновлено." % str(id), "success")
            return redirect(url_for("account_sale"))
    else:
        form.pet.data = adv["pet"]
        form.breed.data = u"{0}_{1}".format(adv["pet"], adv["breed"])
        form.title.data = adv["title"]
        form.desc.data = adv['desc']
        form.price.data = adv['price']
        form.photos.data = ",".join(adv["photos"])
    return render_template("/account/sale_adv.html", form=form, page_title=u"Редактировать объявление", btn_name = u"Сохранить", photos = adv["photos"])



@app.route("/account/sale/add", methods = ['GET', 'POST'])
@login_required
def account_sale_add():
    form = Sale(request.form)
    if request.method == "POST" and form.validate():
        print(request.form)
        (pet, breed) = form.breed.data.split('_')
        id = sales().insert({'user': current_user.id, 'pet': pet, 'breed': breed, 'title':form.title.data, 'desc': form.desc.data, 'photos': form.photos.data.split(","), 'price': form.price.data})
        flash(u"Объявление %s добавлено." % str(id), "success")
        return redirect(url_for('account_sale'))
    else:
        pass
        # form.pet.choices = [(u"", u"")] + form.pet.choices
        # form.breed.choices = [(u"", u"")] + form.breed.choices
    return render_template("/account/sale_adv.html", form=form, page_title=u"Новое объявление", btn_name = u"Добавить")


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
#     return render_template("/account/sale_adv.html", form=form, page_title=u"Новое объявление")



# upload files
# 

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    print(file)
    if file:
        filename = photos.save(file, name=str(uuid.uuid4()) + ".")
        # filename = photos.save(file)
        return filename
        

@app.route('/photo/<filename>')
def show(filename):
    photo = send_from_directory(UPLOADED_PHOTOS_DEST, filename)
    print(filename)
    print(photo)
    return photo


@app.route('/gridster')
def gridster():
    return render_template("gridster.html")


@app.route('/shapeshift')
def shapeshift():
    return render_template("shapeshift.html")


@app.route('/test', methods = ["GET", "POST"])
def test():
    form = Test(request.form)
    if request.method == "POST" and form.validate():
        return render_template('/test.html', form = form)
    return render_template('/test.html', form = form)



if __name__ == "__main__":
    app.debug = True
    app.secret_key = "some_sercet"
    app.run(host='0.0.0.0')
