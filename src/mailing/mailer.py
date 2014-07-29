#!/usr/bin/python
# -*- coding: utf-8 -*-


from smtplib import SMTP_SSL as SMTP

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
import sys
from jinja2 import Template, Environment, PackageLoader
import config
from helpers import (run_async, morph_word, log_exception)
import helpers
import db

base_url = u"http://поводочек.рф"

env = Environment(loader=PackageLoader('mailing', ''))
env.globals['helpers'] = helpers

@run_async
def send_email_async(sender = u"Поводочек <%s>" % config.MAIL_USERNAME,
    to = [],
    subject = u"Сообщение от портала Поводочек", 
    text = u"",
    html = u"", 
    unsubscribe = u""):
    send_email(sender = sender, to = to, subject = subject, 
        text = text, html = html, unsubscribe = unsubscribe)

def send_email_to_user(user, subject, html, unsubscribe = u""):
    print(user)
    if user:
        email = user.get('email')
        name = user.get('username')
        to = [u"%s <%s>" % (name, email) if name != u"Пользователь" else email]
        send_email(to = to, subject = subject, html = html, unsubscribe = unsubscribe)

def send_email(
    sender = u"Поводочек <%s>" % config.MAIL_USERNAME,
    to = [],
    subject = u"Сообщение от портала Поводочек", 
    text = u"",
    html = u"", 
    unsubscribe = u""):
    try:
        if config.DEBUG:
            to = ['egor@povodochek.com']
        # Construct email
        msg = MIMEMultipart('alternative')
        msg['To'] = ", ".join([address.encode("utf-8") for address in to])
        msg['From'] = sender.encode("utf-8")
        msg['Subject'] = subject.encode("utf-8")
        if unsubscribe:
            msg["List-Unsubscribe"] = unsubscribe
         
        # Record the MIME types of both parts - text/plain and text/html.
        if text:
            part1 = MIMEText(text.encode("utf-8"), 'plain', "utf-8")
            msg.attach(part1)
        if html:
            part2 = MIMEText(html.encode("utf-8"), 'html', "utf-8")
            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.
            msg.attach(part2)

        # Send the message via an SMTP server
        s = SMTP(config.MAIL_SERVER)
        s.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
        try:
            if not config.MAIL_SUPPRESS_SEND:
                s.sendmail(sender, to, msg.as_string())
            else:
                print(to, subject)

        finally:
            s.quit()
    except Exception, exc:
        print("mail failed; %s" % str(exc) ) # give a error message

@run_async
def send_email_to_users(users, subject, hmtl):
    counter = 0
    for user in users:
        counter += 1
        print(counter)
        send_email_to_user(user, html = html, subject = subject)
 

def notify_user_of_dog_adv_archived(user, adv):
    if user and db.check_subscribe(user.get("_id"), "archived"):
        unsubscribe = get_unsibscribe_link(user, "expired")
        html = env.get_template('notify_dog_adv_archived.html').render(adv = adv, user = user, unsubscribe = unsubscribe)
        send_email_to_user(user = user, 
            subject = u"Ваше объявление перенесено в архив", 
            html = html, 
            unsubscribe = unsubscribe)

def notify_user_of_dog_adv_expired(user, adv):
    if user and db.check_subscribe(user.get("_id"), "expired"):
        from datetime import (datetime, timedelta)
        now = datetime.utcnow()
        left_days = (adv.get('expire_date').date() - now.date()).days
        unsubscribe = get_unsibscribe_link(user, "expired")
        html = env.get_template('notify_dog_adv_expired.html').render(adv = adv, left_days = left_days, user = user, unsubscribe = unsubscribe)
        send_email_to_user(user = user, 
            subject = u"Срок размещения вашего объявления истекает", 
            html = html, 
            unsubscribe = unsubscribe)

def notify_user_of_news(user, news):
    if user and db.check_subscribe(user.get('_id'), "news"):
        unsubscribe = get_unsibscribe_link(user, "news")
        html = env.get_template('notify_news.html').render(
            news = news, user = user, unsubscribe = unsubscribe)
        send_email_to_user(user = user, 
            subject = news.get('subject'), 
            html = html, 
            unsubscribe = unsubscribe)

def get_unsibscribe_link(user, subscribe):
    return u"%s/unsubscribe/%s/%s/" % (base_url, user.get('_id'), subscribe)

@run_async
def notify_users_of_news(users, news):
    for user in users:
        notify_user_of_news(user, news)


if __name__ == '__main__':
    func = sys.argv[1]
    args = "{0}".format(sys.argv[2:]).strip("[]")
    ex = '{0}({1})'.format(func, args )
    print(ex)
    eval(ex)