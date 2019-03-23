# -*- coding: utf-8 -*-
# @Time    : 2018/8/23 16:59
# @File    : gt_tool.py
# @Software: PyCharm


import subprocess


class GT_Tool:

    def __init__(self, packagename, tcpdump_file='/sdcard/GT/tcpdump.pcap', gt_file='gtfile'):
        self.packagename = packagename
        self.tcpdump_file = tcpdump_file
        self.gt_file = gt_file
        self.start_gt_cmd = 'adb shell am start -W -n com.tencent.wstt.gt/com.tencent.wstt.gt.activity.GTMainActivity'
        self.start_test_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.startTest --es pkgName "{}"'.format(self.packagename)
        self.stop_test_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.endTest --es saveFolderName "{0}"'.format(gt_file)
        self.start_cpu_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei cpu 1'
        self.stop_cpu_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei cpu 0'
        self.start_cpu_jif_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei jif 1' # ����CPUʱ��Ƭ�ɼ�
        self.stop_cpu_jif_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei jif 0'
        self.start_pss_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei pss 1'
        self.stop_pss_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei pss 0'
        self.start_pri_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei pri 1' # ����PrivateDirty�ɼ�
        self.stop_pri_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei pri 0'
        self.start_net_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei net 1'
        self.stop_net_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei net 0'
        self.start_fps_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei fps 1'
        self.stop_fps_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.sampleData --ei fps 0'
        self.sm1_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.sm.modify' # ��ӦUI�ϵġ����ġ���һ��ִ�г���ִ����������ָ���,��һֱ��Ч
        self.sm2_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.sm.resume' # ��ӦUI�ϵġ��ָ������������ʱִ��һ�Σ����ֻ��������������Ȳ��Կ���һֱ���ûָ�
        self.sm3_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.sm.restart' # ��ӦUI�ϵġ��������������ֻ�ʹ�����ġ��򡰻ָ�����Ч
        self.sm4_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.sm.startTest --es procName "{}"'.format(self.packagename) # ��ӦUI�ϵġ���ʼ���ԡ���procName��ָ��������̵Ľ�������ִ�к��ڳ����б�Ӧ���Կ���SM������ע���һ��ִ����Ҫ��GT��Ȩ
        self.sm5_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.sm.endTest' # ��ӦUI�ϵġ�ֹͣ���ԡ�
        self.close_gt_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.baseCommand.exitGT'
        self.start_battery_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.battery.startTest --ei refreshRate 250 --ei brightness 100 --ez I true --ez U true --ez T true --ez P true'
        self.stop_battery_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.battery.endTest'
        self.start_memfill_cmd = 'adb shell am broadcast -a  com.tencent.wstt.gt.plugin.memfill.fill --ei size 200' # �ڴ����
        self.stop_memfill_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.memfill.free'
        self.start_tcpdump_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.tcpdump.startTest --es filepath "{}" --es param "-p -s 0 -vv -w"'.format(tcpdump_file)
        self.stop_tcpdump_cmd = 'adb shell am broadcast -a com.tencent.wstt.gt.plugin.tcpdump.endTest'

    def process(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        for line in iter(p.stdout.readline, ""):
            print line

    def install(self, path):
        s = subprocess.check_output('adb shell pm list packages -3')
        if s.find('com.tencent.wstt.gt') == -1:
            subprocess.call('adb install -r {}'.format(path))

    def start_test(self):
        self.start_gt()
        self.start_test_c()
        self.start_cpu()
        self.start_pss()
        self.start_pri()
        self.start_net()
        self.start_fps()
        self.start_sm()
        # self.start_battery()

    def stop_test(self):
        self.stop_cpu()
        self.stop_pss()
        self.stop_pri()
        self.stop_net()
        self.stop_fps()
        self.stop_sm()
        self.stop_battery()
        self.stop_test_c()
        self.close_gt()

    def pull(self, local):
        remote_path = '/sdcard/GT/GW/{}/unknow/{}'.format(self.packagename, self.gt_file)
        self.process('adb pull {} {}'.format(remote_path, local))
        self.process('adb shell rm -rf {}'.format(remote_path))

    def start_gt(self):
        self.process(self.start_gt_cmd)

    def start_test_c(self):
        self.process(self.start_test_cmd)

    def stop_test_c(self):
        self.process(self.stop_test_cmd)

    def start_cpu(self):
        self.process(self.start_cpu_cmd)

    def stop_cpu(self):
        self.process(self.stop_cpu_cmd)

    def start_cpu_jif(self):
        self.process(self.start_cpu_jif_cmd)

    def stop_cpu_jif(self):
        self.process(self.stop_cpu_jif_cmd)

    def start_pss(self): # ʵ��ʹ�õ������ڴ�
        self.process(self.start_pss_cmd)

    def stop_pss(self):
        self.process(self.stop_pss_cmd)

    def start_pri(self): # ˽��פ���ڴ�
        self.process(self.start_pri_cmd)

    def stop_pri(self):
        self.process(self.stop_pri_cmd)

    def start_net(self):
        self.process(self.start_net_cmd)

    def stop_net(self):
        self.process(self.stop_net_cmd)

    def start_fps(self):
        self.process(self.start_fps_cmd)

    def stop_fps(self):
        self.process(self.stop_fps_cmd)

    # �����Ȳ��ԣ���root
    def start_sm(self):
        self.process(self.sm1_cmd)
        self.process(self.sm4_cmd)

    def stop_sm(self):
        self.process(self.sm5_cmd)
        self.process(self.sm2_cmd)
        self.process(self.sm3_cmd)

    def close_gt(self):
        self.process(self.close_gt_cmd)

    def start_battery(self):
        self.process(self.start_battery_cmd)

    def stop_battery(self):
        self.process(self.stop_battery_cmd)

    def start_memfill(self):
        self.process(self.start_memfill_cmd)

    def stop_memfill(self):
        self.process(self.stop_memfill_cmd)

    def start_tcpdump(self):
        self.process(self.start_tcpdump_cmd)

    def stop_tcpdump(self):
        self.process(self.stop_tcpdump_cmd)

if __name__=="__main__":
    gt = GT_Tool('com.example.ljh99.calculator')
    gt.install('')
