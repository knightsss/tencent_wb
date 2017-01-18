#coding=utf-8
from django.shortcuts import render
from django.shortcuts import render_to_response
import time
from qq_wb_msg.thread import ThreadControl
# Create your views here.
from qq_wb_msg.models import ThreadMsg
from log.rtx import rtx,get_ip

#查看本机所启动的进程
def index(request):
    thread1_status = False
    msg_active = True
    IP = get_ip()
    thread_list = ThreadMsg.objects.filter(thread_ip=IP)
    for thread in thread_list:
        c  = ThreadControl()
        try:
            #查看是否处于活跃状态
            status = c.is_alive(thread.thread_name)
            if status:
                #设置状态为1
                thread.thread_status = 1
                thread.save()
            else:
                #设置状态为0
                thread.thread_status = 0
                thread.save()
        except:
            thread.thread_status = 0
            thread.save()
    return render_to_response('index.html',{'thread1_status':thread1_status,"msg_active":msg_active , "thread_list":thread_list})



def control_thread(request):
    th_name = request.POST['id']
    control = request.POST['control']
    print "thread_name is ",th_name
    #显示活跃状态
    msg_active = True
    thread = ThreadMsg.objects.get(thread_name=th_name)
    if control == 'start':
        rtx('ip','进程' + str(th_name) + '  开始采集标签信息')
        #状态信息
        # thread1_status = True
        c  = ThreadControl()
        # status = 1
        #出现错误，则线程不存在，因此启动线程
        try:
            status = c.is_alive(th_name)
            print "thread is alive? ",status
            if status:
                print "thread is alive,caonot start twice!"
            else:
                print "start ..........thread1"
                c.start(th_name,1)
        except:
            print "thread is not alive start!!!"
            c.start(th_name,1)
        thread.thread_status = 1
        thread.save()
    if control == 'stop':
        # thread1_status = False
        # status = 0
        rtx('ip','进程' + str(th_name) + '  采集标签信息停止')
        c  = ThreadControl()
        try:
            c.stop(th_name)
            thread.thread_status = 0
            thread.save()
        except:
            print "not thread alive"

    IP = get_ip()
    thread_list = ThreadMsg.objects.filter(thread_ip=IP)
    return render_to_response('index.html',{"thread_name":th_name, "control":control, "thread_list":thread_list,"msg_active":msg_active})


def thread_msg_all(request):
    thread_list = ThreadMsg.objects.all()
    all_msg_active = True
    return render_to_response('index.html',{"all_msg_active":all_msg_active, "thread_list":thread_list})

def test_model(requests):
    thread_list = ThreadMsg.objects.all()
    return render_to_response("test.html",{"thread_list":thread_list})



################注释掉
def stop_thread(request):
    thread1_status = False
    thread = request.POST['id']
    control = request.POST['control']
    if control == 'start':
        status = 1
        c  = ThreadControl()
        c.start(thread,2)
    if control == 'stop':
        status = 0
        c  = ThreadControl()
        c.stop(thread)
    return render_to_response('index.html',{'thread1_status':thread1_status,"thread":thread, "control":control,"status":status})

def start_spider(request):
    #通过前端传递的参数来确定启动和关闭线程
    #
    c  = ThreadControl()
    c.start('a',2)
    # time.sleep(4)
    # c.stop('a')
    # time.sleep(5)
    # c.start('a',2)
    # time.sleep(5)
    # c.stop('a')
    # print "over"
    return 0
