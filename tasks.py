# -*- coding: utf-8 -*-
import telebot
from celery import Celery
from settings import jentuBot, CELERY_BROKER
from database import Answer, Response, User

################
##   Celery   ##
################

TaskQueue = Celery('tasks', broker=CELERY_BROKER) #, include=['tasks'])

@TaskQueue.task
def send_answer(chat_id, user_id, answer_id, markup=True):
	try:
		# Try to get answer
		answer = Answer.get(Answer.id == answer_id)
		answer_markup = None
		
		if(answer.next_id == None):
			# Update user checkpoint
			User.update(checkpoint=answer.id).where(User.id == user_id).execute()

			# Make a reply markup
			if(len(answer.markups) > 0):
				answer_markup = telebot.types.ReplyKeyboardMarkup(True, True)
				for resp in answer.markups:
					answer_markup.row(resp.text)
		else:
			# Put next message to Celery
			send_answer.apply_async((chat_id, user_id, answer.next_id, False), countdown=answer.delay)

			# Using for first message after markup
			if(markup):
				answer_markup = telebot.types.ReplyKeyboardRemove()

		# Send messages depending on type
		if(answer.message_type == 'image'):
			jentuBot.send_photo(chat_id, answer.message, reply_markup=answer_markup, disable_notification=True)
		else:
			jentuBot.send_message(chat_id, answer.message, reply_markup=answer_markup, disable_notification=True, parse_mode="Markdown")

		return 'Sent to %d!' % (user_id)

	except Answer.DoesNotExist:
		return 'No such message!'