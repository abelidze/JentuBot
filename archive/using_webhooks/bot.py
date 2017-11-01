# -*- coding: utf-8 -*-
from settings import *
from database import *
import cherrypy
import telebot
if __name__ == '__main__':
	from datetime import datetime
	from tasks import send_answer


################
##   PeeWee   ##
################

	# Just for safe
	jentuDB.connect()
	jentuDB.create_tables([User, Answer, Response], safe=True)

	# SQLite Functions
	@jentuDB.transaction()
	def new_user(message):
		return User.get_or_create(id=message.from_user.id, defaults={"username": message.from_user.first_name, "checkpoint": 1, "achievement": '[]'})[0]


#################
##   TeleBot   ##
#################

# Initialize TeleBot
jentuBot = telebot.TeleBot(drink(vodka))

# Start session
@jentuBot.message_handler(commands=['start'])
def start_broadcasting(message):
	user = new_user(message)
	send_answer.delay(message.chat.id, message.from_user.id, user.checkpoint)
	log("START", message)

# Stop
@jentuBot.message_handler(commands=['stop'])
def send_wtf(message):
	jentuBot.reply_to(message, "WTF?! NO!", reply_markup=telebot.types.ReplyKeyboardRemove())
	log("STOP", message)

# Parsing Text
@jentuBot.message_handler(content_types=['text'])
def parse_response(message):
	if(message.text == "kekos"):
		jentuBot.reply_to(message, "privetos")
	else:
		# Get user
		user = User.get(User.id == message.from_user.id)
		wrong = True

		# Check an answer
		for choice in Response.select().where(Response.id == user.checkpoint):
			if(choice.text == message.text):
				if(choice.next_id != None):
					# Save choice
					user.checkpoint = choice.next_id
					user.save()

					# Next message to Celery
					send_answer.delay(message.chat.id, message.from_user.id, user.checkpoint)
				else:
					entuBot.send_message(message.chat.id, 'Это конец игры, такие ситуации пока еще не обрабатываются :(')
				wrong = False
				break
		if(wrong):
			jentuBot.send_message(message.chat.id, 'Хм... попробуй еще раз!')
	log("TEXT", message)


##################
##   CherryPy   ##
##################

class WebhookServer(object):
	@cherrypy.expose
	def index(self):
		if 'content-length' in cherrypy.request.headers and 'content-type' in cherrypy.request.headers and cherrypy.request.headers['content-type'] == 'application/json':

			# Recieve update
			length = int(cherrypy.request.headers['content-length'])
			json_string = cherrypy.request.body.read(length).decode("utf-8")
			update = telebot.types.Update.de_json(json_string)

			# Updates
			jentuBot.process_new_updates([update])
			return ''
		else:
			raise cherrypy.HTTPError(403)
			# raise cherrypy.HTTPRedirect(WEBSERVER_URL)

################
##    MAIN    ##
################

if __name__ == '__main__':

	# WebHooks
	jentuBot.remove_webhook()
	jentuBot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))

	# Started (no :D)
	print(datetime.now().strftime("[%d/%b/%Y:%H:%M:%S]"), "JentuBot started! <-> ['Ctrl+C' to shutdown]")

	# Start framework
	cherrypy.config.update(server_config)
	cherrypy.engine.subscribe('before_request', jentuDB_connect)
	cherrypy.engine.subscribe('after_request', jentuDB_close)
	cherrypy.quickstart(WebhookServer(), WEBHOOK_URL_PATH, WEBHOOK_CONFIG)

	# But if you want a long polling...
	# jentuBot.polling(none_stop=True, interval=0)

	# Shutdown :c
	print(datetime.now().strftime("[%d/%b/%Y:%H:%M:%S]"), "JentuBot: Bye Bye!")