# coding=utf-8

import xlsxwriter
import sys
import pandas as pd
reload(sys)
sys.setdefaultencoding('utf8')


class OperateReport:
    def __init__(self, wd, data):
        self.wd = wd
        self.data = data
        self.define_format_H1 = self.set_format(
            {'bold': True, 'font_size': 20, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'navy',
             'font_color': '#ffffff', 'text_wrap': 1})
        self.define_format_H2 = self.set_format(
            {'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'blue',
             'font_color': '#ffffff', 'text_wrap': 1})
        self.define_format_H3 = self.set_format(
            {'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'bg_color': 'gray',
             'font_color': '#ffffff', 'text_wrap': 1})

    def init(self, worksheet):
        # �������еĿ��
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 25)
        worksheet.set_column("G:G", 13)
        worksheet.set_column("H:H", 17)

        for i in range(40):
            worksheet.set_row(i, 30)

        worksheet.set_row(0, 50)
        worksheet.set_row(6, 60)
        worksheet.set_row(7, 80)

        worksheet.merge_range('A1:H1', 'APP�Զ������Ա���', self.define_format_H1)
        worksheet.merge_range('A2:H2', 'Ӧ�û�����Ϣ', self.define_format_H2)

        self.write_bg(worksheet, "A3", 'APP����')
        self.write_bg(worksheet, "A4", '��������')
        self.write_bg(worksheet, "A5", '�����ն���')

        self.write(worksheet, "B3", self.data["app_info"]["app_name"])
        self.write(worksheet, "B4", self.data["app_info"]["test_platform"])
        self.write(worksheet, "B5", self.data["test_results"]["test_devices"])

        self.write_bg(worksheet, "C3", "APP�汾")
        self.write_bg(worksheet, "C4", "��������")
        self.write_bg(worksheet, "C5", "����״̬")

        self.write(worksheet, "D3", self.data['app_info']["app_version"])
        self.write(worksheet, "D4", self.data["app_info"]["network"])
        self.write(worksheet, "D5", self.data["test_results"]["status"])

        self.write_bg(worksheet, "E3", "APP����")
        self.write_bg(worksheet, "E4", "���ʱ��")

        self.write(worksheet, "F3", self.data["app_info"]["app_package"])
        self.write(worksheet, "F4", self.data["test_results"]["start_time"])

        self.write_bg(worksheet, "G3", "APP��С")
        self.write_bg(worksheet, "G4", "����ʱ��")

        self.write(worksheet, "H3", self.data['app_info']['app_size'])
        self.write(worksheet, "H4", self.data["test_results"]["total_time"])

        worksheet.merge_range('A6:H6', '���Խ��', self.define_format_H2)
        self.write_bg(worksheet, "A7", "���Խ��")
        self.write_bg(worksheet, "B7", "�ܼ�")
        self.write_bg(worksheet, "C7", "ȫ��ͨ��")
        self.write_bg(worksheet, "D7", "ʧ��")

        self.write_bg(worksheet, "A8", "������")
        self.write(worksheet, "B8", self.data["test_results"]["testcase_total"])
        self.write(worksheet, "C8", self.data["test_results"]["testcase_pass"])
        self.write_red(worksheet, "D8", self.data["test_results"]["testcase_fail"])
        self.pie(worksheet)

        worksheet.merge_range('A9:H9', '�����豸�ֲ�', self.define_format_H2)

        start_init = 10
        worksheet.merge_range('A{0}:D{0}'.format(start_init), '�豸Ʒ�Ʒֲ�', self.define_format_H3)
        self.write(worksheet, "A{}".format(start_init + 1), "Ʒ��")
        self.write(worksheet, "B{}".format(start_init + 1), "�ܼ�")
        self.write(worksheet, "C{}".format(start_init + 1), "ͨ����")
        self.write(worksheet, "D{}".format(start_init + 1), "ʧ����")
        temp = 2
        for key, value in self.data["manufacturer"].iteritems():
            worksheet.set_row(start_init + temp, 30)
            self.write(worksheet, "A" + str(start_init + temp), key)
            self.write(worksheet, "B" + str(start_init + temp), value.get('success', 0) + value.get('fail', 0))
            self.write(worksheet, "C" + str(start_init + temp), value.get('success', 0))
            self.write_red(worksheet, "D" + str(start_init + temp), value.get('fail', 0))
            temp += 1
        self.bar(worksheet, '�豸Ʒ�Ʒֲ�', 'E10', '$A${}:$A${}'.format(start_init + 2, start_init + temp - 1),
                 '$C${}:$C${}'.format(start_init + 2, start_init + temp - 1),
                 '$D${}:$D${}'.format(start_init + 2, start_init + temp - 1))

        start_init = start_init + temp if temp >= 7 else start_init + 7
        worksheet.merge_range('A{0}:D{0}'.format(start_init), '�豸ϵͳ�汾�ֲ�', self.define_format_H3)
        self.write(worksheet, "A{}".format(start_init + 1), "ϵͳ�汾")
        self.write(worksheet, "B{}".format(start_init + 1), "�ܼ�")
        self.write(worksheet, "C{}".format(start_init + 1), "ͨ����")
        self.write(worksheet, "D{}".format(start_init + 1), "ʧ����")
        temp = 2

        for key, value in self.data["platformVersion"].iteritems():
            worksheet.set_row(start_init + temp, 30)
            self.write(worksheet, "A" + str(start_init + temp), key)
            self.write(worksheet, "B" + str(start_init + temp), value.get('success', 0) + value.get('fail', 0))
            self.write(worksheet, "C" + str(start_init + temp), value.get('success', 0))
            self.write_red(worksheet, "D" + str(start_init + temp), value.get('fail', 0))
            temp += 1
        self.bar(worksheet, 'ϵͳ�汾�ֲ�', 'E{}'.format(start_init),
                 '$A${}:$A${}'.format(start_init + 2, start_init + temp - 1),
                 '$C${}:$C${}'.format(start_init + 2, start_init + temp - 1),
                 '$D${}:$D${}'.format(start_init + 2, start_init + temp - 1))

        start_init = start_init + temp if temp >= 7 else start_init + 7
        worksheet.merge_range('A{0}:D{0}'.format(start_init), '�豸�ֱ��ʷֲ�', self.define_format_H3)
        self.write(worksheet, "A{}".format(start_init + 1), "�ֱ���")
        self.write(worksheet, "B{}".format(start_init + 1), "�ܼ�")
        self.write(worksheet, "C{}".format(start_init + 1), "ͨ����")
        self.write(worksheet, "D{}".format(start_init + 1), "ʧ����")
        temp = 2

        for key, value in self.data["display"].iteritems():
            worksheet.set_row(start_init + temp, 30)
            self.write(worksheet, "A" + str(start_init + temp), key)
            self.write(worksheet, "B" + str(start_init + temp), value.get('success', 0) + value.get('fail', 0))
            self.write(worksheet, "C" + str(start_init + temp), value.get('success', 0))
            self.write_red(worksheet, "D" + str(start_init + temp), value.get('fail', 0))
            temp += 1
        self.bar(worksheet, '�ֱ��ʷֲ�', 'E{}'.format(start_init),
                 '$A${}:$A${}'.format(start_init + 2, start_init + temp - 1),
                 '$C${}:$C${}'.format(start_init + 2, start_init + temp - 1),
                 '$D${}:$D${}'.format(start_init + 2, start_init + temp - 1))

    def test_detail(self, worksheet):
        # �������еĿ��
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 15)
        worksheet.set_column("H:H", 15)
        worksheet.set_column("I:I", 30)
        worksheet.set_column("J:J", 17)
        worksheet.set_column("K:K", 15)

        for i in range(len(self.data["devices_detail"])+2):
            worksheet.set_row(i, 30)

        worksheet.merge_range('A1:K1', '��������', self.define_format_H2)
        self.write_bg(worksheet, "A2", 'Ʒ��')
        self.write_bg(worksheet, "B2", '�ͺ�')
        self.write_bg(worksheet, "C2", 'ϵͳ�汾')
        self.write_bg(worksheet, "D2", '�ֱ���')
        self.write_bg(worksheet, "E2", '������')
        self.write_bg(worksheet, "F2", '��װ')
        self.write_bg(worksheet, "G2", 'ж��')
        self.write_bg(worksheet, "H2", '���Խ��')
        self.write_bg(worksheet, "I2", 'ʧ��ԭ��')
        self.write_bg(worksheet, "J2", '��ͼ')
        self.write_bg(worksheet, "K2", '��־')

        temp = 3
        for item in self.data["devices_detail"]:
            if item.get("test_result") == 'success':
                self.write(worksheet, "A" + str(temp), item.get("manufacturer"))
                self.write(worksheet, "B" + str(temp), item.get("deviceName"))
                self.write(worksheet, "C" + str(temp), item.get("platformVersion"))
                self.write(worksheet, "D" + str(temp), item.get("display"))
                self.write(worksheet, "E" + str(temp), item.get("test_name"))
                self.write(worksheet, "F" + str(temp), item.get("test_install"))
                self.write(worksheet, "G" + str(temp), item.get("test_uninstall"))
                self.write(worksheet, "H" + str(temp), item.get("test_result"))
                self.write(worksheet, "I" + str(temp), item.get("test_reason"))
            else:
                self.write_red(worksheet, "A" + str(temp), item.get("manufacturer"))
                self.write_red(worksheet, "B" + str(temp), item.get("deviceName"))
                self.write_red(worksheet, "C" + str(temp), item.get("platformVersion"))
                self.write_red(worksheet, "D" + str(temp), item.get("display"))
                self.write_red(worksheet, "E" + str(temp), item.get("test_name"))
                self.write_red(worksheet, "F" + str(temp), item.get("test_install"))
                self.write_red(worksheet, "G" + str(temp), item.get("test_uninstall"))
                self.write_red(worksheet, "H" + str(temp), item.get("test_result"))
                self.write_red(worksheet, "I" + str(temp), item.get("test_reason"))

            if item.get("test_image"):
                worksheet.insert_image('J' + str(temp), item["test_image"],
                                       {'x_scale': 0.3, 'y_scale': 0.2, 'border': 1})
                worksheet.set_row(temp - 1, 130)
            else:
                self.write(worksheet, "J" + str(temp), item.get("test_image"))
            if item.get("test_log"):
                worksheet.write_url('K' + str(temp), item["test_log"], self.set_format({'bold': True, 'underline':  1, 'valign': 'vcenter', 'border':1}), "������־")
            else:
                self.write(worksheet, "K" + str(temp), item.get("test_log"))
            temp = temp + 1

    def compatib_init(self, worksheet):
        # �������еĿ��
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 25)
        worksheet.set_column("G:G", 13)
        worksheet.set_column("H:H", 17)

        for i in range(40):
            worksheet.set_row(i, 30)

        worksheet.set_row(0, 50)
        worksheet.set_row(6, 60)
        worksheet.set_row(7, 80)

        worksheet.merge_range('A1:H1', 'APP�����Բ��Ա���', self.define_format_H1)
        worksheet.merge_range('A2:H2', 'Ӧ�û�����Ϣ', self.define_format_H2)

        self.write_bg(worksheet, "A3", 'APP����')
        self.write_bg(worksheet, "A4", '��������')
        self.write_bg(worksheet, "A5", '�����ն���')

        self.write(worksheet, "B3", self.data["app_info"]["app_name"])
        self.write(worksheet, "B4", self.data["app_info"]["test_platform"])
        self.write(worksheet, "B5", self.data["test_results"]["test_devices"])

        self.write_bg(worksheet, "C3", "APP�汾")
        self.write_bg(worksheet, "C4", "��������")
        self.write_bg(worksheet, "C5", "����״̬")

        self.write(worksheet, "D3", self.data['app_info']["app_version"])
        self.write(worksheet, "D4", self.data["app_info"]["network"])
        self.write(worksheet, "D5", self.data["test_results"]["status"])

        self.write_bg(worksheet, "E3", "APP����")
        self.write_bg(worksheet, "E4", "���ʱ��")

        self.write(worksheet, "F3", self.data["app_info"]["app_package"])
        self.write(worksheet, "F4", self.data["test_results"]["start_time"])

        self.write_bg(worksheet, "G3", "APP��С")
        self.write_bg(worksheet, "G4", "����ʱ��")

        self.write(worksheet, "H3", self.data['app_info']['app_size'])
        self.write(worksheet, "H4", self.data["test_results"]["total_time"])

        worksheet.merge_range('A6:H6', '���Խ��', self.define_format_H2)
        self.write_bg(worksheet, "A7", "���Խ��")
        self.write_bg(worksheet, "B7", "�ܼ�")
        self.write_bg(worksheet, "C7", "ȫ��ͨ��")
        self.write_bg(worksheet, "D7", "ʧ��")

        self.write_bg(worksheet, "A8", "�ֻ���")
        self.write(worksheet, "B8", self.data["test_results"]["test_total"])
        self.write(worksheet, "C8", self.data["test_results"]["test_pass"])
        self.write_red(worksheet, "D8", self.data["test_results"]["test_fail"])
        self.pie(worksheet)

        worksheet.merge_range('A9:H9', '�����豸�ֲ�', self.define_format_H2)

        start_init = 10
        worksheet.merge_range('A{0}:D{0}'.format(start_init), '�豸Ʒ�Ʒֲ�', self.define_format_H3)
        self.write(worksheet, "A{}".format(start_init + 1), "Ʒ��")
        self.write(worksheet, "B{}".format(start_init + 1), "�ܼ�")
        self.write(worksheet, "C{}".format(start_init + 1), "ͨ����")
        self.write(worksheet, "D{}".format(start_init + 1), "ʧ����")
        temp = 2
        for key, value in self.data["manufacturer"].iteritems():
            worksheet.set_row(start_init + temp, 30)
            self.write(worksheet, "A" + str(start_init + temp), key)
            self.write(worksheet, "B" + str(start_init + temp), value.get('success', 0) + value.get('fail', 0))
            self.write(worksheet, "C" + str(start_init + temp), value.get('success', 0))
            self.write_red(worksheet, "D" + str(start_init + temp), value.get('fail', 0))
            temp += 1
        self.bar(worksheet, '�豸Ʒ�Ʒֲ�', 'E10', '$A${}:$A${}'.format(start_init + 2, start_init + temp - 1),
                 '$C${}:$C${}'.format(start_init + 2, start_init + temp - 1),
                 '$D${}:$D${}'.format(start_init + 2, start_init + temp - 1))

        start_init = start_init + temp if temp >= 7 else start_init + 7
        worksheet.merge_range('A{0}:D{0}'.format(start_init), '�豸ϵͳ�汾�ֲ�', self.define_format_H3)
        self.write(worksheet, "A{}".format(start_init + 1), "ϵͳ�汾")
        self.write(worksheet, "B{}".format(start_init + 1), "�ܼ�")
        self.write(worksheet, "C{}".format(start_init + 1), "ͨ����")
        self.write(worksheet, "D{}".format(start_init + 1), "ʧ����")
        temp = 2

        for key, value in self.data["platformVersion"].iteritems():
            worksheet.set_row(start_init + temp, 30)
            self.write(worksheet, "A" + str(start_init + temp), key)
            self.write(worksheet, "B" + str(start_init + temp), value.get('success', 0) + value.get('fail', 0))
            self.write(worksheet, "C" + str(start_init + temp), value.get('success', 0))
            self.write_red(worksheet, "D" + str(start_init + temp), value.get('fail', 0))
            temp += 1
        self.bar(worksheet, 'ϵͳ�汾�ֲ�', 'E{}'.format(start_init),
                 '$A${}:$A${}'.format(start_init + 2, start_init + temp - 1),
                 '$C${}:$C${}'.format(start_init + 2, start_init + temp - 1),
                 '$D${}:$D${}'.format(start_init + 2, start_init + temp - 1))

        start_init = start_init + temp if temp >= 7 else start_init + 7
        worksheet.merge_range('A{0}:D{0}'.format(start_init), '�豸�ֱ��ʷֲ�', self.define_format_H3)
        self.write(worksheet, "A{}".format(start_init + 1), "�ֱ���")
        self.write(worksheet, "B{}".format(start_init + 1), "�ܼ�")
        self.write(worksheet, "C{}".format(start_init + 1), "ͨ����")
        self.write(worksheet, "D{}".format(start_init + 1), "ʧ����")
        temp = 2

        for key, value in self.data["display"].iteritems():
            worksheet.set_row(start_init + temp, 30)
            self.write(worksheet, "A" + str(start_init + temp), key)
            self.write(worksheet, "B" + str(start_init + temp), value.get('success', 0) + value.get('fail', 0))
            self.write(worksheet, "C" + str(start_init + temp), value.get('success', 0))
            self.write_red(worksheet, "D" + str(start_init + temp), value.get('fail', 0))
            temp += 1
        self.bar(worksheet, '�ֱ��ʷֲ�', 'E{}'.format(start_init),
                 '$A${}:$A${}'.format(start_init + 2, start_init + temp - 1),
                 '$C${}:$C${}'.format(start_init + 2, start_init + temp - 1),
                 '$D${}:$D${}'.format(start_init + 2, start_init + temp - 1))

    def test_compati_detail(self, worksheet):
        # �������еĿ��
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 15)
        worksheet.set_column("H:H", 15)
        worksheet.set_column("I:I", 30)
        worksheet.set_column("J:J", 17)
        worksheet.set_column("K:K", 15)

        for i in range(len(self.data["devices_detail"])+2):
            worksheet.set_row(i, 30)

        worksheet.merge_range('A1:K1', '��������', self.define_format_H2)
        self.write_bg(worksheet, "A2", 'Ʒ��')
        self.write_bg(worksheet, "B2", '�ͺ�')
        self.write_bg(worksheet, "C2", 'ϵͳ�汾')
        self.write_bg(worksheet, "D2", '�ֱ���')
        self.write_bg(worksheet, "E2", 'UI��������')
        self.write_bg(worksheet, "F2", '��װ')
        self.write_bg(worksheet, "G2", 'ж��')
        self.write_bg(worksheet, "H2", '���Խ��')
        self.write_bg(worksheet, "I2", 'ʧ��ԭ��')
        self.write_bg(worksheet, "J2", '��ͼ')
        self.write_bg(worksheet, "K2", '��־')

        temp = 3
        for item in self.data["devices_detail"]:
            if item.get("test_result") == 'success':
                self.write(worksheet, "A" + str(temp), item.get("manufacturer"))
                self.write(worksheet, "B" + str(temp), item.get("deviceName"))
                self.write(worksheet, "C" + str(temp), item.get("platformVersion"))
                self.write(worksheet, "D" + str(temp), item.get("display"))
                self.write(worksheet, "E" + str(temp), item.get("test_ui_result"))
                self.write(worksheet, "F" + str(temp), item.get("test_install"))
                self.write(worksheet, "G" + str(temp), item.get("test_uninstall"))
                self.write(worksheet, "H" + str(temp), item.get("test_result"))
                self.write(worksheet, "I" + str(temp), item.get("test_reason"))
            else:
                self.write_red(worksheet, "A" + str(temp), item.get("manufacturer"))
                self.write_red(worksheet, "B" + str(temp), item.get("deviceName"))
                self.write_red(worksheet, "C" + str(temp), item.get("platformVersion"))
                self.write_red(worksheet, "D" + str(temp), item.get("display"))
                self.write_red(worksheet, "E" + str(temp), item.get("test_ui_result"))
                self.write_red(worksheet, "F" + str(temp), item.get("test_install"))
                self.write_red(worksheet, "G" + str(temp), item.get("test_uninstall"))
                self.write_red(worksheet, "H" + str(temp), item.get("test_result"))
                self.write_red(worksheet, "I" + str(temp), item.get("test_reason"))

            if item.get("test_image"):
                worksheet.insert_image('J' + str(temp), item["test_image"],
                                       {'x_scale': 0.3, 'y_scale': 0.2, 'border': 1})
                worksheet.set_row(temp - 1, 130)
            else:
                self.write(worksheet, "J" + str(temp), item.get("test_image"))
            if item.get("test_log"):
                worksheet.write_url('K' + str(temp), item["test_log"], self.set_format({'bold': True, 'underline':  1, 'valign': 'vcenter', 'border':1}), "������־")
            else:
                self.write(worksheet, "K" + str(temp), item.get("test_log"))
            temp = temp + 1

    def perf_init(self, worksheet):
        # �������еĿ��
        worksheet.set_column("A:A", 15)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 10)
        worksheet.set_column("F:F", 30)
        worksheet.set_column("G:G", 15)
        worksheet.set_column("H:H", 20)

        for i in range(58):
            worksheet.set_row(i, 30)

        worksheet.merge_range('A1:H1', 'APP���ܲ��Ա���', self.define_format_H1)
        worksheet.merge_range('A2:H2', 'Ӧ�û�����Ϣ', self.define_format_H2)

        self.write_bg(worksheet, "A3", 'APP����')
        self.write_bg(worksheet, "A4", '��������')

        self.write(worksheet, "B3", self.data["app_info"]["app_name"])
        self.write(worksheet, "B4", self.data["app_info"]["test_platform"])

        self.write_bg(worksheet, "C3", "APP�汾")
        self.write_bg(worksheet, "C4", "��������")

        self.write(worksheet, "D3", self.data['app_info']["app_version"])
        self.write(worksheet, "D4", self.data["app_info"]["network"])

        self.write_bg(worksheet, "E3", "APP����")
        self.write_bg(worksheet, "E4", "���ʱ��")

        self.write(worksheet, "F3", self.data["app_info"]["app_package"])
        self.write(worksheet, "F4", self.data["test_results"]["start_time"])

        self.write_bg(worksheet, "G3", "APP��С")
        self.write_bg(worksheet, "G4", "����ʱ��")

        self.write(worksheet, "H3", self.data['app_info']['app_size'])
        self.write(worksheet, "H4", self.data["test_results"]["total_time"])

        worksheet.merge_range('A5:H5', '�����豸����', self.define_format_H2)
        self.write_bg(worksheet, "A6", "�豸�ͺ�")
        self.write_bg(worksheet, "C6", "ϵͳ�汾")
        self.write_bg(worksheet, "E6", "CPU�汾")
        self.write_bg(worksheet, "G6", "�ֱ���")

        self.write(worksheet, "B6", '%s(%s)'%(self.data["device"]["manufacturer"],self.data["device"]["deviceName"]))
        self.write(worksheet, "D6", self.data["device"]["platformVersion"])
        self.write(worksheet, "F6", self.data["device"]["cpuPlatform"])
        self.write(worksheet, "H6", self.data["device"]["display"])

        worksheet.merge_range('A7:H7', '���Խ��', self.define_format_H2)
        self.write_bg(worksheet, "A8", "����ʱ��(ms)")
        worksheet.merge_range("B8:C8", "ƽ��CPU(%)", self.wd.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bg_color': 'silver', 'border': 1}))
        worksheet.merge_range("D8:E8", "ƽ���ڴ�(MB)", self.wd.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bg_color': 'silver', 'border': 1}))
        self.write_bg(worksheet, "F8", "������")
        self.write_bg(worksheet, "G8", "��ʼ����")
        self.write_bg(worksheet, "H8", "ʵʱ����")

        self.write(worksheet, "A9", self.data["test_results"].get("startup_time"))
        worksheet.merge_range("B9:C9", self.data["test_results"].get("avg_cpu"), self.wd.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1}))
        worksheet.merge_range("D9:E9", self.data["test_results"].get("avg_mem"), self.wd.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1}))
        self.write(worksheet, "F9", self.data["test_results"].get("flow"))
        self.write(worksheet, "G9", self.data["test_results"].get("start_power"))
        self.write(worksheet, "H9", self.data["test_results"].get("end_power"))

        worksheet.merge_range('A10:H10', '�������ݸ���ͼ', self.define_format_H2)
        chart_index = 11
        data_lenth = len(self.data['test_detail'])+3
        self.cpu_line(worksheet, 'CPU', 'A{}'.format(chart_index), '$A${}:$A${}'.format(3, data_lenth),
                 '$B${}:$B${}'.format(3, data_lenth),
                 '$C${}:$C${}'.format(3, data_lenth))
        self.mem_line(worksheet, '�ڴ�', 'A{}'.format(chart_index+8), '$A${}:$A${}'.format(3, data_lenth),
                 '$D${}:$D${}'.format(3, data_lenth),
                 '$E${}:$E${}'.format(3, data_lenth),
                 '$F${}:$F${}'.format(3, data_lenth))
        self.line(worksheet, '����', '����', 'A{}'.format(chart_index+16), '$A${}:$A${}'.format(3, data_lenth),
                  '$G${}:$G${}'.format(3, data_lenth))
        self.flow_line(worksheet, '����', 'A{}'.format(chart_index + 24), '$A${}:$A${}'.format(3, data_lenth),
                      '$H${}:$H${}'.format(3, data_lenth),
                      '$I${}:$I${}'.format(3, data_lenth),
                      '$J${}:$J${}'.format(3, data_lenth))
        self.line(worksheet, '�߳���', '�߳���', 'A{}'.format(chart_index + 32), '$A${}:$A${}'.format(3, data_lenth),
                  '$K${}:$K${}'.format(3, data_lenth))
        self.line(worksheet, 'FPS', 'FPS', 'A{}'.format(chart_index + 40), '$A${}:$A${}'.format(3, data_lenth),
                  '$L${}:$L${}'.format(3, data_lenth))
        if self.data["test_results"]["crash"]:
            self.write_bg(worksheet, "A{}".format(chart_index + 48), 'Crash')
            worksheet.merge_range('B{0}:H{0}'.format(chart_index + 48), str(self.data["test_results"]['crash']))
            worksheet.set_row(chart_index + 47, 60)

    def test_perf_detail(self, worksheet):
        # �������еĿ��
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 15)
        worksheet.set_column("C:C", 15)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 15)
        worksheet.set_column("H:H", 15)
        worksheet.set_column("I:I", 15)
        worksheet.set_column("J:J", 15)
        worksheet.set_column("K:K", 15)
        worksheet.set_column("L:L", 15)

        worksheet.set_row(0, 30)
        worksheet.set_row(1, 30)

        worksheet.merge_range('A1:L1', '������������', self.define_format_H2)
        self.write_bg(worksheet, "A2", 'ʱ��')
        self.write_bg(worksheet, "B2", 'Ӧ��ռ��CPU')
        self.write_bg(worksheet, "C2", '��ռ��CPU')
        self.write_bg(worksheet, "D2", '���ڴ�(MB)')
        self.write_bg(worksheet, "E2", 'Native(MB)')
        self.write_bg(worksheet, "F2", 'Dalvik(MB)')
        self.write_bg(worksheet, "G2", '����')
        self.write_bg(worksheet, "H2", '����(Kb/s)')
        self.write_bg(worksheet, "I2", '����')
        self.write_bg(worksheet, "J2", '����')
        self.write_bg(worksheet, "K2", '�߳���')
        self.write_bg(worksheet, "L2", 'FPS')

        temp = 3
        for item in self.data["test_detail"]:
            worksheet.set_row(temp-1, 30)
            self.write(worksheet, "A" + str(temp), item.get("ʱ��"))
            self.write_num(worksheet, "B" + str(temp), item.get("Ӧ��ռ��CPU"))
            self.write_num(worksheet, "C" + str(temp), item.get("��ռ��CPU"))
            self.write_num(worksheet, "D" + str(temp), item.get("���ڴ�(MB)"))
            self.write_num(worksheet, "E" + str(temp), item.get("Native(MB)"))
            self.write_num(worksheet, "F" + str(temp), item.get("Dalvik(MB)"))
            self.write_num(worksheet, "G" + str(temp), item.get("����"))
            self.write_num(worksheet, "H" + str(temp), item.get("����(Kb/s)"))
            self.write_num(worksheet, "I" + str(temp), item.get("����"))
            self.write_num(worksheet, "J" + str(temp), item.get("����"))
            self.write_num(worksheet, "K" + str(temp), item.get("�߳���"))
            self.write_num(worksheet, "L" + str(temp), item.get("FPS"))
            temp += 1

    def close(self):
        self.wd.close()

    def set_format(self, option):
        return self.wd.add_format(option)

    def write(self, worksheet, cl, data):
        return worksheet.write(cl, data, self.wd.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1}))

    def write_num(self, worksheet, cl, data):
        return worksheet.write(cl, float(data), self.wd.add_format({'align': 'center', 'valign': 'vcenter', 'border': 1}))

    def write_bg(self, worksheet, cl, data):
        return worksheet.write(cl, data, self.wd.add_format(
            {'align': 'center', 'valign': 'vcenter', 'bg_color': 'silver', 'border': 1}))

    def write_red(self, worksheet, cl, data):
        return worksheet.write(cl, data, self.wd.add_format(
            {'align': 'center', 'valign': 'vcenter', 'font_color': 'red', 'border': 1}))

    def set_row(self, worksheet, num, height):
        worksheet.set_row(num, height)

    def pie(self, worksheet):
        chart1 = self.wd.add_chart({'type': 'pie'})
        chart1.add_series({
            'categories': '=�����ܿ�!$C$7:$D$7',
            'values': '=�����ܿ�!$C$8:$D$8',
            'data_labels': {'value': True},
            'points': [
                {'fill': {'color': 'green'}},
                {'fill': {'color': 'red'}},
            ],
        })
        chart1.set_title({'name': '����ͳ��'})
        worksheet.insert_chart('E7', chart1, {'y_scale': 0.64, 'x_scale': 1.07})

    def bar(self, worksheet, chart_name, position, categories, value1, value2, x_scale=1.07, y_scale=1):
        chart1 = self.wd.add_chart({'type': 'bar', 'subtype': 'stacked'})
        chart1.add_series({
            'name': 'ͨ����',
            'categories': '=�����ܿ�!{}'.format(categories),
            'values': '=�����ܿ�!{}'.format(value1),
            'data_labels': {'value': True},
        })
        chart1.add_series({
            'name': 'ʧ����',
            'categories': '=�����ܿ�!{}'.format(categories),
            'values': '=�����ܿ�!{}'.format(value2),
            'data_labels': {'value': True},
        })
        chart1.set_title({'name': chart_name})
        worksheet.insert_chart(position, chart1, {'y_scale': y_scale, 'x_scale': x_scale})

    def cpu_line(self, worksheet, chart_name, position, categories, value1, value2):
        chart1 = self.wd.add_chart({'type': 'line'})
        chart1.add_series({
            'name': 'Ӧ��ռ��CPU',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value1),
            'data_labels': {'value': True},
        })
        chart1.add_series({
            'name': '��ռ��CPU',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value2),
            'data_labels': {'value': True},
        })
        chart1.set_title({'name': chart_name})
        worksheet.insert_chart(position, chart1, {'y_scale': 1, 'x_scale': 2.2})

    def mem_line(self, worksheet, chart_name, position, categories, value1, value2, value3):
        chart1 = self.wd.add_chart({'type': 'line'})
        chart1.add_series({
            'name': '���ڴ�(MB)',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value1),
            'data_labels': {'value': True},
        })
        chart1.add_series({
            'name': 'Native(MB)',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value2),
            'data_labels': {'value': True},
        })
        chart1.add_series({
            'name': 'Dalvik(MB)',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value3),
            'data_labels': {'value': True},
        })
        chart1.set_title({'name': chart_name})
        worksheet.insert_chart(position, chart1, {'y_scale': 1, 'x_scale': 2.2})

    def flow_line(self, worksheet, chart_name, position, categories, value1, value2, value3):
        chart1 = self.wd.add_chart({'type': 'line'})
        chart1.add_series({
            'name': '����(Kb/s)',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value1),
            'data_labels': {'value': True},
        })
        chart1.add_series({
            'name': '����',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value2),
            'data_labels': {'value': True},
        })
        chart1.add_series({
            'name': '����',
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value3),
            'data_labels': {'value': True},
        })
        chart1.set_title({'name': chart_name})
        worksheet.insert_chart(position, chart1, {'y_scale': 1, 'x_scale': 2.2})

    def line(self, worksheet, chart_name, name, position, categories, value):
        chart1 = self.wd.add_chart({'type': 'line'})
        chart1.add_series({
            'name': name,
            'categories': '=��������!{}'.format(categories),
            'values': '=��������!{}'.format(value),
            'data_labels': {'value': True},
        })
        chart1.set_title({'name': chart_name})
        worksheet.insert_chart(position, chart1, {'y_scale': 1, 'x_scale': 2.2})


if __name__ == '__main__':
    # data = {
    #     'app_info': {'app_name': '\xe8\xae\xa1\xe7\xae\x97\xe5\x99\xa8', 'test_platform': 'Android', 'network': 'WIFI',
    #                  'app_package': 'com.example.ljh99.calculator', 'app_version': '1.0', 'app_size': '2.0M'},
    #     'test_results': {'total_time': 41627, 'testcase_total': 1, 'testcase_pass': 1,
    #                      'start_time': '20180816 09:45:52.958', 'testcase_fail': 0, 'status': 'Finish',
    #                      'test_devices': 2}, 'devices_detail': [
    #         {u'deviceName': u'meizu_PRO6Plus', u'test_reason': u'', u'network': u'WIFI', u'udid': u'10.200.22.129:7401',
    #          u'appium_ip': u'local', u'test_install': u'success', u'platformVersion': u'7.0.0', u'appium_port': 4726,
    #          u'test_name': u'add', u'test_image': u'', u'serial': u'M960BDRB227NU', u'test_result': u'success',
    #          u'display': u'1440x2560', u'manufacturer': u'MEIZU'},
    #         {u'deviceName': u'LLD-AL00', u'test_reason': u'', u'network': u'WIFI', u'udid': u'10.200.22.129:7405',
    #          u'appium_ip': u'local', u'test_install': u'success', u'platformVersion': u'8.0.0', u'appium_port': 4725,
    #          u'test_name': u'add', u'test_screenshot': u'', u'serial': u'MKJNW18511012677', u'test_result': u'success',
    #          u'display': u'1080x2160', u'manufacturer': u'HUAWEI'},
    #         {u'deviceName': u'LLD-AL01', u'test_reason': u'', u'network': u'WIFI', u'udid': u'10.200.22.129:7405',
    #          u'appium_ip': u'local', u'test_install': u'success', u'platformVersion': u'8.0.0', u'appium_port': 4725,
    #          u'test_name': u'add', u'test_image': r'D:\Users\chenlb001\Desktop\123.png', u'serial': u'MKJNW18511012677',
    #          u'test_result': u'fail', u'display': u'1080x2160', u'manufacturer': u'HUAWEI'}],
    #     'platformVersion': {u'7.0.0': {u'success': 1}, u'8.0.0': {u'success': 1, u'fail': 1}},
    #     'display': {u'1080x2160': {u'success': 1, u'fail': 1}, u'1440x2560': {u'success': 1}},
    #     'manufacturer': {u'HUAWEI': {u'success': 1, u'fail': 1}, u'MEIZU': {u'success': 1}}}
    # workbook = xlsxwriter.Workbook('GetReport.xlsx')
    # worksheet = workbook.add_worksheet("�����ܿ�")
    # worksheet2 = workbook.add_worksheet("��������")
    # bc = OperateReport(wd=workbook, data=data)
    # bc.init(worksheet)
    # bc.test_detail(worksheet2)
    # bc.close()

    data = {'app_info': {"app_name":"������", 'test_platform': 'Android', 'app_package': 'com.example.ljh99.calculator', 'app_version': '1.0',
                        'app_size': '2.0M', 'network': 'WIFI'},
              'device':  {u'deviceName': u'LLD-AL00', u'network': u'WIFI','cpuPlatform': u'exynos5',
             u'platformVersion': u'8.0.0', u'display': u'1080x2160', u'manufacturer': u'HUAWEI'},
            'test_results': {'total_time':'10s', 'start_time':'2018-09-03 18:18:33.664000','startup_time':854}}
    df = pd.read_csv('./20180831_10-22-02.csv')
    data['test_results']['avg_cpu'] = round(df['Ӧ��ռ��CPU'].mean(), 2)
    data['test_results']['avg_mem'] = round(df['���ڴ�(MB)'].mean(), 2)
    data['test_results']['flow'] = df['����(Kb/s)'].sum()
    data['test_results']['start_power'] = df['����'].max()
    data['test_results']['end_power'] = df['����'].min()
    data['test_detail'] = df.to_dict('records')
    workbook = xlsxwriter.Workbook('Report.xlsx')
    worksheet = workbook.add_worksheet("�����ܿ�")
    worksheet2 = workbook.add_worksheet("��������")
    bc = OperateReport(wd=workbook, data=data)
    bc.test_perf_detail(worksheet2)
    bc.perf_init(worksheet)
    bc.close()

