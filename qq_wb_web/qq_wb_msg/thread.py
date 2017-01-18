#coding=utf-8
__author__ = 'shifeixiang'
import time
import thread
import threading
from qq_wb_msg.msg import qq_login, redis_connect, connect_mongodb,pop_redis_list, get_msg, load_mongodb

from log.views import log_setting

# from log.rtx import rtx


#单例模式
# class Singleton(type):
#     def __init__(cls, name, bases, dict):
#         super(Singleton, cls).__init__(name, bases, dict)
#         cls._instance = None
#     def __call__(cls, *args, **kw):
#         if cls._instance is None:
#             cls._instance = super(Singleton, cls).__call__(*args, **kw)
#         return cls._instance

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
    #出队
    conn_redis = redis_connect()
    conn_mongo = connect_mongodb()
    print "conn_redis",conn_redis
    print "conn_mongo",conn_mongo
    if conn_redis == 0 or conn_mongo == 0:
        print "redis or mongodb connect error"
    else:
        while not c_thread.thread_stop:
            print 'Thread:(%s) Time:%s\n'%(thread_num,time.ctime())
            log = log_setting()
            log.info('Thread:(%s) Time:%s\n'%(thread_num,time.ctime()))
            url = pop_redis_list(conn_redis)
            #判断队列是否为空
            if url == None:
                print "queue is NULL"
            else:
                #获取详细信息
                msg = get_msg(driver,url)
                print "load to mongodb"
                try:
                    load_mongodb(conn_mongo,url,msg)
                except:
                    print "mongodb error "
                    break
        # rtx('IP','正常停止')
        print thread_num,"quit phantomjs"
        driver.quit()
            # time.sleep(interval)


####################################测试部分
# def test4():
#     c  = ThreadControl()
#     c.start('a',2)
#     time.sleep(4)
#     c.stop('a')
#     time.sleep(5)
#     c.start('a',2)
#     time.sleep(5)
#     c.stop('a')
#     print "over"
# if __name__ == '__main__':
#     # test1()
#     # time.sleep(30)
#     test4()

