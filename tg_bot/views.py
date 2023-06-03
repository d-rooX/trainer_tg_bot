from django.shortcuts import HttpResponse
from .dispatcher import bot
from telebot.types import Update

def webhook(request):
	data = request.body.decode('utf-8')
	update = Update.de_json(data)
	bot.process_new_updates([update])

	return HttpResponse(status=200)


def start(request):
	res = bot.set_webhook('https://e008-188-163-72-69.eu.ngrok.io/')
	return HttpResponse(content=str(res).encode('utf-8'))
