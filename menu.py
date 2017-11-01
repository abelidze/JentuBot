# -*- coding: utf-8 -*-
from telebot import types

# Buttons
call_b_menu = types.InlineKeyboardButton(text="\U0001F4DC Главное меню", callback_data='menu')

call_b_play = types.InlineKeyboardButton(text="\U0001F3AE Вернуться к игре", callback_data='play')
call_b_load = types.InlineKeyboardButton(text="\U0001F4BD Сохранения", callback_data='load')
call_b_achieve = types.InlineKeyboardButton(text="\U0001F4A1 Достижения", callback_data='to_0')
call_b_archive = types.InlineKeyboardButton(text="\U0001F4D6 Архиварий", callback_data='archive')
call_b_setting = types.InlineKeyboardButton(text="\U00002699 Настройки", callback_data='setting')
call_b_support = types.InlineKeyboardButton(text="\U0001F4AC Поддержка", callback_data='support')

call_b_ach_next = types.InlineKeyboardButton(text="Далее \U000027A1", callback_data='an_')
call_b_ach_prev = types.InlineKeyboardButton(text="\U00002B05 Назад", callback_data='ap_')

call_b_lang = types.InlineKeyboardButton(text="\U0001F310 Язык", callback_data='lang')
call_b_info = types.InlineKeyboardButton(text="\U00002139 Информация", callback_data='info')

call_b_type = types.InlineKeyboardButton(text="\U00002709 Написать нам", callback_data='email')
call_b_site = types.InlineKeyboardButton(text="\U0001F4BB Сайт игры", url='http://jentubot.xyz')

call_b_lang_ru = types.InlineKeyboardButton(text="🇷🇺 Русский", callback_data='lang_ru')
call_b_lang_en = types.InlineKeyboardButton(text="🇺🇸 English", callback_data='lang_en')

call_b_restart = types.InlineKeyboardButton(text="\U0001F503 Заново", callback_data='restart')
call_b_continue = types.InlineKeyboardButton(text="\U0001F3AC Продолжить", callback_data='continue')

call_b_save = types.InlineKeyboardButton(text="\U0001F4BE Сохранить", callback_data='save')
call_b_delete = types.InlineKeyboardButton(text="\U0001F5D1 Удалить", callback_data='delete')

call_b_yeap = types.InlineKeyboardButton(text="\U00002705 Да", callback_data='save')
call_b_nope = types.InlineKeyboardButton(text="\U000026A0 Нет", callback_data='restart')


# Markups
menu_main = types.InlineKeyboardMarkup(row_width=1)
menu_play = types.InlineKeyboardMarkup(row_width=2)
menu_back = types.InlineKeyboardMarkup(row_width=1)
menu_confirm = types.InlineKeyboardMarkup(row_width=2)
menu_support = types.InlineKeyboardMarkup(row_width=2)
menu_settings = types.InlineKeyboardMarkup(row_width=2)
menu_language = types.InlineKeyboardMarkup(row_width=2)


# Main menu
menu_main.row(call_b_play)
menu_main.row(call_b_load)
menu_main.row(call_b_achieve)
menu_main.row(call_b_archive)
menu_main.row(call_b_setting)
menu_main.row(call_b_support)


# Play game
menu_play.row(call_b_restart, call_b_continue)
menu_play.row(call_b_menu)


# Backmenu
menu_back.row(call_b_menu)


# Confirm menu
menu_confirm.row(call_b_yeap, call_b_nope)
menu_confirm.row(call_b_menu)


# Support
menu_support.row(call_b_type, call_b_site)
menu_support.row(call_b_menu)


# Settings
menu_settings.row(call_b_lang, call_b_info)
menu_settings.row(call_b_menu)


# Language select
menu_language.row(call_b_lang_ru, call_b_lang_en)
menu_language.row(call_b_menu)