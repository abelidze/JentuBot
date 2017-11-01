# -*- coding: utf-8 -*-
from framework import WebhookServer
from settings import WEBHOOK_URL_BASE, WEBHOOK_URL_PATH, WEBHOOK_SSL_CERT, LANG
from functions import log, set_log
from bot import *

################
##    MAIN    ##
################

if __name__ == '__main__':

	# WebHooks
	jentuBot.remove_webhook()
	jentuBot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))

	# Started (no :D)
	set_log()
	log("JentuBot started! <-> ['Ctrl+C' to shutdown]")

	# Start framework
	jentuApp = WebhookServer()
	jentuApp.start()

	# But if you want a long polling...
	# jentuBot.polling(none_stop=True, interval=0)

	# Shutdown :c
	jentuBot.remove_webhook()
	log("Bye Bye!")