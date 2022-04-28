from django.db import models

class Engine(models.Model):
    name = models.TextField(default='some Engine')
    nu = models.IntegerField(default='0')