# coding=utf-8
__author__ = 'shifeixiang'

import os
import sys
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import bs4
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import datetime
import MySQLdb
import math

import redis
#布隆过滤器
from pybloom import BloomFilter, ScalableBloomFilter
#加载异常处理
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from qq_wb_msg.msg import qq_login
from log.rtx import rtx

'''
#登陆模块统一用qq_wb_msg，以下注释掉
def qq_login():
    flag = 1
    count = 0
    while flag:
        try:
            ###################linux
            # driver = webdriver.PhantomJS('/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
            ###################windows
            driver  = webdriver.PhantomJS('E:\\phantomjs\\phantomjs-2.1.1-windows\\phantomjs-2.1.1-windows\\bin\\phantomjs')
            flag = 0
        except:
            print "PhantomJS error,wait a moment!"
            time.sleep(10)
            count = count + 1
            if count > 10:
                return None
    try:
        driver.get("http://t.qq.com/")
        time.sleep(3)
        # driver.switch_to_frame("login_frame")
        driver.switch_to.frame("login_div")
        driver.find_element_by_id("switcher_plogin").click()
        driver.find_element_by_id("u").send_keys("用户名")
        driver.find_element_by_id("p").send_keys("密码")
        driver.find_element_by_id("login_button").click()
        time.sleep(10)
        print "driver.current_url is",driver.current_url
        if driver.current_url == "http://t.qq.com/s888888k" :
            pass
        else:
            print "url 不一致!"
            driver.quit()
            qq_login()
    except:
        print "login error!"
        driver.quit()
        qq_login()
    return driver

'''

#获取主页的相关信息，包括收听，听众，广播以及其他主页面的一些信息
def get_auditor_page_url_via_url(driver,main_url):
    #main_ulr切分，目的是获取用户唯一id
    mid = main_url.split('/')[-1]
    print "mid",mid
    # return 0
    # f = open('auditor.txt','w')
    #存在异常情况
    print "main_url",main_url
    try:
        print "driver.current_url is ",driver.current_url
        driver.back()
        print "driver.current_url is back ",driver.current_url
        driver.get(main_url)
    except:
        print "driver error,login again!"
        driver = qq_login()
    #处理等待时长
    try :
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , "bor6")))
        main_page = driver.page_source
        soup = BeautifulSoup(main_page)
        #获取听众的信息
        # audience_li = soup.find(class_='first bor6')
        #获取广播的信息
        # broadcast_li = soup.find(class_='last bor6')
        #获取收听的信息
        auditor_page_url_list = []
        try:
            li_list = soup.find(class_='list  ').find_all('li')
            print "list"
        except:
            li_list = soup.find(class_='list  list_limit ').find_all('li')
            print "list_limit"
        for li in li_list:
            #获取收听的li标签
            if li['class'][0] == "bor6":
                #获取收听的人数
                auditor_number = float(li.find(class_='text_count').string)
                #获取收听的总页数
                page_num = int(math.ceil(auditor_number/15))
                #构造每一页的url
                for page in range(page_num):
                    print li.a.get('href')
                    #构造收听的每一页的page url
                    auditor_page_url_list.append(str(li.a.get('href')).replace('t=1',"t=1#u=" + str(mid) + "&t=1&st=1&p=" + str(page+1)))

                    print "last", str(li.a.get('href')).replace('t=1',"t=1#u=shuixingzhan&t=1&st=1&p=" + str(page+1))
                print "page_num",page_num
        print "find audience list"
    except:
        print "connot visit the url,not find audience list label,not the personal weibo"
        auditor_page_url_list = None
        time.sleep(10)
    ########################################################################需要异常处理
    # f.write(main_page.encode('utf-8'))
    # f.close()
    # print auditor_page_url_list
    return auditor_page_url_list
    # driver.quit()

#根据page页获取所有的url
def get_auditor_main_url(driver, auditor_page_url_list):
    count = 1
    url_list = []
    mid_list = []
    # print "auditor_page_url_list ",auditor_page_url_list
    # f = open("page_url" + "_" + str(count) + ".txt",'w')
    # auditor_page_url = auditor_page_url_list[0]
    # print len(auditor_page_url_list)
    for auditor_page_url in auditor_page_url_list:
    # if 1:
        print"auditor_page_url", auditor_page_url
        driver.get(auditor_page_url)
        #等待加载完成再访问,加载异常时退出，重新登录
        try:
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , "userName")))
            print "find userName"
            print "driver.current_url",driver.current_url
            main_page = driver.page_source
            soup = BeautifulSoup(main_page)
            # if count == 1:
                # f.write(driver.page_source.encode('utf-8'))
            li_list = soup.find_all(class_='userName')
            for li in li_list:
                # auditor_main_url_list.append()
                try:
                    print li.find('strong').find('a').get('href')
                    mid_list.append(str(li.find('strong').find('a').get('href')).replace('/',''))
                    url_list.append("http://t.qq.com" + str(li.find('strong').find('a').get('href')))
                except:
                    pass
                # print count," li is ",li.find('strong').find('a').get('href')
            count = count + 1
        except:
            print "not find userName or other error"
            mid_list = None
        driver.back()
    # f.close()
    return mid_list

def redis_connect():
    #带密码连接
    # r = redis.StrictRedis(host='localhost', port=6379, password='npq8pprjxnppn477xssn')
    try:
        redis_conn = redis.Redis(host='192.168.15.111',port=6379,db=0)
    except:
        rtx('IP','redis连接异常')
        print "connect redis error"
        return None
    return redis_conn
############################################## 以下linux配置
# #入临时消息队列
def push_redis_list_tmp(redis_conn,auditor_mid):
    try:
        redis_conn.rpush("tencent_wb_wid_tmp",auditor_mid)
    except:
        redis_conn = redis_connect()

#出wid消息队列
def pop_redis_list(redis_conn):
    try:
        url = redis_conn.lpop("tencent_wb_wid")
        print "pop ok"
    except:
        # redis_conn = redis_connect()
        print "pop faild"
        url = None
    return url

def mysql_connect():
    try:
        mysql_conn = MySQLdb.connect("192.168.15.111","qzone_spider","qzone_spider","db_tencent_wb")
    except:
        print "connect mysql error"
        rtx('IP','mysql连接异常')
        return None
    return mysql_conn

def insert_mysql(mysql_conn,tmp):
    mysql_cursor = mysql_conn.cursor()
    sql = "insert into t_tencent_wb_auditor2(wid, auditor_wid) values(%s, %s)"
    # tmp结构 tmp = (('00', '0000'), ('10', '111'))
    mysql_cursor.executemany(sql, tmp)
    mysql_conn.commit()
    return 0


################################################  以下windows测试连接
#入消息队列
# def push_redis_list_tmp(redis_conn,auditor_mid):
#     try:
#         redis_conn.rpush("Tencent_wb:mid:tmp",auditor_mid)
#     except:
#         redis_conn = redis_connect()
#
# #出消息队列
# def pop_redis_list(redis_conn):
#     try:
#         url = redis_conn.lpop("Tencent_wb:mid")
#         print "pop ok"
#     except:
#         # redis_conn = redis_connect()
#         print "pop faild"
#         url = None
#     return url
#
# def mysql_connect():
#     try:
#         mysql_conn = MySQLdb.connect("localhost","qzone_spider","qzone_spider","db_tencent_wb")
#     except:
#         print "connect mysql error"
#         rtx('IP','mysql连接异常')
#         return None
#     return mysql_conn
#
# def insert_mysql(mysql_conn,tmp):
#     mysql_cursor = mysql_conn.cursor()
#     sql = "insert into t_tencent_wb_wid3(wid, auditor_wid) values(%s, %s)"
#     # tmp结构 tmp = (('00', '0000'), ('10', '111'))
#     mysql_cursor.executemany(sql, tmp)
#     mysql_conn.commit()
#     return 0
######################################################################以上 windows测试连接
def get_tuple(mid,mid_list):
    tmp_list = []
    for auditor_url in mid_list:
        tmp_tup = (mid,auditor_url)
        tmp_list.append(tmp_tup)
    return tuple(tmp_list)
