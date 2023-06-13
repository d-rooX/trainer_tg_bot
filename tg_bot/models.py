from django.db import models


class Client(models.Model):
	name = models.CharField(max_length=50)
	phonenumber = models.CharField(max_length=20)
	telegram_id = models.BigIntegerField(null=True, blank=True)

	def __str__(self):
		return f'{self.name} ({self.phonenumber})'


class Lesson(models.Model):
	date = models.DateTimeField()
	client = models.ForeignKey(Client, related_name='lessons', on_delete=models.CASCADE)


class Mailing(models.Model):
	text = models.TextField(max_length=4096)
	users = models.ManyToManyField(Client, verbose_name="Кому отправить")
	file = models.FileField(null=True, blank=True)

	def __str__(self):
		return f'MailingText: {self.text[:20]}'


