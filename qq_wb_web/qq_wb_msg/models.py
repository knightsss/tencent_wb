#coding=utf-8
from django.db import models

# Create your models here.
class ThreadMsg(models.Model):
    thread_id =  models.IntegerField()
    thread_ip = models.CharField(max_length=30)
    thread_name = models.CharField(max_length=30)    #主键
    thread_status = models.BooleanField()
    # def __unicode__(self):
    #     return self.thread_name
