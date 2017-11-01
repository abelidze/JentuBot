# -*- coding: utf-8 -*-
import sys
from celery import Celery
from telebot import types
from settings import jentuBot, CELERY_BROKER
from database import Answer, Response, User, Achievement, Goal
from functions import parse_logic

################
##   Celery   ##
################

TaskQueue = Celery('tasks', broker=CELERY_BROKER) #, include=['tasks'])

@TaskQueue.task
def send_message(message_type, *args, **kwargs):
	if(message_type == 'text'):
		jentuBot.send_message(*args, **kwargs)
	elif(message_type == 'photo'):
		jentuBot.send_photo(*args, **kwargs)
	elif(message_type == 'reply'):
		jentuBot.reply_to(*args, **kwargs)

@TaskQueue.task
def send_answer(user_id, answer_id, force_mode=False):

	# Try to get user
	try:
		user = User.get(User.user_id == user_id)
	except User.DoesNotExist:
		return 'No such user->%d!' % (user_id)

	# Check user_state
	if(user.state != 'wait') and (not force_mode):
		user.update_user(checkpoint=answer_id)
		return 'Stop state for user->%d!' % (user_id)

	# Try to get answer
	try:
		answer = Answer.get(Answer.answer_id == answer_id)
	except Answer.DoesNotExist:
		return 'No such message for %d!' % (user_id)

	# Try to get next message
	try:
		next_answer = answer.next_id
	except Answer.DoesNotExist:
		jentuBot.send_message(user_id, (answer.message + "\n*ПРОДОЛЖЕНИЕ ВРЕМЕННО НЕДОСТУПНО :(*\nПриносим свои извинения."), disable_notification=True, parse_mode="Markdown")
		return 'Failed to get message for %d!' % (user_id)

	# Keyboard markup
	answer_markup = types.ReplyKeyboardMarkup(True, False)
	answer_markup.row("\U0001F4DC Открыть меню")

	# Inline markup
	inline_markup = None

	# Handle response
	if(next_answer == None):

		# Inline markup
		inline_markup = types.InlineKeyboardMarkup(row_width=1)

		# Make a reply markup
		if(len(answer.markups) > 0):

			# Check all attached responses to this answer
			for resp in answer.markups:
				# Check a requirement for this response
				try:
					OK = True
					temp = resp.requirement.replace(' ', '')
					if(temp != ''):
						# Check objectives
						check_data = [(goal.achievement.achievement_id) for goal in user.user_goals.join(Achievement).where(Goal.active == True)]
						OK = parse_logic(temp, check_data)
				except:
					print(sys.exc_info())

				if OK:
					# Auto-answer
					if(resp.text.replace(' ', '') == ''):
						send_answer.apply_async((user_id, resp.next_id, True), countdown=answer.delay)
						if(answer.force_send):
							inline_markup = None
							break
						else:
							return 'Delayed to %d!' % (user_id)

					# Add markup
					inline_button = types.InlineKeyboardButton(text=resp.text, callback_data="r_{}".format(str(resp.id)))
					inline_markup.row(inline_button)
	else:
		# Put next message to Celery
		send_answer.apply_async((user_id, next_answer), countdown=answer.delay)

	# Send messages depending on type
	if(answer.message_type == 'image'):
		jentuBot.send_photo(user_id, answer.message, reply_markup=answer_markup, disable_notification=True)
	else:
		jentuBot.send_message(user_id, answer.message, reply_markup=answer_markup, disable_notification=True, parse_mode="Markdown")

	if(inline_markup != None):
		# Update user checkpoint and state; Send response
		user.update_user(state='response', checkpoint=answer.answer_id)
		jentuBot.send_message(user_id, '\U0001F5EF *Выбери действие:*', reply_markup=inline_markup, disable_notification=True, parse_mode="Markdown")

	return 'Sent to %d!' % (user_id)