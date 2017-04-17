# -*- coding: utf-8 -*-
from telebot import types
from functions import log
from settings import jentuBot
from database import Response, User, get_user
from tasks import send_answer

#################
##   TeleBot   ##
#################

# Start session
@jentuBot.message_handler(commands=['start'])
def start_broadcasting(message):
	user = get_user(message)
	send_answer.delay(message.chat.id, message.from_user.id, user.checkpoint)
	log("START", message)

# Stop
@jentuBot.message_handler(commands=['stop'])
def send_wtf(message):
	jentuBot.reply_to(message, "WTF?! NO!", reply_markup=types.ReplyKeyboardRemove())
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