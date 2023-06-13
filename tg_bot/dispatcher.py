from telebot import TeleBot, ExceptionHandler
from telebot.types import Message

from .models import Client


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
    try:
        client = Client.objects.get(telegram_id=user_id)
    except Client.DoesNotExist:
        bot.send_message(
            user_id,
            f'Здравствуйте, {message.from_user.full_name}, отправьте свой номер телефона для регистрации.'
        )
        bot.set_state(user_id, 'wait_phone')
    else:
        bot.send_message(user_id, f'Привет, {client.name}.')


def check_phone_state(message: Message):
    return bot.get_state(message.from_user.id) == 'wait_phone'


@bot.message_handler(func=check_phone_state)
def phone_handler(message: Message):
    user_id = message.from_user.id
    phone = message.text

    chars_to_delete = '+()- '
    for c in chars_to_delete:
        phone = phone.replace(c, '')

    if phone.startswith('380'):
        phone = phone[2:]

    if phone.isdigit():
        try:
            client = Client.objects.get(phonenumber=phone)
        except Client.DoesNotExist:
            bot.send_message(user_id, 'Вашего номера нет в базе клиентов')
        else:
            client.telegram_id = user_id
            client.save()
            bot.delete_state(user_id)

            bot.send_message(user_id, f"Здравствуйте, {client.name}, добро пожаловать!")
    else:
        bot.send_message(message.from_user.id, 'Введите номер в нормальном формате, блин')


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
