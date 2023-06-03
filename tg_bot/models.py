from django.db import models


class Client(models.Model):
	name = models.CharField(max_length=50)
	# phonenumber = models.CharField(max_length=20)
	telegram_id = models.BigIntegerField()


class Lesson(models.Model):
	date = models.DateTimeField()
	client = models.ForeignKey(Client, related_name='lessons', on_delete=models.CASCADE)
