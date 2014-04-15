#!/usr/bin/python
# -*- coding: utf-8 -*-

import db
import config

from smtplib import SMTP_SSL as SMTP

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
import sys
from jinja2 import Template, Environment, PackageLoader

env = Environment(loader=PackageLoader('scripts', \
	'mail_templates'))

def send_email(From = u"Поводочек <%s>" % config.MAIL_USERNAME, \
	To = "popovegor.ati@gmail.com", \
	Subject = u"Сообщение от портала Поводочек", Text = u"", \
	HTML = u""):
	try:
		 
		# Construct email
		msg = MIMEMultipart('alternative')
		msg['To'] = To.encode("utf-8")
		msg['From'] = From.encode("utf-8")
		msg['Subject'] = Subject.encode("utf-8")

		 
		# Record the MIME types of both parts - text/plain and text/html.
		part1 = MIMEText(Text.encode("utf-8"), 'plain', "utf-8")
		part2 = MIMEText(HTML.encode("utf-8"), 'html', "utf-8")
		 
		# Attach parts into message container.
		# According to RFC 2046, the last part of a multipart message, in this case
		# the HTML message, is best and preferred.
		msg.attach(part1)
		msg.attach(part2)
		 
		# Send the message via an SMTP server
		s = SMTP(config.MAIL_SERVER)
		s.login(config.MAIL_USERNAME,config.MAIL_PASSWORD)
		try:
			s.sendmail(From, To, msg.as_string())
		finally:
			s.quit()
	except Exception, exc:
		sys.exit( "mail failed; %s" % str(exc) ) # give a error message

def send_notifications_1():
	counter = 0
	for user in db.users.find():
		advs_count = db.get_dog_advs_by_user(user.get('_id')).count()	
		email = user.get('email')
		name = user.get('username')
		if advs_count <= 0:
			counter += 1
			print(counter, name, email)
			to = u"%s <%s>" % (name, email) if name != u"Пользователь" else email
			template = env.get_template('notifications_1.html')
			send_email(HTML = template.render(),\
				Subject = u"Изменения в публикации объявлений на сайте Поводочек.рф", \
				To =  to )

def send_notifications_attraction():
	counter = 0
	for user in db.users.find():
		counter += 1
		email = user.get('email')
		name = user.get('username')
		print(counter, name, email)
		to = u"%s <%s>" % (name, email) if name != u"Пользователь" else email
		template = env.get_template('notifications_attraction.html')
		send_email(HTML = template.render(),\
			Subject = u"Привлекательность объявлений на сайте Поводочек.рф", \
			To =  to )


def send_news_video():
	counter = 0
	for user in db.users.find():
		counter += 1
		email = user.get('email')
		name = user.get('username')
		print(counter, name, email)
		to = u"%s <%s>" % (name, email) if name != u"Пользователь" else email
		template = env.get_template('news_video.html')
		send_email(HTML = template.render(),\
			Subject = u"Новости проекта Поводочек.рф: фильм, фильм, фильм!", \
			To =  to )


if __name__ == '__main__':
	eval('{0}()'.format(sys.argv[1]))