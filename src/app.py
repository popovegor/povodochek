#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import (Flask, render_template, request, flash, redirect, url_for)
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

from wtforms import Form, BooleanField, TextField, PasswordField, validators
from forms import SignUp, SignIn, Sale
from pymongo import MongoClient
from bson.objectid import ObjectId

from werkzeug.utils import secure_filename
import os


def mongo():
    return MongoClient().povodochek

def users():
    return mongo().users

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

SECRET_KEY = "yeah, not actually a secret"
DEBUG = True

app.config.from_object(__name__)

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


@app.route("/account/sale")
@login_required
def account_sale():
    tmpl = render_template("account/sale.html", page_title=u"Продаю")
    return tmpl

app.route("/account/stud")
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

@app.route("/account/sale/add", methods = ['GET', 'POST'])
@app.route("/account/sale/<id>", methods = ['GET', 'POST'])
@login_required
def account_sale_adv(id = 0):
    page_title = (u"Добавить"  if id == 0 else u"Редактировать") + u" объявление"
    print(id)
    form = Sale(request.form)
    if request.method == "POST" and form.validate():
        print(request.form)
        flash(u"Объявление успешно добавлено", "success")
        return redirect(url_for('account_sale'))
    return render_template("/account/sale/adv.html", form=form, page_title=page_title)

# upload files
# 
# 

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    print(request.method, request.files)
    if request.method == 'POST':
        saved_files_urls = []
        for key, file in request.files.iteritems():
            print(key, file)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                print(file_path)
                file.save(file_path)
                saved_files_urls.append(url_for('uploaded_file', filename=filename))
        return saved_files_urls[0]
        #return render_template('saved_files.html', urls=saved_files_urls)

    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER,
                               filename)


@app.route('/upload1', methods=['GET', 'POST'])
def upload1():
    return render_template("upload1.html")

if __name__ == "__main__":
    app.debug = True
    app.secret_key = "some_sercet"
    app.run(host='0.0.0.0')
