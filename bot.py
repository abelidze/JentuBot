# -*- coding: utf-8 -*-
from telebot import types
from functions import log, get_handler
from callback import callback_processing
from settings import jentuBot, MENU_BACKGROUND, LANG
from database import Response, User
from tasks import send_answer, send_message
from menu import menu_main, menu_play, call_b_menu, menu_back

#################
##   TeleBot   ##
#################

# Start session
@jentuBot.message_handler(commands=['start'])
def start_broadcasting(message):
	log("START-", message.from_user)
	user, created = User.create_user(message)
	if(created):
		user.update_user(state='wait')
		send_answer.apply_async((message.from_user.id, 1, True), countdown=3)
	else:
		if(user.state != 'menu'):
			markup = types.ReplyKeyboardMarkup(True, False)
			markup.row(LANG[user.lang]['continue'])

			if(user.menu_id != -1):
				jentuBot.edit_message_caption(chat_id=message.from_user.id, message_id=user.menu_id, caption=LANG[user.lang]['old_form'])

			jentuBot.send_message('text', message.from_user.id, LANG[user.lang]['menu_label'], reply_markup=markup, disable_notification=True, parse_mode="Markdown")
			msg = jentuBot.send_photo(message.from_user.id, MENU_BACKGROUND, caption=LANG[user.lang]['play'], reply_markup=menu_play, disable_notification=True)

			user.update_user(state='menu', menu_id=msg.message_id)
		else:
			if(user.menu_id != -1):
				jentuBot.edit_message_caption(chat_id=message.from_user.id, message_id=user.menu_id, caption=LANG[user.lang]['hide_menu'])

			user.update_user(state='wait', menu_id=-1)
			send_answer.apply_async((message.from_user.id, user.checkpoint, True), countdown=3)


# Stop session
@jentuBot.message_handler(commands=['stop'])
def stop_broadcasting(message):
	# Get user
	user = User.get_user(message, "STOP-ERROR GETTING ")
	if(user == None):
		return None

	if(user.menu_id != -1):
		jentuBot.edit_message_caption(chat_id=message.from_user.id, message_id=user.menu_id, caption=LANG[user.lang]['old_form'])

	log("STOP-", message.from_user)
	user.update_user(state='stop', menu_id=-1)
	send_message.delay('reply', message, LANG[user.lang]['bye'], reply_markup=types.ReplyKeyboardRemove())


# Open/hide menu
@jentuBot.message_handler(commands=['menu'])
def menu_handler(message):
	# Get user
	user = User.get_user(message, "OPEN_MENU-ERROR GETTING ")
	if(user == None):
		return None

	# Delete response if exists
	try:
		jentuBot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id-1, reply_markup=None)
	except:
		pass

	# Check user state
	if(user.menu_id != -1):
		log("OPEN_MENU-HIDE FOR ", message.from_user)
		jentuBot.edit_message_caption(chat_id=message.from_user.id, message_id=user.menu_id, caption=LANG[user.lang]['hide_menu'])
		menu = -1
	else:
		log("OPEN_MENU-OPEN FOR ", message.from_user)
		markup = types.ReplyKeyboardMarkup(True, False)
		markup.row(LANG[user.lang]['continue'])
		jentuBot.send_message(message.from_user.id, LANG[user.lang]['menu_label'], reply_markup=markup, disable_notification=True, parse_mode="Markdown")
		menu = (jentuBot.send_photo(message.from_user.id, MENU_BACKGROUND, caption="Arios Jentu: Interactive fiction", reply_markup=menu_main, disable_notification=True)).message_id
	user.update_user(state='menu', menu_id=menu)


# Save game
@jentuBot.message_handler(commands=['save'])
def save_handler(message):
	# Get user
	user = User.get_user(message, "SAVE_START-ERROR GETTING ")
	if(user == None):
		return None

	log("SAVE-", message.from_user)
	markup_save = types.InlineKeyboardMarkup(row_width=1)
	if(user.saving != -1):
		markup_save.row(types.InlineKeyboardButton(text=LANG[user.lang]['save_this'], callback_data='save_this'))
	if(len(user.user_saves) > 0):
		markup_save.row(types.InlineKeyboardButton(text=LANG[user.lang]['save_other'], callback_data='save_other'))
	if(len(user.user_saves) < 5):
		markup_save.row(types.InlineKeyboardButton(text=LANG[user.lang]['save_new'], callback_data='save_new'))
	markup_save.row(call_b_menu)

	if(user.menu_id != -1):
		jentuBot.edit_message_caption(chat_id=message.from_user.id, message_id=user.menu_id, caption=LANG[user.lang]['save_start'], reply_markup=markup_save)
	else:
		menu = (jentuBot.send_photo(message.from_user.id, MENU_BACKGROUND, caption=LANG[user.lang]['save_start'], reply_markup=markup_save, disable_notification=True)).message_id
	user.update_user(state='saving', menu_id=menu)


# Parsing Callback
@jentuBot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
	if(call.message):
		# Get user
		user = User.get_user(call, "CALLBACK-NO_")
		if(user == None):
			send_message.delay(call.from_user.id, LANG['en']['call_unknown'], reply_markup=types.ReplyKeyboardRemove())
			return None

		# Temporary and in-progress

		### MAIN-MENU ###
		if(call.data == 'menu'):
			callback_processing('menu', call, user)

		### MENU ###
		elif(user.state == 'menu'):
			try:
				callback_processing(get_handler(call.data), call, user)
			except:
				log("CALLBACK[{}]-PROCESSING-ERROR, ".format(call.data), call.from_user)

		### SAVE ###
		elif(user.state == 'saving'):
			try:
				callback_processing(get_handler(call.data), call, user)
			except:
				log("CALLBACK[{}]-SAVING-ERROR, ".format(call.data), call.from_user)

		### RESPONSE ###
		elif(user.state == 'response') and (call.data[:2] == 'r_'):
			# If Response -> Check an answer
			try:
				choice = Response.get(Response.id == int(call.data[2:]))

				# Check validation
				if(choice.answer_id != user.checkpoint):
					log("CALLBACK-WRONG CHECKPOINT FOR ", call.from_user)
					jentuBot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=LANG[user.lang]['old_form'])

				else:
					log("CALLBACK-RESPONSE[{0}], ".format(call.data), call.from_user)
					next_answer = choice.next_id
					if(next_answer != None):
						# Save choice
						user.update_user(checkpoint=next_answer, state='wait')

						# Process/give achievement if exists
						if user.process_achievement(achieve_id=choice.achieve_id):
							if choice.achieve_id.visible:
								jentuBot.answer_callback_query(call.id, text=LANG[user.lang]['call_achieve'].format(choice.achieve_id.name))

						# Edit message text
						jentuBot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=('\U0000270F *{}*'.format(choice.text)), parse_mode="Markdown")

						# Next message to Celery
						send_answer.apply_async((call.from_user.id, next_answer, True), countdown=3)

						# If restart
						if(choice.id == 0):
							user.restart_goals()
					else:
						send_message.delay(call.from_user.id, LANG[user.lang]['gameover'])

			except Response.DoesNotExist:
				send_message.delay(call.from_user.id, LANG[user.lang]['again'])

			except Answer.DoesNotExist:
				send_message.delay(call.from_user.id, LANG[user.lang]['end'])

		### EXPIRED ###
		else:
			log("CALLBACK-EXPIRED STATE FOR ", call.from_user)
			jentuBot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=LANG[user.lang]['old_form'])

	else:
		log("INLINE OR CORRUPTED CALLBACK")


# Receiving Images with LOG
@jentuBot.message_handler(content_types=['photo'])
def recieve_photo(message):
	log("IMAGE-", message.from_user)
	for image in message.photo:
		print(image)


# Parsing Text
@jentuBot.message_handler(content_types=['text'])
def parse_text(message):
	log("TEXT-", message.from_user)

	if(message.text == "kekos"):
		jentuBot.reply_to(message, "privetos")
	else:
		# Get user
		user = User.get_user(message, "ERROR GETTING ")
		if(user == None):
			jentuBot.send_message(message.from_user.id, LANG['en']['unknown'], reply_markup=types.ReplyKeyboardRemove())

		elif(user.state == 'naming'):
			log("SAVE-NAMING FOR ", message.from_user)
			user.update_user(state='menu')

			# Save game
			if(user.save_game(caption=message.text[:20])):
				result = 'saved'
			else:
				result = 'unsaved'

			# Send result
			jentuBot.edit_message_caption(chat_id=message.chat.id, message_id=user.menu_id, caption=LANG[user.lang][result], reply_markup=menu_back)

		elif(user.state == 'menu'):
			if(message.text == LANG[user.lang]['continue']):
				# Continue game
				user.update_user(state='wait')
				send_answer.apply_async((message.from_user.id, user.checkpoint, True), countdown=3)

				# Close menu
				jentuBot.edit_message_caption(chat_id=message.from_user.id, message_id=user.menu_id, caption=LANG[user.lang]['story_go'])
				user.update_user(menu_id=-1)

		elif(message.text == LANG[user.lang]['open_menu']):
			# Open menu
			markup = types.ReplyKeyboardMarkup(True, False)
			markup.row(LANG[user.lang]['continue'])
			user.update_user(state='menu')
			jentuBot.send_message(message.from_user.id, LANG[user.lang]['menu_label'], reply_markup=markup, disable_notification=True, parse_mode="Markdown")
			msg = jentuBot.send_photo(message.from_user.id, MENU_BACKGROUND, caption=LANG[user.lang]['play'], reply_markup=menu_play, disable_notification=True)
			user.update_user(menu_id=msg.message_id)

			# Delete response if exists
			try:
				jentuBot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id-1, reply_markup=None)
			except:
				pass

		else:
			log("WRONG TEXT-", message.from_user)