# -*- coding: utf-8 -*-
# @Time    : 2018/7/23 10:18
# @File    : stf_connect.py
# @Software: PyCharm


import requests
import json
from titanrun.common.adbtool import AdbTools
import time
import os


class DeviceApi(object):
    def __init__(self, ip, port, token):
        self.baseurl = 'http://{}:{}/api/v1'.format(ip, port)
        self.headers = {'Authorization': 'Bearer ' + token}

    def get_user(self):
        res = requests.get(self.baseurl+'/user', headers=self.headers).content
        return json.loads(res)

    def get_devices(self, status=1):
        """:param
            status=0 ��ȡȫ���豸
            status=1 ��ȡδʹ�õ��豸
        """
        devices = {}
        res = requests.get(self.baseurl+'/devices', headers=self.headers).content
        data = json.loads(res).get('devices')
        if status == 0:
            for d in data:
                model = str(d.get('model')).strip()
                devices[model] = d
        else:
            for d in data:
                if not d.get('present') or not d.get('ready'):
                    continue
                if d.get('using') and d.get('owner'):
                    user = self.get_user()
                    name = user.get('user').get('name')
                    name1 = d.get('owner').get('name')
                    if name != name1:
                        continue
                platformVersion = d.get('version')
                if len(platformVersion) == 3:
                    platformVersion = "{}.0".format(platformVersion)
                serial = str(d.get('serial')).strip()
                devices[serial] = {'serial': serial, 'deviceName': d.get('model'), 'platformVersion': platformVersion,
                                             'manufacturer': d.get('manufacturer'), 'display': '{}x{}'.format(d.get('display').get('width'), d.get('display').get('height')),
                                             'network': d.get('network').get('type'), 'cpuPlatform': d.get('cpuPlatform'), 'battery': d.get('battery'),
                                             'owner': d.get('owner'), 'provider': d.get('provider').get('name'), 'abi': d.get('abi'), 'sdk': d.get('sdk')}
        return devices

    def get_device(self, serial):
        return requests.get(self.baseurl+'/devices/{}'.format(serial), headers=self.headers).content

    def get_devices_of_cur_user(self):
        return requests.get(self.baseurl+'/user/devices', headers=self.headers).content

    def add_device_to_cur_user(self, serial):
        self.headers['Content-Type'] = 'application/json'
        data = {"serial": serial, "timeout": 900}
        return requests.post(self.baseurl+'/user/devices', json=data, headers=self.headers).content

    def del_device_to_cur_user(self, serial):
        return requests.delete(self.baseurl + '/user/devices/{}'.format(serial), headers=self.headers).content

    def remoteconect_device(self, serial):
        res = self.add_device_to_cur_user(serial)
        if res.find('true')>=0:
            r = requests.post(self.baseurl + '/user/devices/{}/remoteConnect'.format(serial), headers=self.headers).content
            udid = json.loads(r).get('remoteConnectUrl')
            return udid
        else:
            return res

    def disremoteconnect_device(self, serial):
        return requests.delete(self.baseurl + '/user/devices/{}/remoteConnect'.format(serial), headers=self.headers).content

    def connect(self, mobile_name):
        devices = self.get_devices()
        serial = devices.get(mobile_name, {}).get('serial')
        if not serial:
            raise Exception('�Ҳ����豸:%s'%serial)
        r = self.remoteconect_device(serial)
        udid = json.loads(r).get('remoteConnectUrl')
        return udid

    def disconnect(self, mobile_name):
        devices = self.get_devices(status=0)
        serial = devices.get(mobile_name).get('serial')
        if not serial:
            raise Exception('Device is not available')
        return self.del_device_to_cur_user(serial)


if __name__=="__main__":
    STF = {"ip": "10.200.20.99", "port": "7100",
           "token": "70580bade44b4908ae1de4337cae4dfeebbb3cd1b11c4fa294c9ce4cc9e2b34c"}

    d = DeviceApi(**STF)
    # print d.get_user()
    print d.get_device("da719efa")
    # print d.add_device_to_cur_user("da719efa")
    print d.get_devices_of_cur_user()
    # print d.remoteconect_device("da719efa")
    print d.del_device_to_cur_user('MKJNW18511012677')
    # print d.disremoteconnect_device("MKJNW18511012677")

    # d.connect("LLD-AL00")
    mobiles = d.get_devices()
    print mobiles

