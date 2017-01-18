#coding=utf-8
from django.shortcuts import render
from django.shortcuts import render_to_response
# Create your views here.
from wb_get_wid.models import Threadauditor
from wb_get_wid.thread import ThreadControl
from log.rtx import rtx,get_ip

def auditor(request):
    thread1_status = False
    auditor_thread = True
    IP = get_ip()
    thread_list = Threadauditor.objects.filter(thread_ip=IP)
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
    return render_to_response("auditor.html",{"thread_list":thread_list, "auditor_thread":auditor_thread})

def control_auditor(request):

    th_name = request.POST['id']
    control = request.POST['control']
    print "thread_name is ",th_name
    auditor_thread = True
    thread = Threadauditor.objects.get(thread_name=th_name)
    if control == 'start':
        #状态信息
        rtx('ip','进程' + str(th_name) + '  开始采集关系链')
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
        rtx('ip','进程' + str(th_name) + '  采集关系链停止')
        c  = ThreadControl()
        try:
            c.stop(th_name)
            thread.thread_status = 0
            thread.save()
        except:
            print "not thread alive"

    IP = get_ip()
    thread_list = Threadauditor.objects.filter(thread_ip=IP)
    return render_to_response('auditor.html',{"thread_name":th_name, "control":control, "thread_list":thread_list,"auditor_thread":auditor_thread})

def thread_auditor_all(request):
    thread1_status = False
    all_auditor_active = True
    thread_list = Threadauditor.objects.all()
    return render_to_response("auditor.html",{"thread_list":thread_list, "all_auditor_active":all_auditor_active})
