from django.db import models
from django.contrib.auth.models import User


class UserTask(models.Model):
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)
    task_id = models.CharField(verbose_name='Task ID', max_length=100)
