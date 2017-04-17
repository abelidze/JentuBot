# -*- coding: utf-8 -*-
import cherrypy
from telebot import types
from database import jentuDB_connect, jentuDB_close
from settings import SERVER_CONFIG, WEBHOOK_CONFIG, WEBHOOK_URL_PATH, jentuBot

##################
##   CherryPy   ##
##################

# Basic application class (CherryPy class)
class WebhookApplication(object):
	@cherrypy.expose
	def index(self):
		if 'content-length' in cherrypy.request.headers \
		and 'content-type' in cherrypy.request.headers \
		and cherrypy.request.headers['content-type'] == 'application/json':

			# Recieve update
			length = int(cherrypy.request.headers['content-length'])
			json_string = cherrypy.request.body.read(length).decode("utf-8")
			update = types.Update.de_json(json_string)

			# Updates
			jentuBot.process_new_updates([update])
			return ''
		else:
			raise cherrypy.HTTPError(403)
			# raise cherrypy.HTTPRedirect(WEBSERVER_URL)


# Basic server class (Bot class)
class WebhookServer(object):
	def __init__(self):
		cherrypy.tree.mount(WebhookApplication(), WEBHOOK_URL_PATH, WEBHOOK_CONFIG)

	# a blocking call that starts the web application listening for requests
	def start(self, config=SERVER_CONFIG):
		cherrypy.config.update(config)
		cherrypy.engine.subscribe('before_request', jentuDB_connect)
		cherrypy.engine.subscribe('after_request', jentuDB_close)
		cherrypy.engine.signals.subscribe()

		cherrypy.engine.start()
		cherrypy.engine.block()

	# stops the web application
	def stop(self):
		cherrypy.engine.stop()