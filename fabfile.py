#!/usr/bin/python
# -*- coding: utf-8 -*-

from fabric.api import *


env.roledefs = {
    'dev': ['192.168.222.167']
}
 
env.user = 'root'
env.password = "NET-admin557"

@roles('dev')
def deploy_dev():
	run('rm -fR /etc/apt/sources.list.d/mongodb.list')
	run("echo 'deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen' | tee /etc/apt/sources.list.d/mongodb.list")
	run('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
	run('apt-get update')
	run('apt-get install mongodb-10gen git emacs python-pip supervisor python-dev nginx libfreetype6-dev libjpeg8-dev')
	# jpeg decoder
	run('rm /usr/lib/libfreetype.so && ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/')
	run('rm /usr/lib/libz.so && ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/')
	run('rm /usr/lib/libjpeg.so && ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/')

	run('pip install virtualenv')
	run('rm -fR workon/povodochek && mkdir workon/povodochek')
	with cd('workon/povodochek'):
		run('virtualenv venv')
		run('source venv/bin/activate')
		run('git clone https://popovegor:Hdhsydn=03nd2@github.com/popovegor/povodochek.git')
		run('pip install -r ./povodochek/pip_reqs.txt')


