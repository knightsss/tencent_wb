#coding=utf-8
__author__ = 'shifeixiang'

from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time
import datetime
import MySQLdb
import redis
from pymongo import *
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tencent_wb_user.models import TencentUser
from tencent_wb_user.models import TencentProxy
import random
from log.rtx import rtx
#定义当前帐号用户数量
# USER_COUNT = 2
# PROXY_COUNT = 0

def qq_login():

    USER_COUNT = TencentUser.objects.count()
    PROXY_COUNT = TencentProxy.objects.count()
    #产生随机数
    print 'USER_COUNT', USER_COUNT
    print 'PROXY_COUNT', PROXY_COUNT
    user_number = random.randint(1, USER_COUNT)
    #判断是否有代理
    if PROXY_COUNT == 0:
        proxy_status = False
    else:
        proxy_number = random.randint(1, PROXY_COUNT)
        print "proxy_number",proxy_number
        proxy_object = TencentProxy.objects.get(proxy_id=proxy_number)
        #proxy_ip = '110.73.6.15:8123'
        proxy_ip = proxy_object.proxy_ip
        proxy = '--proxy=' + proxy_ip
        service_args = [proxy]
        proxy_status = True
        print "proxy",proxy

    print 'user_number is',user_number
    print "proxy_status",proxy_status

    #去数据库中取，随机获取登陆帐号
    user = TencentUser.objects.get(user_id=user_number)
    login_name = user.login_name
    login_pwd = user.login_password
    tencent_wb_name = user.tencent_wb_name

    flag = 1
    count = 0
    while flag:
        try:
            ###################linux
            driver = webdriver.PhantomJS(executable_path='/usr/local/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
            ###################windows
            # if proxy_status:
            #     print "use proxy"
            #     driver  = webdriver.PhantomJS(executable_path='E:\\phantomjs\\phantomjs-2.1.1-windows\\phantomjs-2.1.1-windows\\bin\\phantomjs',service_args=service_args)
            # else:
            #     print "no proxy"
            #     driver  = webdriver.PhantomJS(executable_path='E:\\phantomjs\\phantomjs-2.1.1-windows\\phantomjs-2.1.1-windows\\bin\\phantomjs')
            flag = 0
        except:
            print "PhantomJS error,wait a moment!"
            time.sleep(2)
            count = count + 1
            if count > 5:
                rtx('IP','连接phantomjs失败，检查phantomjs是否可用')
                return None
    try:
        print "start get main"
        driver.get("http://t.qq.com/")
        print "get over"
        time.sleep(3)
        # driver.switch_to_frame("login_frame")
        driver.switch_to.frame("login_div")
        driver.find_element_by_id("switcher_plogin").click()
        driver.find_element_by_id("u").send_keys(login_name)
        driver.find_element_by_id("p").send_keys(login_pwd)
        driver.find_element_by_id("login_button").click()
        time.sleep(10)
        print "driver.current_url is",driver.current_url
        #判断登陆成功
        if driver.current_url == str("http://t.qq.com/" + tencent_wb_name):
            pass
        else:
            print "url not match!"
            driver.quit()
            qq_login()
    except:
        print "login error!"
        rtx('IP','登陆异常，检查帐密或者代理是否可用')
        #代理访问出错
        driver.quit()
        qq_login()
    return driver

#连接redis
def redis_connect():
    #带密码连接
    # r = redis.StrictRedis(host='localhost', port=6379, password='npq8pprjxnppn477xssn')
    try:
        redis_conn = redis.Redis(host='192.168.15.111',port=6379,db=0)
    except:
        print "connect redis error"
        rtx('IP','redis连接异常')
        redis_conn = 0
    return redis_conn

#################  以下 linux 出队列
def pop_redis_list(redis_conn):
    try:
        url = redis_conn.lpop("tencent_wb_msg_wid")
        print "pop ok"
    except:
        # redis_conn = redis_connect()
        print "pop faild"
        url = None
    return url

################## 以下 windows 出队列
# def pop_redis_list(redis_conn):
#     try:
#         url = redis_conn.lpop("Tencent_wb:mid:msg")
#         print "pop ok"
#     except:
#         # redis_conn = redis_connect()
#         print "pop faild"
#         url = None
#     return url
################## 以上 windows 出队列

#连接mongodb
def connect_mongodb():
    #新版本连接方式
    try:
        conn = MongoClient("192.168.15.111", 27017)
    except:
        conn = 0
        rtx('IP','mongodb连接异常')
    #旧版本连接方式
    # conn = pymongo.Connection("192.168.15.111",27017)
    return conn


#########################  以下 linux 入库到mongodb
def load_mongodb(conn,url,msg):
    db = conn.db_tx_wb_msg
    t_tencent_wb_msg2 = db.t_tencent_wb_msg2
    msg_label = {
        'wid':url,
        'info':msg
    }
    t_tencent_wb_msg2.insert(msg_label)
    return 0
###########################  以下 windows 入库到mongodb
# def load_mongodb(conn,url,msg):
#     db = conn.db_tx_wb_msg
#     t_tx_wb_msg = db.t_tx_wb_msg
#     msg_label = {
#         'wid':url,
#         'info':msg
#     }
#     t_tx_wb_msg.insert(msg_label)
#     return 0
###########################   以上 windows 入库到mongodb


def get_msg(driver,url):
    wid = url
    msg_url = "http://p.t.qq.com/m/home_userinfo.php?u=" + str(wid)
    try:
        driver.get(msg_url)
        try:
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , "u_info")))
            print "find userName"
            print "driver.current_url",driver.current_url
            soup = BeautifulSoup(driver.page_source)
            msg = soup.find(class_='u_info')
            msg_list = []
            for sub_msg in msg.stripped_strings:
                msg_list.append(sub_msg.encode('utf-8'))
            try:
                for label in msg.find(class_='badgeBox').find_all('span'):
                    if label.get('title') == None:
                        pass
                    else:
                        msg_list.append(label.get('title').encode('utf-8'))
            except:
                print "no xunzhang"
            #不适用ascii显示
            msg_list = json.dumps(msg_list, encoding="UTF-8", ensure_ascii=False)
            # for k in eval(msg_list):
            #     print k
        except:
            print "load error or connot find u_info!"
            msg_list = None
    except:
        print "get error"
        msg_list = None
    return msg_list


