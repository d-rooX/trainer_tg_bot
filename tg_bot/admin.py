import telebot.apihelper
from django.contrib import admin
from django.core.files.uploadedfile import TemporaryUploadedFile

from .dispatcher import bot
from .models import Client, Lesson, Mailing


class LessonAdminInline(admin.TabularInline):
	model = Lesson
	extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	readonly_fields = ('telegram_id',)
	inlines = [LessonAdminInline]


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
	def save_model(
			self,
			request,
			obj: Mailing,
			form,
			change: bool
	):
		super().save_model(request, obj, form, change)

		text = form.cleaned_data['text']
		users: list[Client] = form.cleaned_data['users']
		file: TemporaryUploadedFile = form.cleaned_data['file']

		if file is not None:
			file_id = None
			for user in users:
				file_to_send = file.open('rb') if file_id is None else file_id
				message = bot.send_document(user.telegram_id, document=file_to_send, caption=text)
				if file_id is None:
					file_id = message.document.file_id

		else:
			for user in users:
				try:
					bot.send_message(user.telegram_id, text)
				except telebot.apihelper.ApiTelegramException as e:
					print(f'ERROR: ({user}) {e}')


