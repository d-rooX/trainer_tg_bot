from django.contrib import admin
from .models import Client, Lesson


class LessonAdminInline(admin.TabularInline):
	model = Lesson
	extra = 0


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
	readonly_fields = ('telegram_id',)
	inlines = [LessonAdminInline]



