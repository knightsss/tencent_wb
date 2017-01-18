#coding=utf-8
__author__ = 'shifeixiang'
import time
import thread
import threading
from wb_get_wid.auditor import redis_connect,pop_redis_list,get_auditor_page_url_via_url,get_auditor_main_url,mysql_connect,get_tuple,insert_mysql,push_redis_list_tmp
from qq_wb_msg.msg import qq_login

class Spider(threading.Thread):
    # __metaclass__ = Singleton
    thread_stop = False
    thread_num = 0
    interval = 0
    behavior = None
    def run(self):
        self.behavior(self,self.thread_num,self.interval)
    def stop(self):
        self.thread_stop = True

class ThreadControl():
    thread_stop = False
    current_thread = {}
    def start(self,thread_num,interval):
        spider = Spider()
        spider.behavior = loaddata
        spider.thread_num = thread_num
        spider.interval = interval
        spider.start()
        self.current_thread[str(thread_num)] = spider
    #判断进程是否活跃
    def is_alive(self,thread_num):
        tt = self.current_thread[str(thread_num)]
        return tt.isAlive()
    #获取当前线程名称
    # def get_name(self):
    def stop(self,thread_num):
        print "stop"
        spider = self.current_thread[str(thread_num)]
        spider.stop()

def loaddata(c_thread,thread_num,interval):
    print "run......"
    driver = qq_login()
    time.sleep(3)

    if driver == None :
        "phantomjs error!quit"
        return 0
    else:
        pass

    #连接redis
    conn_redis = redis_connect()
    #mysql连接 异常返回None
    #mysql_conn = mysql_connect()
    # conn_mongo = connect_mongodb()
    print "conn_redis",conn_redis
    # print "conn_mongo",conn_mongo
    if conn_redis == None  :
        print "redis connect error"
    else:
        while not c_thread.thread_stop:
            print 'Thread:(%s) Time:%s\n'%(thread_num,time.ctime())
            mid = pop_redis_list(conn_redis)
            if mid == None:
                print "queue is NULL"
                break
            else:
                url = "http://t.qq.com/" + str(mid)
                print "url",url
                time.sleep(3)
                #根据用户的主页url获取收听的所有页面
                auditor_page_url_list = get_auditor_page_url_via_url(driver,url)
                if auditor_page_url_list == None:
                    print "page is not personal,login again"
                    driver.quit()
                    driver = qq_login()
                    if driver == None:
                        break
                    else:
                        pass
                #根据收听的所有页面获取收听者的主页url
                ################根据已知mid获取所有收听的mid
                else:
                    mid_list = get_auditor_main_url(driver, auditor_page_url_list)
                    if mid_list == None:
                        continue
                    else:
                        #############################################存入mysql
                        print "insert mysql"
                        #获取mid和auditor_mid组成的元组，多个
                        tmp_tuple = get_tuple(mid,mid_list)
                        #插入mysql数据库
                        print "insert into table "
                        mysql_conn = mysql_connect()
                        insert_mysql(mysql_conn,tmp_tuple)
                        #关闭数据库
                        mysql_conn.close()
                        ############################################存入临时的redis
                        print "put mid redis"
                        push_redis_list_tmp(conn_redis,mid)
                        print "put auditor mid redis"
                        for auditor_mid in mid_list:
                            push_redis_list_tmp(conn_redis,auditor_mid)
        print thread_num,"quit phantomjs"
        driver.quit()
        
