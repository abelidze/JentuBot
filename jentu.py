# -*- encoding: utf-8 -*-
from multiprocessing import Process, Queue
from signal import signal, SIGINT
from random import randint
import settings
import telebot
import sqlite3
import json
import time
# import os

#################
##  Threading  ##
#################
def signal_ctrl(signal, frame):
	print("You pressed Ctrl+C!\nShutdown broadcasting...")
	exit(0)

def broadcasting(jobs, ready):
	#info("Broadcasting")
	signal(SIGINT, signal_ctrl)
	timer = 0
	while True:
		timer = time.time()
		temp_list = []

		while not jobs.empty():
			task = jobs.get()

			if(timer-task[0] >= 2.0):
				if(task[0] < 1.0):
					answer_markup = telebot.types.ReplyKeyboardRemove()
				else:
					answer_markup = None

				message = task[3][0]
				del task[3][0]
				task[0] = time.time()

				if task[3]:
					temp_list.append(task)
				elif task[4]:
					answer_markup = telebot.types.ReplyKeyboardMarkup(True, True)
					for edge in task[4]:
						answer_markup.row(edge[2])

				if(message[0] == 't'):
					bot.send_message(task[1], message[1], reply_markup=answer_markup, disable_notification=True, parse_mode="Markdown")
				elif(message[0] == 'i'):
					bot.send_photo(task[1], message[1], reply_markup=answer_markup, disable_notification=True)

				ready.put(task[2])
				break
			else:
				temp_list.append(task)

		for job in temp_list:
			jobs.put(job)

		delta = 0.025 - time.time() + timer
		if(delta > 0.0):
			time.sleep(delta)


#################
##  Main-only  ##
#################
if(__name__ == '__main__'):

	# Game Data
	story = []
	users = {}
	tasks = Queue()
	user_states = Queue()

	# Connect SQLite
	dataDB = sqlite3.connect('data.db', check_same_thread=False)
	dataEX = dataDB.cursor()

	# Loading Story
	dataEX.execute("SELECT * FROM answer ORDER BY id")
	dataDB.commit()
	for row in dataEX:
		story.append(json.loads(row[1]))
	#print(story[0][1][1][2])

	# Loading Users
	dataEX.execute("SELECT * FROM users WHERE id != 0")
	dataDB.commit()
	print("USERS:")
	for row in dataEX:
		users[row[0]] = [row[1], row[2], True]
		print("-> user", row[0], "-----", users[row[0]])

	# SQLite Functions
	def new_user(message):
		dataEX.execute("""
			INSERT INTO users (id, save, archivement)
			SELECT {0}, {1}, '{2}' FROM users
			WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = {0} LIMIT 1)
			LIMIT 1""".format(str(message.from_user.id), '0', '[]'))
		dataDB.commit()
		users[message.from_user.id] = [0,'[]',True]
		#users[row[0]] = [row[1], row[2]]
	#usersEX.execute('CREATE TABLE users (id INTEGER NOT NULL PRIMARY KEY, save INTEGER NOT NULL, archivement TEXT)')

	# Debug logging
	def log(info, message):
		print("\n______________________________________LOG______________________________________")
		print("From: {0} {1}; Info: {2}".format(message.from_user.first_name, message.from_user.last_name, info))
		print("Text: " + message.text)
		print("_______________________________________________________________________________")


#################
##   TeleBot   ##
#################

# Initialize TeleBot
bot = telebot.TeleBot(settings.drink(settings.vodka))

# Start session
@bot.message_handler(commands=['start'])
def send_welcome(message):
	new_user(message)
	users[message.from_user.id][2] = False
	tasks.put([0.0, message.chat.id, message.from_user.id, story[0][2], story[0][1]])
	log("START", message)

# Stop
@bot.message_handler(commands=['stop'])
def send_wtf(message):
	stop_markup = telebot.types.ReplyKeyboardRemove()
	bot.reply_to(message, "WTF?! NO!", reply_markup=stop_markup)
	log("STOP", message)

# Parsing Text
@bot.message_handler(content_types=['text'])
def send_answer(message):
	if(message.text == "kekos"):
		bot.reply_to(message, "privetos")
		if(message.from_user.id in users):
			bot.send_message(message.chat.id, "Oh, I know who are you!")
	else:
		user_id = message.from_user.id
		answer_id = message.chat.id
		okay = False

		if(not users[user_id][2]):
			while not user_states.empty():
				user_id = user_states.get()
				users[user_id][2] = True
				if(user_id == message.from_user.id):
					okay = True
					break
		else:
			okay = True

		if(okay):
			wrong = True
			for edge in story[users[user_id][0]][1]:
				if(message.text == edge[2]):
					users[user_id][0] = edge[0]
					users[user_id][2] = False
					wrong = False
					tasks.put([0.0, answer_id, user_id, story[edge[0]][2], story[edge[0]][1]])
					break
			if(wrong):
				bot.send_message(answer_id, "Хм.. что-то пошло не так!")
	log("TEXT", message)


################
##    MAIN    ##
################
if(__name__ == '__main__'):
	broad = Process(target=broadcasting, args=(tasks, user_states))
	broad.start()
	print("JentuBot started! <-> ['Ctrl+C' to shutdown]")
	bot.polling(none_stop=True, interval=0)

# def info(title):
# 	print("!#", title, "...")
# 	print("... working on process:", os.getpid(), "<=> Parent:", os.getppid())