# -*- coding: utf-8 -*-
from datetime import datetime

# It does the stuff
def to_ascii(h):
	strs = ""
	for i in range(len(h)//2):
		strs += chr(int(h[(i*2):(i*2)+2], 16))
	return strs

# Get encrypted data
def de_token(message):
	message = to_ascii(message)
	for i, v in enumerate(message):
		message = message[:i] + chr(ord(v)+12) + message[i+1:]
	return message

# Debug logging
def log(info, message=None):
	print(datetime.now().strftime("[%d/%b/%Y:%H:%M:%S]"), "LOG:", info)
	if(message != None):
		print("-> From:", message.from_user.first_name, message.from_user.last_name)
		print("-> Message:", message.text)
	print('')