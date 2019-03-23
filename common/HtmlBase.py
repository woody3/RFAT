# encoding=UTF-8

"""
HtmlParse����
"""

import re
import json
import types
import requests

from robot.api import logger

from business.conf import EnvSetting
from titanrun.common import Core
from titanrun.common.Core import get_var
from titanrun.common.DbOperate import RHOracle
from titanrun.common.IniParser import RHIniParser
from robot.libraries.BuiltIn import _Verify
from titanrun.common.Result import Result


session = requests.session()


class HtmlBase(object):

    def __init__(self, data_source, version):
        self.dic_args = {}
        self.result = Result()
        self.Verify = _Verify()
        self.upload_files = {}
        self.cur_path = ""
        self.ini_path = ""
        self.urlparam = ""
        self.default_data_dict = {}
        self.version = version
        self.data_source = data_source

        # =========·������Ʒ��ִ�нӿڻ�ȡ�� eg��msp.apply.01;msp.apply:interface_a;interface_b ==========
        self.data_source_apis = self.data_source[0].split(":")  # �� ����datasource�ĵ�һ��Ԫ�ؽ��в��
        self.apis = self.html_replace_data(self.data_source_apis[1])  # ����ǽӿ���   ȡ���ӿ���
        self.interface_path_product = self.html_replace_data(self.data_source_apis[0])  # ����� msp.01
        self.api_name = self.interface_path_product[0].split(".")[0]  # ȡ���� msp
        self.api_len = len(self.apis)

        # ================��ȡ�ӿ�����=====================
        self.api_def_dic = EnvSetting.ENV_DEF_DIC
        self.db_def_dic = EnvSetting.ENV_DB_DIC
        self.version_dict = EnvSetting.VERSION
        self.env_pro_dic = self.api_def_dic.get(self.api_name)
        self.token_key = self.env_pro_dic.get("token_key", "")
        self.version_info = self.version_dict.get(version)
        self.version_port = self.version_info.get("port", self.env_pro_dic.get("port", ""))
        self.version_url = self.version_info.get("url", self.env_pro_dic.get("url", ""))
        self.version_uri = self.version_info.get("uri", self.env_pro_dic.get("uri", ""))
        self.version_url = self.concat_url()
        self.ini_name_list = self.env_pro_dic["api_ini_name"]

    def html_replace_data(self, data):
        data = str(data).strip().replace("\n", "").replace("��", "\"").replace("��", "\'").replace("��", "\'").replace("��", ";").decode("utf-8")
        if data.endswith(";"):
            data = data[:-1]
        return data.split(";")

    def concat_url(self):
        return "%s:%s/%s" % (self.version_url, self.version_port, self.version_uri)

    def get_productname(self, i):
        if len(self.interface_path_product) == 1:
            path_list = self.interface_path_product[0].split(".")
            if len(path_list) == 2:
                product_name = path_list[1]
            else:
                product_name = None
        else:
            path_list = self.interface_path_product[i].split(".")
            if len(path_list) == 2:
                product_name = path_list[1]
            else:
                product_name = None
        return product_name

    # ��ȡ�ӿ�·��
    def get_modelurl(self, ini_data, api):
        model_url_data = json.loads(ini_data.get_ini_info("MODEL_URL", "MODEL_URL_DATA"))
        if len(model_url_data.keys()) == 1:
            model_url = model_url_data.values()[0]
        else:
            model_url = model_url_data.get(api, "")
        return model_url

    # �滻html����
    def change_para_html(self, html_cont, data):
        if data == "":
            return html_cont

        replace_data = self.html_replace_data(data)
        for data in replace_data:
            if "=" not in data:
                raise Exception("error format,not found =")
            try:
                if ":=" not in data:
                    raise Exception("error format")
                sval = get_var(data.split(":=")[1])
                name = data.split(":=")[0]
                # �Բ�����num��str���� ���֣�222222�� str��'222222'
                if sval != "":
                    if Core.is_numeric(sval):
                        sval = int(sval)
                    elif "\'" in sval:
                        sval = sval.replace("\'", "")
                    elif sval.startswith("[") or sval.startswith("{"):
                        sval = Core.eval_str(sval)
                # ���������Ϊbool, null�Ĵ���
                if sval == 'false':
                    sval = False
                elif sval == 'true':
                    sval = True
                elif sval == 'null' or sval == "":
                    sval = None
                scmd = '''html_cont[%s]="%s" ''' % (name, sval)
                html_cont[name] = sval
            except Exception, e:
                raise Exception("error after %s, %s" % (scmd, str(e)))
        return html_cont

    # htmlĬ��form������
    def html_request(self, url, html, cookies={}, files={}, method="post", headers={}):
        if method == "get":
            response = session.get(url, params=html, headers=headers, cookies=cookies, verify=False)
        elif method == "uploadfiles":
            # headers = {}
            response = session.post(url, files=files, data=html, headers=headers, cookies=cookies, verify=False)
        else:
            response = session.post(url, data=html, headers=headers, cookies=cookies, verify=False)
        # print response.text
        return response.text

    # ���У��
    # ��json��ʽ����ģ��Ϊ:ResultInfoDesc:=�Զ��˱�ͨ��(������message);
    # json����ģ��Ϊ��error:=���׳ɹ�   ����ʵ��ֵΪ��"error":"���׳ɹ�"
    # ����Ϊlist��ģ��Ϊ��1.aaa:=bbbb   ���� 1:=bbbb
    def rh_html_check_result(self, input, response_json):
        data = str(input).strip().replace("\n", "").replace("��", "\"").replace("��", "\'").replace("��", "\'").replace(
            "��", ";")
        if data is None:
            raise Exception("error format,prepareResult is none.")

        flag = False
        # eval()������ֵ����
        # null = ""
        # true = True
        # false = False
        # ���ؽ��Ϊlist[]���� json��ʽ �Ƚ�
        if (response_json.startswith("[") or response_json.startswith("{")) and response_json not in ["[]", "{}"]:
            response_json = Core.eval_str(response_json)  # strת��list
            cmp_result = Core.rh_check_result(input, response_json)
            if "[success]" in cmp_result:
                flag = True
            else:
                return cmp_result
        # ���ؽ��Ϊtext
        else:
            except_message = data.split(":=")[1]
            if response_json.__contains__(except_message):
                flag = True
            else:
                return "[fail]:response data do not contains %s." % data
        if flag:
            return "[success]:response data contains %s." % data

    # �滻html ���õı���
    def change_in_html_dic(self, sdic, new_dic, html_cont):
        if new_dic != {}:
            if sdic.get("input", "") != "":
                for (sname, sval) in sdic.get("input", "").items():
                    try:
                        name = sname
                        vaule = new_dic[sval]
                        html_cont[name] = vaule
                    except Exception, e:
                        raise Exception("error after change, %s, %s" % (name, str(e)))

    # ��ȡ�ӿڷ��ص�json���ݣ�ȡ��Ӧ�ֶδ浽sdic
    def get_out_html_dic(self, sdic, response_json, pattern):
        out = {}
        if sdic.get("output", "") != "":
            if '<' not in response_json and '{' in response_json and '}' in response_json and not response_json.startswith('['):
                response_json = response_json[response_json.find('{'):response_json.rfind('}') + 1]
            i = -1
            if response_json.startswith("{") or response_json.startswith("["):
                # if response_json.startswith("{"):
                #     # ������Ϊresponse.text ����Ҫת��json����Ϊresponse.json()������
                #     response_json = json.loads(response_json)
                for (sname, sval) in sdic.get("output", "").items():
                    i += 1
                    try:
                        out[sname] = self.get_nestdict_value(sval, response_json)
                    except Exception, e:
                        logger.info("out arg %s not find" % sval)
            else:
                for (sname, sval) in sdic.get("output", "").items():
                    i += 1
                    p = re.compile(pattern[i])
                    value = p.findall(response_json)
                    try:
                        out[sname] = value[0]  # ȡƥ�䵽�ĵ�1��
                    except Exception, e:
                        logger.info("out arg %s not find" % sname)
        return out

    def get_new_dic(self, new_out_dic, out):
        for (k, v) in out.items():
            new_out_dic[k] = v
        return new_out_dic

    # a=111&b=222 ԭ��form����ʽת��dict
    def transfor_to_dict(self, data):
        if isinstance(data, dict):
            properties = data
        else:
            listdata = data.split("&")
            # print listdata
            properties = {}
            # a = 0
            for line in listdata:
                # a += 1
                if line.find("=") > 0:
                    strs = line.replace("\n", "").replace("\t|\n", "").split("=")
                    properties[strs[0]] = strs[1]
        return properties

    # JSESSIONID=0a51;_rf_profile=pppp; �ȸ�ʽת��dict       ����cookies
    def str_to_dict(self, data, pattern01, pattern02):
        listdata = data.replace(" ", "").split(pattern01)
        dictdata = {}
        for i in listdata:
            nv = i.split(pattern02)
            dictdata[nv[0]] = nv[1]
        return dictdata

    # �ϴ���Ƭ����, ����Ҫ�ϴ������������������dict
    def upload_files_format(self, filedata, path):
        """
        :param filedata:        # ����key�ش���value�Ǵ��ĸ����� ��"" ���ɡ�  eg: filedata = {"filename1": ""}
        :param path: 
        :return:         
            {
              "field1" : open("filePath1", "rb")),
              "field2" : open("filePath2", "rb")),
              "field3" : open("filePath3", "rb"))
            }
        """
        upload_files = {}
        for key in filedata.keys():
            if filedata[key] != "":
                filedata[key] = path + filedata[key]
            else:
                filedata[key] = ""
        for (k, v) in filedata.items():
            if v != "":
                vfile = open(v, 'rb')
                upload_files[k] = vfile
            else:
                upload_files[k] = ""
        return upload_files

    # �滻��ͬ�汾url, port����
    def change_url_port(self, url, change_port, change_url=""):
        j = [m.start() for m in re.finditer(":", url)][1] + 1
        if "RH_" in url:
            k = [m.start() for m in re.finditer("/", url)][2]
            oraginal_port = url[j:k]
        else:
            oraginal_port = url[j:]
        oraginal_url = url[:j-1]
        url = url.replace(oraginal_port, change_port)
        if change_url != "":
            url = url.replace(oraginal_url, change_url)
        return url

    # �滻url in out���õı���
    def change_in_html_urldic(self, sdic, new_dic, url, data=""):
        # �滻url�������滻�ı���
        if data != "":
            replace_data = self.html_replace_data(data)
            for data in replace_data:
                url_name = data.split(":=")[0]
                url_param = data.split(":=")[1]
                url = url.replace(url_name, url_param)
        # ����urlinput����Ҫ�滻�ı���������������Ҫ�滻�ı���һ�£��򲻻ᴦ��
        elif new_dic != {}:
            if sdic.get("urlinput", "") != "":
                for (sname, sval) in sdic.get("urlinput", "").items():
                    try:
                        name = sname
                        vaule = new_dic[sval]
                        url = url.replace(str(name), str(vaule))
                        # url = url.replace(vaule, "82612502bac711e78e43d0a637ed6da3") # �����޸ķǱ��û�����
                    except Exception, e:
                        raise Exception("error after change, %s" % name)
        # print url
        return url

    # ����token
    def change_in_token_dic(self, sdic, new_dic, token):
        if new_dic != {}:
            if sdic.get("headinput", "") != "":
                for (sname, sval) in sdic.get("headinput", "").items():
                    try:
                        name = sname
                        token = new_dic[sval]
                    except Exception, e:
                        raise Exception("error after change, %s" % name)
        return token

    # json�ϲ�    Ƕ�׵�jsonȡ��ֵ�ϲ���һ��
    # Json:{"a":"aa","b":['{"c":"cc","d":"dd"}',{"f":{"e":"ee"}}]} ����� Dic:{'a': 'aa', 'c': 'cc'', 'd': 'dd', 'e': 'ee }
    def get_format_dict(self, dictdata):
        for (k, v) in dictdata.items():
            if isinstance(v, list):
                for i in v:
                    if isinstance(i, dict):
                        new_dict = i.copy()
                        dictdata = dict(dictdata.items() + new_dict.items())
                dictdata.pop(k)
                if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
                    return dictdata
                else:
                    return self.get_format_dict(dictdata)
            else:
                if isinstance(v, dict):
                    new_dict = v.copy()
                    dictdata.pop(k)
                    dictdata = dict(dictdata.items() + new_dict.items())
                    if "{" not in str(dictdata)[1:-1] or "}" not in str(dictdata)[1:-1]:
                        return dictdata
                    else:
                        return self.get_format_dict(dictdata)
        return dictdata

    # ��ȡ�ֵ��е�objkey��Ӧ��ֵ���������ֵ�Ƕ��
    # dict:�ֵ�
    # objkey:Ŀ��key
    # default:�Ҳ���ʱ���ص�Ĭ��ֵ
    # PS:��Ƕ�׵�json����list����key������ͬ����ֻ�ܻ�ȡ����һ��key��ֵ����ֻ��ȡ��һ��key���Ա�
    def dict_get(self, dict, objkey, default=None):
        tmp = dict
        for k, v in tmp.items():
            if k == objkey:
                return v
            else:
                if type(v) is types.DictType:
                    ret = self.dict_get(v, objkey, default)
                    if ret is not default:
                        return ret
                elif type(v) is types.ListType:
                    for val in v:
                        ret = self.dict_get(val, objkey, default)
                        if ret is not default:
                            return ret
        return default

    # ��ȡ����Ƕ��list��json��Ӧ���±꣨key��ֵ
    # ��ʽ��keytag�� "2.a"      dict_data��[{"a": "111", "b": 222}, "bbbb", {"a": "555", "b": 222}]
    def get_nestdict_value(self, keytag, dict_data):
        if type(dict_data) not in [types.ListType, types.DictType]:     # ������ֵΪ "{}" ,"[]"���
            # dict_data = json.loads(dict_data)
            dict_data = Core.eval_str(dict_data)  # Ч��ͬ��
        # ���� "a": "[]" ���
        dict_data = self.dict_handle(dict_data)
        sname = keytag.strip()
        obj = scmd = realval = ""
        for i in sname.split("."):
            if Core.is_numeric(i):
                obj = "%s[%s]" % (obj, i)
            else:
                if 'str(' in i:
                    i = i[i.find('(')+1:-1]
                obj = "%s['%s']" % (obj, i)
        scmd = "%s%s" % ("dict_data", obj)
        try:
            realval = eval(scmd)
        except:
            return "[Failed]:cmd change error,eval(%s)" % scmd
        return realval

    def dict_handle(self, dict_data):
        """
        �÷�������jsonǶ���У�Ƕ�׵�json��list��str���͡�����Ҫeval���� eg: {"a": "[]"}  --> {"a": []}
        :param dict_data: 
        :return: 
        """
        if type(dict_data) in [types.DictType]:
            for k, v in dict_data.items():
                if type(v) in [types.StringType, types.UnicodeType] and (str(v).startswith("[") or str(v).startswith("{")):
                    v1 = Core.eval_str(v)
                    dict_data[k] = v1
                else:
                    pass
        elif type(dict_data) in [types.ListType]:
            for l in dict_data:
                self.dict_handle(l)
        return dict_data

    # �ж�ini�ļ���section��ȡֵ��û��Ĭ�Ϸ���{}
    def get_ini_value(self, ini_data, section_value, section_option):
        return str(ini_data.get_ini_info(section_value, section_option) if section_value in ini_data.get_ini_sections() else {})

    # ��װȡiniĬ�����ݷ���
    def get_ini_default_contant(self, ini_data, api=None, product_name=None):
        # ini_data = RHIniParser(ini_path)
        if api is None and product_name is None:
            default_contant = json.loads(self.get_ini_value(ini_data, "DATA", "ENV_DEFAULT_DATA"))
            request_method = json.loads(self.get_ini_value(ini_data, "METHED", "REQUEST_METHOD"))
            in_out_para_dic = json.loads(self.get_ini_value(ini_data, "PARA", "DICT_IN_OUT"))
            default_re_set = json.loads(self.get_ini_value(ini_data, "RE", "RE_SET"))
            sql_list = json.loads(self.get_ini_value(ini_data, "SQL", "SQL_DIC"))
            rollback_sqllist = json.loads(self.get_ini_value(ini_data, "DML_SQL", "DMLSQL_DIC"))
            return default_contant, request_method, in_out_para_dic, default_re_set, sql_list, rollback_sqllist
        elif product_name is None:
            if ".db" in api:
                sql_list = json.loads(self.get_ini_value(ini_data, "SQL", "SQL_DIC")).get(api, [])
                return sql_list
            elif ".dmldb" in api:
                rollback_sqllist = json.loads(self.get_ini_value(ini_data, "DML_SQL", "DMLSQL_DIC")).get(api, [])
                return rollback_sqllist
            else:
                default_contant = json.loads(self.get_ini_value(ini_data, "DATA", "ENV_DEFAULT_DATA")).get(api, "")
                request_method = json.loads(self.get_ini_value(ini_data, "METHED", "REQUEST_METHOD")).get(api, "")
                in_out_para_dic = json.loads(self.get_ini_value(ini_data, "PARA", "DICT_IN_OUT")).get(api, {})
                default_re_set = json.loads(self.get_ini_value(ini_data, "RE", "RE_SET")).get(api, "")
                return default_contant, request_method, in_out_para_dic, default_re_set
        else:
            if ".db" in api:
                sql_list = json.loads(self.get_ini_value(ini_data, "SQL", "SQL_DIC")).get(api, {}).get(product_name, [])
                return sql_list
            elif ".dmldb" in api:
                rollback_sqllist = json.loads(self.get_ini_value(ini_data, "DML_SQL", "DMLSQL_DIC")).get(api, {}).get(product_name, [])
                return rollback_sqllist
            else:
                default_contant = json.loads(self.get_ini_value(ini_data, "DATA", "ENV_DEFAULT_DATA")).get(api, "").get(product_name, "")
                request_method = json.loads(self.get_ini_value(ini_data, "METHED", "REQUEST_METHOD")).get(api, {}).get(product_name, "")
                in_out_para_dic = json.loads(self.get_ini_value(ini_data, "PARA", "DICT_IN_OUT")).get(api, {}).get(product_name, {})
                default_re_set = json.loads(self.get_ini_value(ini_data, "RE", "RE_SET")).get(api, {}).get(product_name, "")
                return default_contant, request_method, in_out_para_dic, default_re_set


