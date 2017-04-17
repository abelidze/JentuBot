# -*- coding: utf-8 -*-
import os
import telebot
from functions import de_token
from bottoken import token

# Yeah, it is here <-- cycle import
jentuBot = telebot.TeleBot(de_token(token))

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')

CELERY_BROKER = 'redis://127.0.0.1:8060//'

WEBHOOK_SSL_CERT = './ssl/jentu_cert.pem'
WEBHOOK_SSL_PRIV = './ssl/jentu_pkey.pem'
WEBHOOK_HOST 	 = '127.0.0.1'
WEBHOOK_PORT 	 = 443 # 443, 80, 88 or 8443
WEBHOOK_LISTEN 	 = '0.0.0.0'
WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (de_token(token))

WEBSERVER_HOST 	 = '127.0.0.1'
WEBSERVER_PORT 	 = 80
WEBSERVER_URL 	 = "http://%s:%s" % (WEBSERVER_HOST, WEBSERVER_PORT)
WEBSERVER_DB	 = './jentudb/jentu.db'

WEBHOOK_CONFIG = {
	'/':
	{
		'log.access_file': '',
		'log.error_file': '',
		'tools.staticdir.on': True,
		'tools.staticdir.root': CURRENT_PATH[:],
		'tools.staticdir.dir': '',
		'tools.staticfile.root': CURRENT_PATH[:]
	},

	'/favicon.ico':
	{
		'tools.staticfile.on': True,
		'tools.staticfile.filename': 'resource/favicon.ico'
	}
}

SERVER_CONFIG = {
	'server.socket_host': WEBHOOK_LISTEN,
	'server.socket_port': WEBHOOK_PORT,
	'server.ssl_module': 'builtin',
	'server.ssl_certificate': WEBHOOK_SSL_CERT,
	'server.ssl_private_key': WEBHOOK_SSL_PRIV,
	'log.screen': False
}