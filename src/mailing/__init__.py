#!/usr/bin/python
# -*- coding: utf-8 -*-


from smtplib import SMTP_SSL as SMTP

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 
import sys
from jinja2 import Template, Environment, PackageLoader
import config
import db
from helpers import run_async

env = Environment(loader=PackageLoader('mailing', ''))

@run_async
def send_email_async(From = u"Поводочек <%s>" % config.MAIL_USERNAME,
	To = [],
	Subject = u"Сообщение от портала Поводочек", 
	Text = u"",
	HTML = u""):
	send_email(From, To, Subject, Text, HTML)

def send_email(From = u"Поводочек <%s>" % config.MAIL_USERNAME,
	To = [],
	Subject = u"Сообщение от портала Поводочек", 
	Text = u"",
	HTML = u""):
	try:
		# Construct email
		msg = MIMEMultipart('alternative')
		msg['To'] = ", ".join([to.encode("utf-8") for to in To])
		msg['From'] = From.encode("utf-8")
		msg['Subject'] = Subject.encode("utf-8")

		 
		# Record the MIME types of both parts - text/plain and text/html.
		if Text:
			part1 = MIMEText(Text.encode("utf-8"), 'plain', "utf-8")
			msg.attach(part1)
		if HTML:
			part2 = MIMEText(HTML.encode("utf-8"), 'html', "utf-8")
			# Attach parts into message container.
			# According to RFC 2046, the last part of a multipart message, in this case
			# the HTML message, is best and preferred.
			msg.attach(part2)

		# Send the message via an SMTP server
		s = SMTP(config.MAIL_SERVER)
		s.login(config.MAIL_USERNAME,config.MAIL_PASSWORD)
		try:
			if not config.MAIL_SUPPRESS_SEND:
				s.sendmail(From, To, msg.as_string())
			else:
				print(To)
		finally:
			s.quit()
	except Exception, exc:
		print("mail failed; %s" % str(exc) ) # give a error message

@run_async
def send_email_to_users(Subject, HTML, users):
	counter = 0
	for user in users:
		counter += 1
		email = user.get('email')
		name = user.get('username')
		print(counter, name, email)
		to = [u"%s <%s>" % (name, email) if name != u"Пользователь" else email]
		send_email(HTML = HTML, Subject = Subject, To =  to)


def get_layout_template():
	return env.get_template('layout.html')

if __name__ == '__main__':
	func = sys.argv[1]
	args = "{0}".format(sys.argv[2:]).strip("[]")
	ex = '{0}({1})'.format(func, args )
	print(ex)
	eval(ex)