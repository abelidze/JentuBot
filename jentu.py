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

def broadcasting(jobs):
	#info("Broadcasting")
	signal(SIGINT, signal_ctrl)
	timer = 0
	while True:
		timer = time.time()
		temp_list = []

		while not jobs.empty():
			task = jobs.get()

			if timer-task[0] >= 2:
				if task[2][0][0] == 't':
					bot.send_message(task[1], task[2][0][1])
				task[0] = time.time()
				del task[2][0]
				if task[2]:
					temp_list.append(task)
				break
			else:
				temp_list.append(task)

		for job in temp_list:
			jobs.put(job)

		time.sleep(0.025)


#################
##  Main-only  ##
#################
if __name__ == '__main__':

	# Game Data
	chapter1 = []
	users = {}
	tasks = Queue()

	# Loading Story
	storyDB = sqlite3.connect('story.db')
	storyEX = storyDB.cursor()
	storyEX.execute("SELECT * FROM chapter1 ORDER BY id")
	storyDB.commit()
	for row in storyEX:
		chapter1.append(json.loads(row[1]))
	storyDB.close()
	#print(chapter1[0][1][1][2])

	# Loading Users
	usersDB = sqlite3.connect('users.db', check_same_thread=False)
	usersEX = usersDB.cursor()
	usersEX.execute("SELECT * FROM users WHERE id != 0")
	usersDB.commit()
	for row in usersEX:
		users[row[0]] = [row[1], row[2]]
		print("User", row[0], "-----", users[row[0]])

	# SQLite Functions
	def new_user(message):
		usersEX.execute("""
			INSERT INTO users (id, save, archivement)
			SELECT {0}, '{1}', '{2}' FROM users
			WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = {0} LIMIT 1)
			LIMIT 1""".format(str(message.from_user.id), '0', '[]'))
		usersDB.commit()
		users[message.from_user.id] = ['0','[]']
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
	tasks.put([time.time()-3, message.chat.id, chapter1[0][2]])
	log("START", message)

# Stop
@bot.message_handler(commands=['stop'])
def send_wtf(message):
	bot.reply_to(message, "WTF?! NO!")
	log("STOP", message)

# Parsing Text
@bot.message_handler(content_types=['text'])
def send_answer(message):
	if(message.text == "kekos"):
		bot.reply_to(message, "privetos")
		if(message.from_user.id in users):
			bot.send_message(message.chat.id, "Oh, i know who are you!")
	else:
		bot.send_message(message.chat.id, json.dumps(chapter1[randint(0,2)]))
	log("TEXT", message)


################
##    MAIN    ##
################
if __name__ == '__main__':
	broad = Process(target=broadcasting, args=(tasks,))
	broad.start()
	print("JentuBot started! <-> ['Ctrl+C' to shutdown]")
	bot.polling(none_stop=True, interval=0)

# def info(title):
# 	print("!#", title, "...")
# 	print("... working on process:", os.getpid(), "<=> Parent:", os.getppid())