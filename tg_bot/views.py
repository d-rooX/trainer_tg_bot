from django.shortcuts import HttpResponse
from .dispatcher import bot
from telebot.types import Update

def webhook(request):
	if request.method == 'POST':
		data = request.body.decode('utf-8')
		update = Update.de_json(data)
		bot.process_new_updates([update])

		return HttpResponse(status=200)
	else:
		text = f'<h1> Hello! Bot is working. <a href="https://t.me/{bot.get_me().username}">Click here to visit...</a> </h1>'
		return HttpResponse(status=200, content=text.encode('utf-8'))


def start(request):
	res = bot.set_webhook('https://9c50-188-163-72-69.eu.ngrok.io/')
	return HttpResponse(content=str(res).encode('utf-8'))
