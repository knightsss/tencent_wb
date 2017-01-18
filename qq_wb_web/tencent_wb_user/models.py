#coding=utf-8
from django.db import models

#多用户帐号
# Create your models here.
class TencentUser(models.Model):
    user_id =  models.IntegerField()
    user_name = models.CharField(max_length=30)   #主键
    login_name = models.CharField(max_length=30)
    login_password = models.CharField(max_length=30)
    tencent_wb_name = models.CharField(max_length=50)
    qq_qzone_name = models.CharField(max_length=50)
    visit = models.BooleanField()   #是否可以访问
    # def __unicode__(self):
    #     return self.thread_name

#多代理IP
class TencentProxy(models.Model):
    proxy_id =  models.IntegerField()
    proxy_ip = models.CharField(max_length=50)   #代理IP
    visit = models.BooleanField() #是否可以访问
