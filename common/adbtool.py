#!/usr/bin/env python
# coding: utf-8


import os
import platform
import re
import time
from math import floor
import zipfile


class AdbTools(object):

    def __init__(self, device_id=''):
        self.__system = platform.system()
        self.__find = ''
        self.__command = ''
        self.__device_id = device_id
        self.__get_find()
        self.aapt = ''
        self.__check_adb()
        self.__connection_devices()

    def __get_find(self):
        """
        �ж�ϵͳ���ͣ�windowsʹ��findstr��linuxʹ��grep
        :return:
        """
        if self.__system is "Windows":
            self.__find = "findstr"
        else:
            self.__find = "grep"

    def __check_adb(self):
        """
        ���adb
        �ж��Ƿ����û�������ANDROID_HOME
        :return:
        """
        if "ANDROID_HOME" in os.environ:
            if self.__system == "Windows":
                path = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb.exe")
                if os.path.exists(path):
                    self.__command = path
                else:
                    raise EnvironmentError(
                        "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
            else:
                path = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", "adb")
                if os.path.exists(path):
                    self.__command = path
                else:
                    raise EnvironmentError(
                        "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
            android_path = os.path.join(os.environ["ANDROID_HOME"], 'build-tools')
            self.aapt = os.path.join(android_path, os.listdir(android_path)[0], 'aapt')
        else:
            raise EnvironmentError(
                "Adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])

    def __connection_devices(self):
        """
        ����ָ���豸�������豸�ɲ���device_id
        :return:
        """
        if self.__device_id == "":
            return
        self.__device_id = "-s %s" % self.__device_id

    def adb(self, args):
        """
        ִ��adb����
        :param args:����
        :return:
        """
        cmd = "%s %s %s" % (self.__command, self.__device_id, str(args))
        # print(cmd)
        return os.popen(cmd)

    def shell(self, args):
        """
        ִ��adb shell����
        :param args:����
        :return:
        """
        cmd = "%s %s shell %s" % (self.__command, self.__device_id, str(args))
        # print(cmd)
        return os.popen(cmd)

    def mkdir(self, path):
        """
        ����Ŀ¼
        :param path: ·��
        :return:
        """
        return self.shell('mkdir %s' % path)

    # def unlock(self):

    def get_devices(self):
        """
        ��ȡ�豸�б�
        :return:
        """
        l = self.adb('devices').readlines()
        return [i.split()[0] for i in l if 'devices' not in i and len(i) > 5]

    def get_current_application(self):
        """
        ��ȡ��ǰ���е�Ӧ����Ϣ
        :return:
        """
        return self.shell('dumpsys window w | %s \/ | %s name=' % (self.__find, self.__find)).read()

    def get_current_package(self):
        """
        ��ȡ��ǰ����app����
        :return:
        """
        reg = re.compile(r'name=(.+?)/')
        return re.findall(reg, self.get_current_application())[0]

    def get_current_activity(self):
        """
        ��ȡ��ǰ����activity
        :return: package/activity
        """
        reg = re.compile(r'name=(.+?)\)')
        return re.findall(reg, self.get_current_application())[0]

    def get_current_app_version(self):
        '''
        ��ȡ��ǰ����app�İ汾��
        :return: 
        '''
        s = self.shell('dumpsys package %s'%self.get_current_package()).read()
        reg = re.compile(r'versionName=(.+)')
        return re.findall(reg, s)

    def get_app_name(self, apk_path):
        """
        ��ȡapk��
        :return: 
        """
        try:
            s = os.popen('%s dump badging %s | %s application-label:'%(self.aapt, apk_path, self.__find)).read()
            return s[19:-2]
        except Exception as e:
            print(e)

    def get_app_size(self, apk_path):
        """
        ��ȡ����С
        :param apk_path: 
        :return: 
        """
        size = floor(os.path.getsize(apk_path) / (1024 * 1000))
        return str(size) + "M"

    def get_app_icon(self, apk_path):
        """
        ��ȡapp��ͼ��
        :param apk_path:
        :return:
        """
        s = os.popen('%s dump badging %s'%(self.aapt, apk_path)).read()
        icon_path = re.search("application-icon-\d+?:'(\S+)'", s)
        icon_path = icon_path.group(1)
        zip = zipfile.ZipFile(apk_path)
        iconData = zip.read(icon_path)
        appicon = apk_path.split('.')[0] + '.png'
        with open(appicon, 'wb+') as saveIconFile:
            saveIconFile.write(iconData)
        return os.path.basename(appicon)

    def get_app_package(self, apk_path):
        """
        ��ȡapp����
        :param apk_path: 
        :return: 
        """
        try:
            s = os.popen('%s dump badging %s | %s package:' % (self.aapt, apk_path, self.__find)).read()
            return s.split()[1][6:-1]
        except Exception as e:
            print(e)

    def get_app_activity(self, apk_path):
        """
        ��ȡapp����ҳ
        :param apk_path: 
        :return: 
        """
        try:
            s = os.popen('%s dump badging %s | %s launchable-activity:' % (self.aapt, apk_path, self.__find)).read()
            return s.split()[1][6:-1]
        except Exception as e:
            print(e)

    def get_app_version(self, apk_path):
        """
        ��ȡapp�汾��
        :param apk_path: 
        :return: 
        """
        try:
            s = os.popen('%s dump badging %s | %s versionName=' % (self.aapt, apk_path, self.__find)).read()
            return s.split()[3][13:-1]
        except Exception as e:
            print(e)

    def __get_process(self, package_name):
        """
        ��ȡ������Ϣ
        :param package_name:
        :return:
        """
        if self.__system is "Windows":
            pid_command = self.shell("ps | %s %s$" % (self.__find, package_name)).read()
        else:
            pid_command = self.shell("ps | %s -w %s" % (self.__find, package_name)).read()
        return pid_command

    def process_exists(self, package_name):
        """
        ���ؽ����Ƿ����
        :param package_name:
        :return:
        """
        process = self.__get_process(package_name)
        return package_name in process

    def get_pid(self, package_name):
        """
        ��ȡpid
        :return:
        """
        pid_command = self.__get_process(package_name)
        if pid_command == '':
            print("The process doesn't exist.")
            return pid_command

        req = re.compile(r"\d+")
        result = str(pid_command).split()
        result.remove(result[0])
        return req.findall(" ".join(result))[0]

    def get_uid(self, pid):
        """
        ��ȡuid
        :param pid:
        :return:
        """
        result = self.shell("cat /proc/%s/status" % pid).readlines()
        for i in result:
            if 'uid' in i.lower():
                return i.split()[1]

    def get_flow_data_tcp(self, uid):
        """
        ��ȡӦ��tcp����
        :return:(����, ����)
        """
        tcp_rcv = self.shell("cat proc/uid_stat/%s/tcp_rcv" % uid).read().split()[0]
        tcp_snd = self.shell("cat proc/uid_stat/%s/tcp_snd" % uid).read().split()[0]
        return tcp_rcv, tcp_snd

    def get_flow_data_all(self, uid):
        """
        ��ȡӦ������ȫ������
        ������Ӧ�ö�����̵��������� tcp udp��
        (rx_bytes, tx_bytes) >> (����, ����)
        :param uid:
        :return:list(dict)
        """
        all_data = []
        d = {}
        data = self.shell("cat /proc/net/xt_qtaguid/stats | %s %s" % (self.__find, uid)).readlines()
        for i in data:
            if not i.startswith('\n'):
                item = i.strip().split()
                d['idx'] = item[0]
                d['iface'] = item[1]
                d['acct_tag_hex'] = item[2]
                d['uid_tag_int'] = item[3]
                d['cnt_set'] = item[4]
                d['rx_bytes'] = item[5]
                d['rx_packets'] = item[6]
                d['tx_bytes'] = item[7]
                d['tx_packets'] = item[8]
                d['rx_tcp_bytes'] = item[9]
                d['rx_tcp_packets'] = item[10]
                d['rx_udp_bytes'] = item[11]
                d['rx_udp_packets'] = item[12]
                d['rx_other_bytes'] = item[13]
                d['rx_other_packets'] = item[14]
                d['tx_tcp_bytes'] = item[15]
                d['tx_tcp_packets'] = item[16]
                d['tx_udp_bytes'] = item[17]
                d['tx_udp_packets'] = item[18]
                d['tx_other_bytes'] = item[19]
                d['tx_other_packets'] = item[20]

                all_data.append(d)
                d = {}
        return all_data

    def hide_nav(self):
        self.shell('settings put global policy_control immersive.full=*')

    def recover_nav(self):
        self.shell('settings put global policy_control null*')

    @staticmethod
    def dump_apk(path):
        """
        dump apk�ļ�
        :param path: apk·��
        :return:
        """
        # ���build-tools�Ƿ���ӵ�����������
        # ��Ҫ�õ������aapt����
        l = os.environ['PATH'].split(';')
        build_tools = False
        for i in l:
            if 'build-tools' in i:
                build_tools = True
        if not build_tools:
            raise EnvironmentError("ANDROID_HOME BUILD-TOOLS COMMAND NOT FOUND.\nPlease set the environment variable.")
        return os.popen('aapt dump badging %s' % (path,))

    @staticmethod
    def dump_xml(path, filename):
        """
        dump apk xml�ļ�
        :return:
        """
        return os.popen('aapt dump xmlstrings %s %s' % (path, filename))

    def uiautomator_dump(self):
        """
        ��ȡ��Ļuiautomator xml�ļ�
        :return:
        """
        return self.shell('uiautomator dump').read().split()[-1]

    def pull(self, source, target):
        """
        ���ֻ�����ȡ�ļ������Զ�
        :return:
        """
        self.adb('pull %s %s' % (source, target))

    def push(self, source, target):
        """
        �ӵ��Զ������ļ����ֻ���
        :param source:
        :param target:
        :return:
        """
        self.adb('push %s %s' % (source, target))

    def remove(self, path):
        """
        ���ֻ���ɾ���ļ�
        :return:
        """
        self.shell('rm %s' % (path,))

    def clear_app_data(self, package):
        """
        ����Ӧ������
        :return:
        """
        self.shell('pm clear %s' % (package,))

    def install(self, path):
        """
        ��װapk�ļ�
        :return:
        """
        # adb install ��װ���󳣼��б�
        errors = {'INSTALL_FAILED_ALREADY_EXISTS': '�����Ѿ�����',
                  'INSTALL_DEVICES_NOT_FOUND': '�Ҳ����豸',
                  'INSTALL_FAILED_DEVICE_OFFLINE': '�豸����',
                  'INSTALL_FAILED_INVALID_APK': '��Ч��APK',
                  'INSTALL_FAILED_INVALID_URI': '��Ч������',
                  'INSTALL_FAILED_INSUFFICIENT_STORAGE': 'û���㹻�Ĵ洢�ռ�',
                  'INSTALL_FAILED_DUPLICATE_PACKAGE': '�Ѵ���ͬ������',
                  'INSTALL_FAILED_NO_SHARED_USER': 'Ҫ��Ĺ����û�������',
                  'INSTALL_FAILED_UPDATE_INCOMPATIBLE': '�汾���ܹ���',
                  'INSTALL_FAILED_SHARED_USER_INCOMPATIBLE': '����Ĺ����û�ǩ������',
                  'INSTALL_FAILED_MISSING_SHARED_LIBRARY': '����Ĺ�����Ѷ�ʧ',
                  'INSTALL_FAILED_REPLACE_COULDNT_DELETE': '����Ĺ������Ч',
                  'INSTALL_FAILED_DEXOPT': 'dex�Ż���֤ʧ��',
                  'INSTALL_FAILED_DEVICE_NOSPACE': '�ֻ��洢�ռ䲻�㵼��apk����ʧ��',
                  'INSTALL_FAILED_DEVICE_COPY_FAILED': '�ļ�����ʧ��',
                  'INSTALL_FAILED_OLDER_SDK': 'ϵͳ�汾����',
                  'INSTALL_FAILED_CONFLICTING_PROVIDER': '����ͬ���������ṩ��',
                  'INSTALL_FAILED_NEWER_SDK': 'ϵͳ�汾����',
                  'INSTALL_FAILED_TEST_ONLY': '�����߲���������ԵĲ��Գ���',
                  'INSTALL_FAILED_CPU_ABI_INCOMPATIBLE': '�����ı������벻����',
                  'CPU_ABIINSTALL_FAILED_MISSING_FEATURE': 'ʹ����һ����Ч������',
                  'INSTALL_FAILED_CONTAINER_ERROR': 'SD������ʧ��',
                  'INSTALL_FAILED_INVALID_INSTALL_LOCATION': '��Ч�İ�װ·��',
                  'INSTALL_FAILED_MEDIA_UNAVAILABLE': 'SD��������',
                  'INSTALL_FAILED_INTERNAL_ERROR': 'ϵͳ���⵼�°�װʧ��',
                  'INSTALL_PARSE_FAILED_NO_CERTIFICATES': '�ļ�δͨ����֤ >> ���ÿ���δ֪��Դ',
                  'INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES': '�ļ���֤��һ�� >> ��ж��ԭ�����ٰ�װ',
                  'INSTALL_FAILED_INVALID_ZIP_FILE': '�Ƿ���zip�ļ� >> ��ж��ԭ�����ٰ�װ',
                  'INSTALL_CANCELED_BY_USER': '��Ҫ�û�ȷ�ϲſɽ��а�װ',
                  'INSTALL_FAILED_VERIFICATION_FAILURE': '��֤ʧ�� >> ���������ֻ�',
                  'DEFAULT': 'δ֪����'
                  }
        print('Installing...')
        l = self.adb('install -r %s' % (path,)).read()
        if 'Success' in l:
            print('Install Success')
        if 'Failure' in l:
            reg = re.compile('\\[(.+?)\\]')
            key = re.findall(reg, l)[0]
            try:
                print('Install Failure >> %s' % errors[key])
            except KeyError:
                print('Install Failure >> %s' % key)
        return l

    def uninstall(self, package):
        """
        ж��apk
        :param package: ����
        :return:
        """
        print('Uninstalling...')
        l = self.adb('uninstall %s' % (package,)).read()
        print(l)
        return l

    def screenshot(self, target_path=''):
        """
        �ֻ���ͼ
        :param target_path: Ŀ��·��
        :return:
        """
        format_time = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        self.shell('screencap -p /sdcard/%s.png' % (format_time,))
        time.sleep(1)
        if target_path == '':
            self.pull('/sdcard/%s.png' % (format_time,), os.path.expanduser('~'))
        else:
            self.pull('/sdcard/%s.png' % (format_time,), target_path)
        self.remove('/sdcard/%s.png' % (format_time,))

    def get_cache_logcat(self):
        """
        ����������־
        :return:
        """
        return self.adb('logcat -v time -d')

    def get_crash_logcat(self):
        """
        ����������־
        :return:
        """
        return self.adb('logcat -v time -d | %s AndroidRuntime' % (self.__find,))

    def clear_cache_logcat(self):
        """
        ����������־
        :return:
        """
        self.adb('logcat -c')

    def get_device_time(self):
        """
        ��ȡ�豸ʱ��
        :return:
        """
        return self.shell('date').read().strip()

    def ls(self, command):
        """
        shell ls����
        :return:
        """
        return self.shell('ls %s' % (command,)).readlines()

    def file_exists(self, target):
        """
        �ж��ļ���Ŀ��·���Ƿ����
        :return:
        """
        l = self.ls(target)
        for i in l:
            if i.strip() == target:
                return True
        return False

    def is_install(self, target_app):
        """
        �ж�Ŀ��app���豸���Ƿ��Ѱ�װ
        :param target_app: Ŀ��app����
        :return: bool
        """
        return target_app in self.shell('pm list packages %s' % (target_app,)).read()

    def get_device_model(self):
        """
        ��ȡ�豸�ͺ�
        :return:
        """
        return self.shell('getprop ro.product.model').read().strip()

    def get_device_id(self):
        """
        ��ȡ�豸id
        :return:
        """
        return self.adb('get-serialno').read().strip()

    def get_device_android_version(self):
        """
        ��ȡ�豸Android�汾
        :return:
        """
        return self.shell('getprop ro.build.version.release').read().strip()

    def get_device_sdk_version(self):
        """
        ��ȡ�豸SDK�汾
        :return:
        """
        return self.shell('getprop ro.build.version.sdk').read().strip()

    def get_device_mac_address(self):
        """
        ��ȡ�豸MAC��ַ
        :return:
        """
        return self.shell('cat /sys/class/net/wlan0/address').read().strip()

    def get_device_ip_address(self):
        """
        ��ȡ�豸IP��ַ
        pass: ����WIFI ��������
        :return:
        """
        if not self.get_wifi_state() and not self.get_data_state():
            return
        l = self.shell('ip addr | %s global' % self.__find).read()
        reg = re.compile('\d+\.\d+\.\d+\.\d+')
        return re.findall(reg, l)[0]

    def get_device_imei(self):
        """
        ��ȡ�豸IMEI
        :return:
        """
        sdk = self.get_device_sdk_version()
        # Android 5.0���·���
        if int(sdk) < 21:
            l = self.shell('dumpsys iphonesubinfo').read()
            reg = re.compile('[0-9]{15}')
            return re.findall(reg, l)[0]
        elif self.root():
            l = self.shell('service call iphonesubinfo 1').read()
            print(l)
            print(re.findall(re.compile("'.+?'"), l))
            imei = ''
            for i in re.findall(re.compile("'.+?'"), l):
                imei += i.replace('.', '').replace("'", '').replace(' ', '')
            return imei
        else:
            print('The device not root.')
            return ''

    def check_sim_card(self):
        """
        ����豸SIM��
        :return:
        """
        return len(self.shell('getprop | %s gsm.operator.alpha]' % self.__find).read().strip().split()[-1]) > 2

    def get_device_operators(self):
        """
        ��ȡ��Ӫ��
        :return:
        """
        return self.shell('getprop | %s gsm.operator.alpha]' % self.__find).read().strip().split()[-1]

    def get_device_state(self):
        """
        ��ȡ�豸״̬
        :return:
        """
        return self.adb('get-state').read().strip()

    def get_display_state(self):
        """
        ��ȡ��Ļ״̬
        :return: ����/����
        """
        l = self.shell('dumpsys power').readlines()
        for i in l:
            if 'mScreenOn=' in i:
                return i.split()[-1] == 'mScreenOn=true'
            if 'Display Power' in i:
                return 'ON' in i.split('=')[-1].upper()

    def get_lock_state(self):
        """
        ��ȡ����״̬false������trueδ����
        :return: bool
        """
        l = self.shell("dumpsys window policy|%s isStatusBarKeyguard"%self.__find).read()
        state = l.split('=')[-1].strip()
        return state

    def unlock(self, apk):
        """
        ������Ļ
        :param apk: unlock.apk��ַ
        :return: 
        """
        state = self.get_lock_state()
        if state == "true":
            flag = self.is_install('io.appium.unlock')
            if not flag:
                self.install(apk)
            self.start_application('io.appium.unlock/.Unlock -a android.intent.action.MAIN -c android.intent.category.LAUNCHER -f 0x10200000')
            print('unlock screen')

    def get_screen_normal_size(self):
        """
        ��ȡ�豸��Ļ�ֱ��� >> ����
        :return:
        """
        return self.shell('wm size').read().strip().split()[-1].split('x')

    def get_screen_reality_size(self):
        """
        ��ȡ�豸��Ļ�ֱ��� >> ʵ�ʷֱ���
        :return:
        """
        x = 0
        y = 0
        l = self.shell(r'getevent -p | %s -e "0"' % self.__find).readlines()
        for n in l:
            if len(n.split()) > 0:
                if n.split()[0] == '0035':
                    x = int(n.split()[7].split(',')[0])
                elif n.split()[0] == '0036':
                    y = int(n.split()[7].split(',')[0])
        return x, y

    def get_device_interior_sdcard(self):
        """
        ��ȡ�ڲ�SD���ռ�
        :return: (path,total,used,free,block)
        """
        return self.shell('df | %s \/mnt\/shell\/emulated' % self.__find).read().strip().split()

    def get_device_external_sdcard(self):
        """
        ��ȡ�ⲿSD���ռ�
        :return: (path,total,used,free,block)
        """
        return self.shell('df | %s \/storage' % self.__find).read().strip().split()

    def __fill_rom(self, path, stream, count):
        """
        �������
        :param path: ����ַ
        :param stream: �������С
        :param count: ������
        :return:
        """
        self.shell('dd if=/dev/zero of=%s bs=%s count=%s' % (path, stream, count)).read().strip()

    def fill_interior_sdcard(self, filename, size):
        """
        �������SD��
        :param filename: �ļ���
        :param size: ����С����λbyte
        :return:
        """
        if size > 10485760:  # 10m
            self.__fill_rom('sdcard/%s' % filename, 10485760, size / 10485760)
        else:
            self.__fill_rom('sdcard/%s' % filename, size, 1)

    def fill_external_sdcard(self, filename, size):
        """
        �������SD��
        :param filename: �ļ���
        :param size: ����С����λbyte
        :return:
        """
        path = self.get_device_external_sdcard()[0]
        if size > 10485760:  # 10m
            self.__fill_rom('%s/%s' % (path, filename), 10485760, size / 10485760)
        else:
            self.__fill_rom('%s/%s' % (path, filename), size, 1)

    def kill_process(self, pid):
        """
        ɱ������
        pass: һ����ҪȨ�޲��Ƽ�ʹ��
        :return:
        """
        return self.shell('kill %s' % pid).read().strip()

    def quit_app(self, package):
        """
        �˳�Ӧ��
        :return:
        """
        return self.shell('am force-stop %s' % package).read().strip()

    def reboot(self):
        """
        �����豸
        :return:
        """
        self.adb('reboot')

    def recovery(self):
        """
        �����豸������recoveryģʽ
        :return:
        """
        self.adb('reboot recovery')

    def fastboot(self):
        """
        �����豸������fastbootģʽ
        :return:
        """
        self.adb('reboot bootloader')

    def root(self):
        """
        ��ȡroot״̬
        :return:
        """
        return 'not found' not in self.shell('su -c ls -l /data/').read().strip()

    def wifi(self, power):
        """
        ����/�ر�wifi
        pass: ��ҪrootȨ��
        :return:
        """
        if not self.root():
            print('The device not root.')
            return
        if power:
            self.shell('su -c svc wifi enable').read().strip()
        else:
            self.shell('su -c svc wifi disable').read().strip()

    def data(self, power):
        """
        ����/�رշ�������
        pass: ��ҪrootȨ��
        :return:
        """
        if not self.root():
            print('The device not root.')
            return
        if power:
            self.shell('su -c svc data enable').read().strip()
        else:
            self.shell('su -c svc data disable').read().strip()

    def get_wifi_state(self):
        """
        ��ȡWiFi����״̬
        :return:
        """
        return 'enabled' in self.shell('dumpsys wifi | %s ^Wi-Fi' % self.__find).read().strip()

    def get_data_state(self):
        """
        ��ȡ�ƶ���������״̬
        :return:
        """
        return '2' in self.shell('dumpsys telephony.registry | %s mDataConnectionState' % self.__find).read().strip()

    def get_network_state(self):
        """
        �豸�Ƿ����ϻ�����
        :return:
        """
        return 'unknown host' not in self.shell('ping -w 1 www.baidu.com').read().strip()

    def get_wifi_password_list(self):
        """
        ��ȡWIFI�����б�
        :return:
        """
        if not self.root():
            print('The device not root.')
            return []
        l = re.findall(re.compile('ssid=".+?"\s{3}psk=".+?"'), self.shell('su -c cat /data/misc/wifi/*.conf').read())
        return [re.findall(re.compile('".+?"'), i) for i in l]

    def call(self, number):
        """
        ����绰
        :param number:
        :return:
        """
        self.shell('am start -a android.intent.action.CALL -d tel:%s' % number)

    def open_url(self, url):
        """
        ����ҳ
        :return:
        """
        self.shell('am start -a android.intent.action.VIEW -d %s' % url)

    def start_application(self, component):
        """
        ����һ��Ӧ��
        e.g: com.android.settings/com.android.settings.Settings
        """
        return self.shell("am start -n %s" % component).read()

    def send_keyevent(self, keycode):
        """
        ����һ�������¼�
        https://developer.android.com/reference/android/view/KeyEvent.html
        :return:
        """
        self.shell('input keyevent %s' % keycode)

    def rotation_screen(self, param):
        """
        ��ת��Ļ
        :param param: 0 >> ���򣬽�ֹ�Զ���ת; 1 >> �Զ���ת
        :return:
        """
        self.shell('/system/bin/content insert --uri content://settings/system --bind '
                   'name:s:accelerometer_rotation --bind value:i:%s' % param)

    def instrument(self, command):
        """
        ����instrument app
        :param command: ����
        :return:
        """
        return self.shell('am instrument %s' % command).read()

    def export_apk(self, package, target_path='', timeout=5000):
        """
        ���豸����Ӧ��
        :param timeout: ��ʱʱ��
        :param target_path: ������apk�洢·��
        :param package: ����
        :return:
        """
        num = 0
        if target_path == '':
            self.adb('pull /data/app/%s-1/base.apk %s' % (package, os.path.expanduser('~')))
            while 1:
                num += 1
                if num <= timeout:
                    if os.path.exists(os.path.join(os.path.expanduser('~'), 'base.apk')):
                        os.rename(os.path.join(os.path.expanduser('~'), 'base.apk'),
                                  os.path.join(os.path.expanduser('~'), '%s.apk' % package))

        else:
            self.adb('pull /data/app/%s-1/base.apk %s' % (package, target_path))
            while 1:
                num += 1
                if num <= timeout:
                    if os.path.exists(os.path.join(os.path.expanduser('~'), 'base.apk')):
                        os.rename(os.path.join(os.path.expanduser('~'), 'base.apk'),
                                  os.path.join(os.path.expanduser('~'), '%s.apk' % package))


class KeyCode:
    KEYCODE_CALL = 5  # ���ż�
    KEYCODE_ENDCALL = 6  # �һ���
    KEYCODE_HOME = 3  # Home��
    KEYCODE_MENU = 82  # �˵���
    KEYCODE_BACK = 4  # ���ؼ�
    KEYCODE_SEARCH = 84  # ������
    KEYCODE_CAMERA = 27  # ���ռ�
    KEYCODE_FOCUS = 80  # �Խ���
    KEYCODE_POWER = 26  # ��Դ��
    KEYCODE_NOTIFICATION = 83  # ֪ͨ��
    KEYCODE_MUTE = 91  # ��Ͳ������
    KEYCODE_VOLUME_MUTE = 164  # ������������
    KEYCODE_VOLUME_UP = 24  # ����+��
    KEYCODE_VOLUME_DOWN = 25  # ����-��
    KEYCODE_ENTER = 66  # �س���
    KEYCODE_ESCAPE = 111  # ESC��
    KEYCODE_DPAD_CENTER = 23  # ������ >> ȷ����
    KEYCODE_DPAD_UP = 19  # ������ >> ����
    KEYCODE_DPAD_DOWN = 20  # ������ >> ����
    KEYCODE_DPAD_LEFT = 21  # ������ >> ����
    KEYCODE_DPAD_RIGHT = 22  # ������ >> ����
    KEYCODE_MOVE_HOME = 122  # ����ƶ�����ʼ��
    KEYCODE_MOVE_END = 123  # ����ƶ���ĩβ��
    KEYCODE_PAGE_UP = 92  # ���Ϸ�ҳ��
    KEYCODE_PAGE_DOWN = 93  # ���·�ҳ��
    KEYCODE_DEL = 67  # �˸��
    KEYCODE_FORWARD_DEL = 112  # ɾ����
    KEYCODE_INSERT = 124  # �����
    KEYCODE_TAB = 61  # Tab��
    KEYCODE_NUM_LOCK = 143  # С������
    KEYCODE_CAPS_LOCK = 115  # ��д������
    KEYCODE_BREAK = 121  # Break / Pause��
    KEYCODE_SCROLL_LOCK = 116  # ����������
    KEYCODE_ZOOM_IN = 168  # �Ŵ��
    KEYCODE_ZOOM_OUT = 169  # ��С��
    KEYCODE_0 = 7
    KEYCODE_1 = 8
    KEYCODE_2 = 9
    KEYCODE_3 = 10
    KEYCODE_4 = 11
    KEYCODE_5 = 12
    KEYCODE_6 = 13
    KEYCODE_7 = 14
    KEYCODE_8 = 15
    KEYCODE_9 = 16
    KEYCODE_A = 29
    KEYCODE_B = 30
    KEYCODE_C = 31
    KEYCODE_D = 32
    KEYCODE_E = 33
    KEYCODE_F = 34
    KEYCODE_G = 35
    KEYCODE_H = 36
    KEYCODE_I = 37
    KEYCODE_J = 38
    KEYCODE_K = 39
    KEYCODE_L = 40
    KEYCODE_M = 41
    KEYCODE_N = 42
    KEYCODE_O = 43
    KEYCODE_P = 44
    KEYCODE_Q = 45
    KEYCODE_R = 46
    KEYCODE_S = 47
    KEYCODE_T = 48
    KEYCODE_U = 49
    KEYCODE_V = 50
    KEYCODE_W = 51
    KEYCODE_X = 52
    KEYCODE_Y = 53
    KEYCODE_Z = 54
    KEYCODE_PLUS = 81  # +
    KEYCODE_MINUS = 69  # -
    KEYCODE_STAR = 17  # *
    KEYCODE_SLASH = 76  # /
    KEYCODE_EQUALS = 70  # =
    KEYCODE_AT = 77  # @
    KEYCODE_POUND = 18  # #
    KEYCODE_APOSTROPHE = 75  # '
    KEYCODE_BACKSLASH = 73  # \
    KEYCODE_COMMA = 55  # ,
    KEYCODE_PERIOD = 56  # .
    KEYCODE_LEFT_BRACKET = 71  # [
    KEYCODE_RIGHT_BRACKET = 72  # ]
    KEYCODE_SEMICOLON = 74  # ;
    KEYCODE_GRAVE = 68  # `
    KEYCODE_SPACE = 62  # �ո��
    KEYCODE_MEDIA_PLAY = 126  # ��ý��� >> ����
    KEYCODE_MEDIA_STOP = 86  # ��ý��� >> ֹͣ
    KEYCODE_MEDIA_PAUSE = 127  # ��ý��� >> ��ͣ
    KEYCODE_MEDIA_PLAY_PAUSE = 85  # ��ý��� >> ���� / ��ͣ
    KEYCODE_MEDIA_FAST_FORWARD = 90  # ��ý��� >> ���
    KEYCODE_MEDIA_REWIND = 89  # ��ý��� >> ����
    KEYCODE_MEDIA_NEXT = 87  # ��ý��� >> ��һ��
    KEYCODE_MEDIA_PREVIOUS = 88  # ��ý��� >> ��һ��
    KEYCODE_MEDIA_CLOSE = 128  # ��ý��� >> �ر�
    KEYCODE_MEDIA_EJECT = 129  # ��ý��� >> ����
    KEYCODE_MEDIA_RECORD = 130  # ��ý��� >> ¼��


if __name__ == '__main__':
    a = AdbTools(device_id='10.200.23.209:7405')
    # print a.get_app_name(r'D:\workspace\auto_wireless\apk\app-release-for-152725-o_1bmc0gmt11l6vn5voikiva3or2g-uid-569540.apk')
    print a.unlock(r'D:\workspace\auto_wireless\resource\unlock.apk')