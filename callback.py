# -*- coding: utf-8 -*-
from telebot import types
from functions import log
from settings import jentuBot, LANG
from database import Goal, Achievement, User
from tasks import send_answer
from menu import menu_main, menu_play, menu_back, menu_settings, menu_support, menu_language, call_b_menu, call_b_save, call_b_delete

##################
##   Callback   ##
##################

### Callback functions ###
def saving_new(callback, user):
	log("SAVING-NEW, ", callback.from_user)
	user.update_user(state='naming')
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['save_new'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['saving'], reply_markup=menu_back)

def saving_this(callback, user):
	log("SAVING-THIS, ", callback.from_user)
	if(user.save_game()):
		result = 'saved'
	else:
		result = 'unsaved'

	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang][result])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang][result], reply_markup=menu_back)

def saving_other(callback, user):
	log("SAVING-OTHER, ", callback.from_user)
	markup_select = types.InlineKeyboardMarkup(row_width=1)
	for save in user.user_saves:
		markup_select.row(types.InlineKeyboardButton(text='\U0001F4BE {}'.format(save.title), callback_data='sg_{}'.format(save.id)))
	markup_select.row(call_b_save)
	markup_select.row(call_b_menu)

	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['save_start'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['save_start'], reply_markup=markup_select)

def saving_select(callback, user):
	log("SAVING-SELECT, ", callback.from_user)
	save_id = callback.data[3:]
	if(user.save_game(save_id=save_id)):
		result = 'saved'
	else:
		result = 'unsaved'

	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang][result])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang][result], reply_markup=menu_back)

def saving_delete(callback, user):
	log("SAVING-DELETE, ", callback.from_user)
	save_id = callback.data[3:]
	if(user.delete_game(save_id=save_id)):
		result = 'deleted'
	else:
		result = 'error'

	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang][result])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang][result], reply_markup=menu_back)

def call_menu(callback, user):
	log("CALLBACK-MAINMENU, ", callback.from_user)
	if(user.state != 'menu'):
		user.update_user(state='menu')
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption="Arios Jentu: Interactive fiction", reply_markup=menu_main)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['main_menu'])

def call_play(callback, user):
	log("CALLBACK-PLAYMENU, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['game'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['retry'], reply_markup=menu_play)

def call_load(callback, user):
	log("CALLBACK-LOAD, ", callback.from_user)
	markup_load = types.InlineKeyboardMarkup(row_width=2)
	for save in user.user_saves:
		markup_load.row(types.InlineKeyboardButton(text='\U0001F4C0 {}'.format(save.title), callback_data='go_{}'.format(save.id)))
	markup_load.row(call_b_save, call_b_delete)
	markup_load.row(call_b_menu)
	
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['call_load'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['load'], reply_markup=markup_load)

def call_save(callback, user):
	log("CALLBACK-SAVE, ", callback.from_user)
	markup_save = types.InlineKeyboardMarkup(row_width=1)
	if(user.saving != -1):
		markup_save.row(types.InlineKeyboardButton(text=LANG[user.lang]['save_this'], callback_data='save_this'))
	if(len(user.user_saves) > 0):
		markup_save.row(types.InlineKeyboardButton(text=LANG[user.lang]['save_other'], callback_data='save_other'))
	if(len(user.user_saves) < 5):
		markup_save.row(types.InlineKeyboardButton(text=LANG[user.lang]['save_new'], callback_data='save_new'))
	markup_save.row(call_b_menu)

	user.update_user(state='saving')
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['save_start'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['save_start'], reply_markup=markup_save)

def call_save_load(callback, user):
	log("CALLBACK-LOAD_SAVE, ", callback.from_user)
	saved_id = int(callback.data[3:])
	load_id = user.load_game(save_id=saved_id)
	if(load_id):
		log('SAVE-LOADED-{}'.format(saved_id))
		user.update_user(state='wait', saving=saved_id, checkpoint=load_id, menu_id=-1)
		jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['load_success'])
		jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['load_success'])
		send_answer.apply_async((callback.from_user.id, load_id, True), countdown=3)
	else:
		jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['load_failed'])
		jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['load_failed'], reply_markup=menu_back)

def call_save_delete(callback, user):
	log("CALLBACK-DELETE_SAVE, ", callback.from_user)
	markup_delete = types.InlineKeyboardMarkup(row_width=1)
	for save in user.user_saves:
		markup_delete.row(types.InlineKeyboardButton(text='\U0001F5D1 {}'.format(save.title), callback_data='er_{}'.format(save.id)))
	markup_delete.row(call_b_menu)

	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['save_delete'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['save_delete'], reply_markup=markup_delete)

def call_restart(callback, user):
	log("CALLBACK-RESTART, ", callback.from_user)
	user.restart_game()
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['loading'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['gg'])
	send_answer.apply_async((callback.from_user.id, 1, True), countdown=3)

def call_continue(callback, user):
	log("CALLBACK-CONTINUE, ", callback.from_user)
	user.update_user(state='wait', menu_id=-1)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['loading'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['story_go'])
	send_answer.apply_async((callback.from_user.id, user.checkpoint, True), countdown=3)

def call_archive(callback, user):
	log("CALLBACK-ARCHIVE, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['unavailable'])

def call_setting(callback, user):
	log("CALLBACK-SETTINGS, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['call_settings'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['settings'], reply_markup=menu_settings)

def call_support(callback, user):
	log("CALLBACK-SUPPORT, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['call_support'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['support'], reply_markup=menu_support)

def call_info(callback, user):
	log("CALLBACK-INFO, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['unavailable'], show_alert=True)

def call_email(callback, user):
	log("CALLBACK-EMAIL, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['unavailable'], show_alert=True)

def call_language(callback, user):
	log("CALLBACK-LANGUAGE, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['call_lang'])
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['lang'], reply_markup=menu_language)

def call_lang_ru(callback, user):
	log("CALLBACK-RUSSIAN, ", callback.from_user)
	user.update_user(lang='ru')
	jentuBot.answer_callback_query(callback.id, text=LANG['ru']['lang_changed'], show_alert=True)

def call_lang_en(callback, user):
	log("CALLBACK-ENGLISH, ", callback.from_user)
	user.update_user(lang='en')
	jentuBot.answer_callback_query(callback.id, text=LANG['en']['lang_changed'], show_alert=True)

def call_empty(callback, user):
	log("CALLBACK-EMPTY, ", callback.from_user)
	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['empty'])

def call_get_achievement(callback, user):
	goal_id = int(callback.data[3:])
	log("CALLBACK-ACHIVEMENT[{0}], ".format(goal_id), callback.from_user)
	try:
		goal = Goal.get(Goal.id == goal_id)
		jentuBot.answer_callback_query(callback.id, text="*{0}*\n\n\U0001F4DD: {1}".format(goal.achievement.name, goal.achievement.content), show_alert=True)
	except Goal.DoesNotExist:
		log("CALLBACK-STRANGE GOAL_ID FOR ", callback.from_user)
	except Achievement.DoesNotExist:
		log("CALLBACK-ILLEGAL GOAL FOR ", callback.from_user)

def call_achievements_list(callback, user):
	log("CALLBACK-ACHIVEMENTS, ", callback.from_user)
	i = 0
	buttons = []
	page = int(callback.data[3:])
	markup_achieve = types.InlineKeyboardMarkup(row_width=4)
	for goal in user.user_goals.join(Achievement).where(Goal.active == True, Achievement.visible == True).offset(page * 12).limit(13):
		i += 1
		if(i >= 13):
			break
		buttons.append(types.InlineKeyboardButton(text=goal.achievement.caption, callback_data='get{}'.format(goal.id)))

	j = i
	while(j < 12):
		buttons.append(types.InlineKeyboardButton(text='\U0001F512', callback_data='empty'))
		j += 1

	if(len(markup_achieve.keyboard) > 0):
		if(page > 0):
			buttons.append(types.InlineKeyboardButton(text=LANG[user.lang]['back'], callback_data='to_{}'.format(page - 1)))
		elif(i >= 13):
			buttons.append(types.InlineKeyboardButton(text=LANG[user.lang]['next'], callback_data='to_{}'.format(page + 1)))
	
	markup_achieve.add(*buttons)
	markup_achieve.row(call_b_menu)

	jentuBot.answer_callback_query(callback.id, text=LANG[user.lang]['call_achievements'].format(page + 1))
	jentuBot.edit_message_caption(chat_id=callback.message.chat.id, message_id=callback.message.message_id, caption=LANG[user.lang]['achieve_list'], reply_markup=markup_achieve)


### Making a dictionary of functions ###
callback_dictionary = {
	"menu": call_menu,
	"play": call_play,
	"load": call_load,
	"save": call_save,
	"save_new": saving_new,
	"save_this":saving_this,
	"save_other": saving_other,
	"delete": call_save_delete,
	"restart": call_restart,
	"continue": call_continue,
	"archive": call_archive,
	"setting": call_setting,
	"support": call_support,
	"info": call_info,
	"email": call_email,
	"lang": call_language,
	"lang_ru": call_lang_ru,
	"lang_en": call_lang_en,
	"sg_": saving_select,
	"er_": saving_delete,
	"get": call_get_achievement,
	"to_": call_achievements_list,
	"go_": call_save_load,
	"empty": call_empty,
}


### Main callback processor ###
def callback_processing(handler="menu", *args):
	return callback_dictionary[handler](*args)