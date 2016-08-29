from django.db import models
from datetime import datetime

class RecentScansDB(models.Model):
	NAME = models.TextField()
	MD5 = models.CharField(max_length = 100)
	URL = models.TextField()
	USER = models.CharField(max_length = 50)
	TS = models.CharField(max_length = 50, default=datetime.now().strftime("%Y-%m-%d"))

class User(models.Model):
	username = models.CharField(max_length = 50)
	password = models.CharField(max_length = 50)

	def __unicode__(self):
		return self.username
