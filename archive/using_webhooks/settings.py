# -*- coding: utf-8 -*-
def to_ascii(h):
	strs = ""
	for i in range(len(h)//2):
		strs += chr(int(h[(i*2):(i*2)+2], 16))
	return strs

# Just drink it
def drink(message):
	message = to_ascii(message)
	for i, v in enumerate(message):
		message = message[:i] + chr(ord(v)+12) + message[i+1:]
	return message

# Debug logging
def log(info, message):
	print("\n______________________________________LOG______________________________________")
	print("From: {0} {1}; Info: {2}".format(message.from_user.first_name, message.from_user.last_name, info))
	print("Text: " + message.text)
	print("_______________________________________________________________________________")

vodka = "TELEGRAM-BOT-KEY"

# import os
# CURRENT_PATH = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')

DATABASE = './jentudb/jentu.db'

WEBHOOK_CONFIG = './config/jentu.conf'
WEBHOOK_SSL_CERT = './ssl/jentu_cert.pem'
WEBHOOK_SSL_PRIV = './ssl/jentu_pkey.pem'

WEBHOOK_HOST = 'TELEGRAM-SERVER-ADDRESS'
WEBHOOK_PORT = 443 # 443, 80, 88 или 8443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (drink(vodka))

WEBSERVER_HOST = '127.0.0.1'
WEBSERVER_PORT = 80
WEBSERVER_URL = "http://%s:%s" % (WEBSERVER_HOST, WEBSERVER_PORT)

server_config = {
	'server.socket_host': WEBHOOK_LISTEN,
	'server.socket_port': WEBHOOK_PORT,
	'server.ssl_module': 'builtin',
	'server.ssl_certificate': WEBHOOK_SSL_CERT,
	'server.ssl_private_key': WEBHOOK_SSL_PRIV,
	'log.screen': True
}
