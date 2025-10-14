import pymssql
from pymssql import _mssql
from pymssql import _pymssql
import uuid
import decimal
import os
import time
# 还原数据库
def RestoreDB(dbname,dbpath,newname,tempfile,logiclist,hst,pot,usr,pwd,dbN):
    con = SQLcon(hst,pot,usr,pwd,dbN)
    if con != False:
        con.autocommit(True)
        cur = con.cursor()
        dbfile = dbpath + '\\' + dbname
        dbfile = os.path.abspath(dbfile)
        tempfile = os.path.abspath(tempfile)
        # 构建新的sql，通过修改文件位置保证物理文件不重复
        sql1 = f"RESTORE DATABASE [{newname}] FROM DISK = N'{dbfile}' WITH Replace,stats = 10"
        sql2 = f",move '{logiclist[0]}' to '{tempfile}\{newname}.mdf'"
        sql3 = f",move '{logiclist[1]}' to '{tempfile}\{newname}_log.ldf'"
        sql = sql1 + sql2 + sql3
        # print(sql)
        # 检查同名数据库是否存在
        if ExistcheckDb(newname,hst,pot,usr,pwd,dbN) == [[]]:
            try:
                cur.execute(sql)
                con.autocommit(False)
                cur.close()
                # print('Restore Success')
                return True
            except Exception as e:
                con.autocommit(False)
                cur.close()
                # print('Restore Failed')
                res = ErrorMark(str(e))
                return res
        else:
            # print('The DBName Exists Right now')
            return False
    else:
        # print('SQL not Connect')
        return 'Unconnect'
# 备份数据库
def BackupDB(dbname,backpath,newname,hst,pot,usr,pwd,dbN):
    con = SQLcon(hst, pot, usr, pwd, dbN)
    if con != False:
        con.autocommit(True)
        cur = con.cursor()
        newfile = backpath + '\\' + newname
        newfile = os.path.abspath(newfile)
        # 备份数据库的脚本(with format是关键,是覆盖备份,如果有同名备份的话会被覆盖)
        sql = f"backup database {dbname} to disk='{newfile}' with format"
        # 校验备份目录是否合法以及存在
        # print(sql)
        dircheck = mkdir(backpath)
        if dircheck != 'Invalid FileName':
            try:
                cur.execute(sql)
                con.autocommit(False)
                cur.close()
                # print('Backup Success')
                return True
            except Exception as e:
                con.autocommit(False)
                cur.close()
                # print('Backup Failed')
                res = ErrorMark(str(e))
                return res
        else:
            # print('Invalid FileName')
            # print('Backup Failed')
            return False
    else:
        # print('SQL not Connect')
        return 'Unconnect'
# 删除数据库
def DeleteDB(dbname,hst,pot,usr,pwd,dbN):
    con = SQLcon(hst, pot, usr, pwd, dbN)
    if con != False:
        con.autocommit(True)
        cur = con.cursor()
        sqlonly = f'ALTER DATABASE [{dbname}] SET  SINGLE_USER WITH ROLLBACK IMMEDIATE'
        sql = f'USE master DROP DATABASE {dbname}'
        # a = ExistcheckDb(dbname,hst,pot,usr,pwd,dbN)
        # print(a)
        if ExistcheckDb(dbname,hst,pot,usr,pwd,dbN) != [[]]:
            try:
                cur.execute(sqlonly)
                time.sleep(3)
                cur.execute(sql)
                while cur.nextset():
                    pass
                con.autocommit(False)
                cur.close()
                # print('Delete Success')
                return True
            except Exception as e:
                con.autocommit(False)
                cur.close()
                # print('Delete Failed')
                res = ErrorMark(str(e))
                return res
        else:
            # print("The DBName Doesn't Exist")
            return False

    else:
        # print('SQL not Connect')
        return 'Unconnect'
# 错误标志(把已知错误整理了,后续使用正则重新处理)
def ErrorMark(e):
    if r'error 5(\xe6\x8b\x92\xe7\xbb\x9d\xe8\xae\xbf\xe9\x97\xae\xe3\x80\x82)' in e:
        # print (1)
        return '错误5：拒绝访问'
    elif r'error 3(\xe7\xb3\xbb\xe7\xbb\x9f\xe6\x89\xbe\xe4\xb8\x8d\xe5\x88\xb0\xe6\x8c\x87\xe5\xae\x9a\xe7\x9a\x84\xe8\xb7\xaf\xe5\xbe\x84\xe3\x80\x82)' in e:
        # print(2)
        return '错误3：系统找不到指定的路径'
    elif r'does not exist. Make sure that the name is entered correctly' in e:
        # print(3)
        return '错误：备份的数据库不存在.请确认数据库名字是否填写错误'
    else:
        # print(4)
        return e
# 判断数据库是否存在
def ExistcheckDb(dbname,hst,pot,usr,pwd,dbN):
    con = SQLcon(hst, pot, usr, pwd, dbN)
    if con != False:
        rt = []
        con.autocommit(True)
        cur = con.cursor()
        sqlcheck = f"select * from sysdatabases where name = '{dbname}'"
        try:
            cur.execute(sqlcheck)
            rs = cur.fetchall()
            con.autocommit(False)
            cur.close()
            rt.append(rs)
        except Exception as e:
            return (str(e))
        return rt
    else:
        # print('SQL not Connect')
        return 'Unconnect'
#获取备份文件实际的数据库逻辑文件信息
def LogicalData(dbname,dbpath,hst,pot,usr,pwd,dbN):
    con = SQLcon(hst, pot, usr, pwd, dbN)
    if con != False:
        con.autocommit(True)
        cur = con.cursor()
        dbfile = dbpath +'\\'+dbname
        dbfile = os.path.abspath(dbfile)
        # 核心点就在逻辑文件可能会出现和现有数据库重复的情况
        sql = f"RESTORE FILELISTONLY from disk='{dbfile}'"
        # print(sql)
        try:
            cur.execute(sql)
            rt = cur.fetchall()
            rs = [rt[0][0],rt[1][0]]
            con.autocommit(False)
            cur.close()
            return rs
        except Exception as e:
            return False
    else:
        return 'Unconnect'
# 检查目录是否合法\存在
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        try:
            os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径
            # print("---  目录生成中...  ---")
            # print("---  OK  ---")
            return 'Create file Success'
        except Exception as e:
            # print('非法的目录名')
            return 'Invalid FileName'
    else:
        # print(f"---  {path}目录已存在！  ---")
        return 'Exists'
# 检测数据库是否连接成功
def SQLcon(hst,pot,usr,pwd,dbN):
    try:
        con = pymssql.connect(host=hst, port=pot, user=usr, password=pwd, database=dbN)
        return con
    except:
        return False


if __name__ ==  '__main__':
    # t = BackupDB('Nice','E:\\','ZZ')
    # t = BackupDB('Nice','E:\\','ZZ','127.0.0.1','1433','sa','123','master')
    # logiclist = LogicalData('000001_建瓯天茂塑胶_20210605100743','E:\\test','127.0.0.1','1433','sa','123','master')
    # rest = RestoreDB('000001_建瓯天茂塑胶_20210605100743','E:\\test','broken','E:\\test',logiclist,'127.0.0.1','1433','sa','123','master')
    d = DeleteDB('origin','127.0.0.1','1433','sa','123','master')
