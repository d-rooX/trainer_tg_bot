import datetime

from telebot import TeleBot, ExceptionHandler
from telebot.types import Message
from .models import Client, Lesson


class MyExceptionHandler(ExceptionHandler):
	def handle(self, exception):
		print(exception)


bot = TeleBot(
	token="6071931476:AAE1uTGuGZiVRBbMmqjqSu6NcyKhN3CX3SI",
	exception_handler=MyExceptionHandler(),
)


@bot.message_handler(commands=['start'])
def start_cmd(message: Message):
	user_id = message.from_user.id
	client, is_created = Client.objects.get_or_create(
		telegram_id=user_id,
		defaults={'name': message.from_user.full_name}
	)

	bot.send_message(user_id, f"Доброго дня, {client.name}, я бот помічник по фітнесу!")

	if is_created:
		Lesson.objects.create(client_id=client.id, date=datetime.datetime(year=2023, month=6, day=1, hour=9))
		Lesson.objects.create(client_id=client.id, date=datetime.datetime(year=2023, month=6, day=3, hour=16))
		Lesson.objects.create(client_id=client.id, date=datetime.datetime(year=2023, month=12, day=5, hour=17))

		bot.send_message(user_id, f"Вітаємо з реєстрацією!")

	bot.send_message(user_id, "Використовуйте команди:\n"
							  "/myschedule - отримати розклад занять")


@bot.message_handler(commands=['myschedule'])
def schedule_cmd(message: Message):
	user_id = message.from_user.id

	client = Client.objects.get(telegram_id=user_id)

	text = ''
	for lesson in client.lessons.all():
		day = f'{lesson.date.month:02d}.{lesson.date.day:02d}'
		hour = f'{lesson.date.hour:02d}:{lesson.date.minute:02d}'
		text += f'Заняття {day} о {hour}\n'

	if text != '':
		bot.send_message(user_id, text)
	else:
		bot.send_message(user_id, "У вас ще немає записів на заняття")
