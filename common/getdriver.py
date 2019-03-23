#!/usr/bin/env python
# coding=utf-8

# ****************************************************************
# getdriver.py
# Author     : Lieb  
# Version    : 1.1  
# Date       : 2015-12-01
# Description: appiumdriver  
# ****************************************************************
import os
from selenium.common.exceptions import *
from business.conf import EnvSetting
import com
from appium import webdriver
import traceback


def showmobileinfo(desired_caps):
    print '--------------------------------------------'
    print u'���Ի���: %s' % desired_caps.get('deviceName')
    print u'�ֻ�ϵͳ: %s' % desired_caps.get('platformName')
    print u'ϵͳ�汾: %s' % desired_caps.get('platformVersion')
    print u'app����: %s' % desired_caps.get('appPackage')
    print '--------------------------------------------'


def appium_driver(desired_caps, host='127.0.0.1', port='4723'):
    # print 'http://%s:%s/wd/hub' % (host, port), desired_caps
    if host == 'local':
        host = 'localhost'
    driver = webdriver.Remote('http://%s:%s/wd/hub' % (host, port), desired_caps)
    return driver


def getDriver(test_type, mobile, host, port, path, api_name='', app_file=''):
    test_type = test_type.lower()
    desired_caps = {}
    if test_type == "android":
        desired_caps = EnvSetting.DESIRED_CAPS_ANDROID
        if not mobile.get('platformVersion'):
            ver = os.popen('adb -s %s shell getprop ro.build.version.release' % mobile.get('udid')).read().strip()  # ��ȡAndroid�ֻ��汾��
        if not mobile.get('deviceName'):
            dev = os.popen('adb -s %s shell getprop ro.product.model' % mobile.get('udid')).read().strip()  # ��ȡAndroid�ֻ��豸��
        desired_caps['platformVersion'] = mobile.get('platformVersion') or ver
        desired_caps['deviceName'] = mobile.get('deviceName') or dev
        if not app_file:
            app_file = com.find_newfile('{}/apk/'.format(path))
        desired_caps['app'] = app_file
    elif test_type == "ios":
        desired_caps = EnvSetting.DESIRED_CAPS_IOS
    package = EnvSetting.PACKAGE.get(api_name, {})
    desired_caps1 = dict(desired_caps, **package)
    desired_caps1['udid'] = mobile.get('udid')
    try:
        driver = appium_driver(desired_caps1, host, port)
    except WebDriverException as e:
        if str(e).find('was not in the list of connected devices') != -1:
            print('���������ֻ��������ֻ���һ��!')
            raise WebDriverException, '���������ֻ��������ֻ���һ��!'
        elif str(e).find('Requested a new session but one was in progress') != -1:
            print('appium���ϴβ���δ�����˳���session�Ự,����ֹͣ����,�����´�appium����!')
            raise WebDriverException, 'appium���ϴβ���δ�����˳���session�Ự,����ֹͣ����,�����´�appium����!'
        elif str(e).find("Activity used to start app doesn't exist or cannot be launched") != -1:
            print('Activity������,��ȷ�Ϻ����õ�activity�ǿ������ġ�')
            raise WebDriverException, 'Activity������,��ȷ�Ϻ����õ�activity�ǿ������ġ�'
        else:
            print(e)
            raise WebDriverException, e
    except Exception as e:
        driver = ''
        print traceback.print_exc()
        if str(e).find('Errno 10061') != -1:
            print('appium�����δ����,������������,�����в���!')
            raise Exception, 'appium�����δ����,������������,�����в���!'
        else:
            raise Exception, e
    showmobileinfo(desired_caps1)
    return driver