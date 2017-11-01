def to_ascii(h):
	strs = ""
	for i in range(len(h)//2):
		strs += chr(int(h[(i*2):(i*2)+2], 16))
	return strs

def drink(message):
	message = to_ascii(message)
	for i, v in enumerate(message):
		message = message[:i] + chr(ord(v)+12) + message[i+1:]
	return message

vodka = "..."

#def to_hex(s):
#	strs = ""
#	for i in range(len(s)):
#		strs += "%x"%(ord(s[i]))
#	return strs

#def rot(message):
#	for i, v in enumerate(message):
#		message = message[:i] + chr(ord(v)-12) + message[i+1:]
#	return to_hex(message)