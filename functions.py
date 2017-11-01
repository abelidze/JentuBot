# -*- coding: utf-8 -*-
from json import loads as de_json, JSONDecodeError
from datetime import datetime
import os.path

# It does the stuff
def to_ascii(h):
	strs = ""
	for i in range(len(h)//2):
		strs += chr(int(h[(i*2):(i*2)+2], 16))
	return strs

# Get callback handler
def get_handler(data):
	handler = data[:3]
	if handler not in ['get', 'sg_', 'to_', 'go_', 'er_']:
		handler = data
	return handler

# Get encrypted data
def de_token(message):
	message = to_ascii(message)
	for i, v in enumerate(message):
		message = message[:i] + chr(ord(v)+12) + message[i+1:]
	return message

# JSON
def load_json(path='resource/lang_ru.json'):
	if(not os.path.isfile(path)):
		return None
	try:
		return de_json(open(path).read())

	except JSONDecodeError:
		return None

# Logic checker
def get_logic(expression, data):
	element = ''
	true = 1
	false = 0
	result = ('F', 'T')
	for ch in expression:
		if(ch == '~'):
			false = true
			true = true ^ 1
		elif(ch == '|'):
			if(element == result[true]):
				return result[1]
			elif(element == result[false]):
				pass
			elif(int(element) in data):
				return result[true]
			element = ''
			true = 1
			false = 0
		elif(ch == ','):
			if(element == result[false]):
				return result[0]
			elif(element == result[true]):
				pass
			elif(int(element) not in data):
				return result[false]
			element = ''
			true = 1
			false = 0
		else:
			element += ch
	if(element != ''):
		if(element == result[true]):
			return result[1]
		elif(element == result[false]):
			return result[0]
		elif(int(element) not in data):
			return result[false]
	return result[true]

# Parser
def parse_logic(string, data, spaces=False):
	cursor = 0
	stack = ['']
	if spaces:
		string = string.replace(' ', '')
	for char in string:
		if(char == '('):
			stack.append('')
			cursor += 1
			continue
		if(char == ')'):
			char = get_logic(stack.pop(), data)
			cursor -= 1
		stack[cursor] += char

	return (get_logic(stack.pop(), data) == 'T')

# Debug logging
LOG_FILE = "log/jentu_{}.log".format(datetime.now().strftime("%d.%m.%y_%H-%M-%S"))

def set_log():
	global LOG_FILE
	if(not os.path.isfile(LOG_FILE)):
		f = open(LOG_FILE, "w")
		f.close()

def log(info, user=None):
	if(user == None):
		text = "{0} LOG: {1}\n".format(datetime.now().strftime("[%d/%b/%Y:%H:%M:%S]"), info)
	else:
		text = "{0} LOG: {1}USER-{2}_{3}\n".format(datetime.now().strftime("[%d/%b/%Y:%H:%M:%S]"), info, user.id, user.first_name)
	print(text)

	f_log = open(LOG_FILE, 'a')
	f_log.write(text)
	f_log.close()