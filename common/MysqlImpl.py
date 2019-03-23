# -*- coding: utf-8 -*-


from business.script.MysqlDbOperate import RHMysql
from business.conf import EnvSetting


# ############################���DB�Ĵ���--Start##############################################################
def connect_db(self, version, sid, user=''):
    if user == '':
        user = EnvSetting.ENV_DB_DIC.get(sid)["db_usr"]
    sqlobj = RHMysql(user=user,
                     passwd=EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"],
                     host=EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                     db=EnvSetting.ENV_DB_DIC.get(sid)["db_name"], charset="utf8")
    return sqlobj


def check_sql(sql_list, db_usr, db_pwd, db_ip, db_name, param=[]):
    sqlobj = RHMysql(usr=db_usr, pwd=db_pwd, ip=db_ip, db=db_name)
    result = sqlobj.execute_query_many(sql_list, param)
    return result


def dml_sql(sql_list, db_usr, db_pwd, db_ip, db_name, param=[]):
    sqlobj = RHMysql(usr=db_usr, pwd=db_pwd, ip=db_ip, db=db_name)
    sqlobj.execute_rollback_sql(sql_list, param)


def check_db(sql_list, version, sid='slis', param=[]):
    result = check_sql(sql_list, EnvSetting.ENV_DB_DIC.get(sid)["db_usr"], EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"],
                            EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                            EnvSetting.ENV_DB_DIC.get(sid)["db_name"], param)
    return result


def dml_db(sql_list, version, sid='slis', param=[]):
    dml_sql(sql_list, EnvSetting.ENV_DB_DIC.get(sid)["db_usr"], EnvSetting.ENV_DB_DIC.get(sid)["db_pwd"],
                 EnvSetting.VERSION.get(version)[sid + "_db_ip"],
                 EnvSetting.ENV_DB_DIC.get(sid)["db_name"], param)

# ############################���DB�Ĵ���--END################################################################


