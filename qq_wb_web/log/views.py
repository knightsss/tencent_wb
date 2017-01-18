from django.shortcuts import render

# Create your views here.
import logging
import logging.config
import os

def log_setting():
    ##############linux
    file_abspath = os.getcwd() + "/log/"
    ##############windows
    # file_abspath = os.getcwd() + "\\log\\"
    print "file_abspath",file_abspath
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename= file_abspath + 'spider_server.log',
                    filemode='a')

    return logging

