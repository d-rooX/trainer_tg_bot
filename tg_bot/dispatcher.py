import datetime

from django.conf import settings
from telebot import TeleBot, ExceptionHandler
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardRemove

from . import buttons
from .models import Client, Lesson


class MyExceptionHandler(ExceptionHandler):
    def handle(self, exception):
        raise exception


bot = TeleBot(
    token="1044470544:AAGyzDZV5PoJL5YYCfKXRt23LQhJOEXIjz4",
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
            f"Доброго дня, {message.from_user.full_name}, я бот-помічник по фітнесу. \n"
            "Відправте свій номер телефону для реєстрації"
        )
        bot.set_state(user_id, 'wait_phone')
    else:
        bot.send_message(user_id, f'Вітаю, {client.name}')


def check_phone_state(message: Message):
    return bot.get_state(message.from_user.id) == 'wait_phone'


@bot.message_handler(func=check_phone_state)
def phone_handler(message: Message):
    user_id = message.from_user.id
    phone = message.text
    chars_to_delete = '+()- '
    for char in chars_to_delete:
        phone = phone.replace(char, '')

    if phone.startswith('380'):
        phone = phone[2:]

    if phone.isdigit():
        try:
            client = Client.objects.get(phonenumber=phone)
        except Client.DoesNotExist:
            bot.send_message(user_id, 'Вашого номера немає в базі клієнтів')
        else:
            client.telegram_id = user_id
            client.save()
            bot.delete_state(user_id)

            bot.send_message(user_id, f'Вітаю, {client.name}, ласкаво просимо!')
    else:
        bot.send_message(message.from_user.id, 'Введіть номер телефону в нормальному форматі')


@bot.message_handler(commands=['myschedule'])
def schedule_cmd(message: Message):
    user_id = message.from_user.id
    client = Client.objects.get(telegram_id=user_id)

    if not client.lessons.exists():
        return bot.send_message(user_id, "У вас ще немає записів на заняття")

    keyboard = []
    today = datetime.datetime.now()
    two_weeks_later = today + datetime.timedelta(days=14)
    for lesson in client.lessons.filter(
        date__gte=datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day
        ),
        date__lte=two_weeks_later,
    ):
        button = InlineKeyboardButton(
            text=lesson.date.strftime("%d.%m.%Y о %H:%M"),
            callback_data=lesson.id
        )
        keyboard.append(button)

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*keyboard)

    bot.send_message(user_id, 'Ваш розклад:', reply_markup=markup)


@bot.message_handler(commands=['pay'])
def schedule_cmd(message: Message):
    user_id = message.from_user.id
    bot.send_message(user_id, ' 4149 6090 0855 7136 ПриватБанк \n4441 1144 6527 0831  Монобанк')


@bot.message_handler(func=lambda message: message.text in (
        buttons.BUTTON_LESS_THAN_10_MINUTES,
        buttons.BUTTON_15_MINUTES,
        buttons.BUTTON_MORE_THAN_20_MINUTES
))
def late_lesson_handler(message: Message):
    lesson_id = bot.get_state(message.from_user.id)
    if (lesson_id is None) or (not lesson_id.isdigit()):
        return
    lesson = Lesson.objects.get(id=lesson_id)

    bot.send_message(settings.ADMIN_USER_ID, f'⌛️ Клієнт {lesson.client.name} запізниться на заняття {message.text.lower()}')
    bot.send_message(
        message.from_user.id,
        'Добре, я повідомив адміністратору за Ваше запізнення',
        reply_markup=ReplyKeyboardRemove()
    )

    bot.delete_state(message.from_user.id)


@bot.message_handler(func=lambda message: message.text in (buttons.BUTTON_CANCEL, buttons.BUTTON_NO_CANCEL))
def cancel_lesson_handler(message: Message):
    lesson_id = bot.get_state(message.from_user.id)
    if (lesson_id is None) or (not lesson_id.isdigit()):
        return

    message_text = None
    match message.text:
        case buttons.BUTTON_CANCEL:
            cancel_lesson(lesson_id)
            message_text = 'Окей, я надіслав адміністратору повідомлення про відміну тренування',
        case buttons.BUTTON_NO_CANCEL:
            message_text = 'Радий що заняття відміняти не довелося :)'

    bot.send_message(
        message.from_user.id,
        message_text,
        reply_markup=ReplyKeyboardRemove()
    )

    bot.delete_state(message.from_user.id)


def cancel_lesson(lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    text = f'❌ Клієнт {lesson.client.name} відмінив заняття о {lesson.date.strftime("%d.%m.%Y %H:%M")}'
    bot.send_message(settings.ADMIN_USER_ID, text)


@bot.callback_query_handler(lambda x: x.data.startswith('cancel'))
def cancel_lesson_callback(call: CallbackQuery):
    lesson_id = call.data.split('_')[1]
    bot.set_state(call.from_user.id, lesson_id)

    bot.send_message(
        call.from_user.id,
        'Нагадую, що відміняти тренування потрібно не менше, ніж за 3 години. '
        'В іншому випадку, тренування буде зараховане, як проведене.',
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
            KeyboardButton(text=buttons.BUTTON_CANCEL),
            KeyboardButton(text=buttons.BUTTON_NO_CANCEL),
        )
    )


@bot.callback_query_handler(lambda x: x.data.startswith('late'))
def cancel_lesson_handler(call: CallbackQuery):
    lesson_id = call.data.split('_')[1]
    bot.set_state(call.from_user.id, lesson_id)

    bot.send_message(
        call.from_user.id,
        'Уточніть будь-ласка час запізнення',
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
            KeyboardButton(text=buttons.BUTTON_LESS_THAN_10_MINUTES),
            KeyboardButton(text=buttons.BUTTON_15_MINUTES),
            KeyboardButton(text=buttons.BUTTON_MORE_THAN_20_MINUTES),
        )
    )


@bot.callback_query_handler(lambda x: True)
def button_click_handler(call: CallbackQuery):
    lesson_id = call.data
    lesson = Lesson.objects.get(id=lesson_id)

    keyboard = [
        InlineKeyboardButton(
            text='Відмінити тренування',
            callback_data=f'cancel_{lesson.id}'
        ),
        InlineKeyboardButton(
            text='Запізнююсь на тренування',
            callback_data=f'late_{lesson.id}'
        ),
    ]

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(*keyboard)

    bot.edit_message_text(
        f'Заняття буде проведено {lesson.date.strftime("%d.%m.%Y о %H:%M")}',
        call.from_user.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def anything_else_handler(message: Message):
    bot.send_message(
        message.from_user.id,
        'Я не розумію вас, використовуйте кнопки та команди для взаємодії зі мною'
    )
