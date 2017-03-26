# -*- encoding: utf-8 -*-
import settings
import telebot
import sqlite3

#################
## SQLite Shit ##
#################

# Connect SQLite
storyDB = sqlite3.connect('story.db')
storyEX = storyDB.cursor()

usersDB = sqlite3.connect('users.db', check_same_thread=False)
usersEX = usersDB.cursor()
usersEX.execute("SELECT * FROM users")
usersDB.commit()
print(usersEX.fetchall())

# SQLite Functions
def new_user(message):
	usersEX.execute("INSERT INTO users (id, firstName, secondName) SELECT {0}, '{1}', '{2}' FROM users WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = {0} LIMIT 1) LIMIT 1".format(str(message.from_user.id), message.from_user.first_name, message.from_user.last_name))
	usersDB.commit()
#usersEX.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, firstName VARCHAR(100), secondName VARCHAR(30))')
#usersDB.commit()

# Close SQLite
storyDB.close()

#################
##  Game Vars  ##
#################



#################
##   TeleBot   ##
#################

# Initialize TeleBot
bot = telebot.TeleBot(settings.token)
print("JentuBot started! _____ ['Ctrl+C' to shutdown]")

# Debug logging
def log(info, message):
	print("\n______________________________________LOG______________________________________")
	print("From: {0} {1}; Info: {2}".format(message.from_user.first_name, message.from_user.last_name, info))
	print("Text: " + message.text)
	print("_______________________________________________________________________________")

# Start session
@bot.message_handler(commands=['start'])
def send_welcome(message):
	new_user(message)
	bot.send_message(message.chat.id, "Welcome!!!")
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
	log("TEXT", message)

# Update
bot.polling(none_stop=True, interval=0)