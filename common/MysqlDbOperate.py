#-*- coding:utf-8 -*-

import mysql.connector
import time
from titanrun.common.Result import Result


class RHMysql(object):
    def __init__(self,usr="fhrsopr",pwd="Fhrsopr123!",ip="100.69.13.43",port="4308",db="fhrs",charset="utf8"):
        self.ip = ip
        self.port = port
        self.db = db
        self.usr = usr
        self.pwd = pwd
        self.charset = charset
        retry_count = 3
        backoff = 1.2
        count = 0
        while count < retry_count:
            try:
                self.conn = mysql.connector.connect(host=self.ip,port=self.port,db=self.db,user=self.usr,passwd=self.pwd,charset=self.charset)
                self.cursor = self.conn.cursor()
                return
            except Exception:
                time.sleep(backoff)
                count = count + 1
        if retry_count == 3:
            raise Exception("Unable to connect to Database after 3 retries.")
    def fetchall_query(self, sql, param={}):
        if len(param) > 0:
            self.cursor.execute(sql, param)
        else:
            self.cursor.execute(sql)
        retval = self.cursor.fetchall()
        return retval
#执行查询语句，返回第一行的数据
    def fetchone_query(self, sql):
        self.cursor.execute(sql)
        retval = self.cursor.fetchone()
        return retval

    def execute_query(self, sql, param={}):
        if len(param) > 0:
            retval = self.cursor.execute(sql, param)
        else:
            retval = self.cursor.execute(sql)
        return retval

    '''
    查询多条返回 True， False    
    param参数可传list或dict， EG：param = ["1186020000068016"]，param = {"apply_bar_code": "1186020000068016"}
    
    '''
    def execute_query_many(self, sql_list, param=[]):
        result_list = []
        result = Result()
        for sql in sql_list:
            if "%s" in sql or "%d" in sql or ":" in sql:
                self.cursor.execute(sql, param)
            else:
                self.cursor.execute(sql)
            retval = self.cursor.fetchone()
            result_list.append(retval)
        result_list = [i[0] for i in result_list]
        if len(result_list) == 1:
            if result_list[0] == 1:
                result.flag = True
            else:
                result.flag = False
        else:
            result.flag = reduce(lambda x, y: x == y and x != 0, result_list)
        return result

    def check_query_count(self,sql):
        flag = False
        data = self.fetchone_query(sql)
        if int(data[0]) >= 1:
            flag = True
        return flag
#只支持第一列第一个结果的对比
    def check_query_equal(self,sql_list,R_target):
        result_list = []
        result = Result()
        param=[]
        for sql in sql_list:
            if "%s" in sql or "%d" in sql or ":" in sql:
                self.cursor.execute(sql, param)
            else:
                self.cursor.execute(sql)
            retval = self.cursor.fetchone()
            result_list.append(retval)
        result_list = [i[0] for i in result_list]
        if len(result_list) == 1:
            if result_list[0] == R_target:
                result.flag = True
            else:
                result.flag = False
        else:
            result.flag = reduce(lambda x, y: x == y and x == R_target, result_list)
        return result

    '''
    数据回滚/insert数据
    '''
    def execute_rollback_sql(self, sql_list, param=[]):
        for sql in sql_list:
            if "%s" in sql or "%d" in sql or ":" in sql:
                self.cursor.execute(sql, param)
            else:
                self.cursor.execute(sql)
        self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    param = ["1186020000068016"]
    # param = {"apply_bar_code": "1186020000068016"}
    sqltest = RHMysql(usr="fhrsopr",pwd="Fhrsopr123!",ip="100.69.13.43",port="4308",db="fhrs")

    sql = ["select count(1) from uw_apply_info where apply_bar_code = :1 and apply_status = 09", "select count(1) from uw_apply_info where apply_bar_code = :1 and apply_status = 06"]

    param=("CMHK_486558114786922496")
    SS=["SELECT count(*) FROM fhrs.fhrs_top_manager where company_id ='%s'"]
    # sql = ["select count(1) from uw_apply_info where apply_bar_code = :apply_bar_code and apply_status = 09", "select count(1) from uw_apply_info where apply_bar_code = :apply_bar_code and apply_status = 06"]
    result = sqltest.execute_query_many(SS,param)
    # result = sqltest.check_query_equal(SS,7)
    print result.flag