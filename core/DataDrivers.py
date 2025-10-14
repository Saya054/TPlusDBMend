import pyodbc
import os,sys,time
import logging

try:
    import pymssql
    PYMSSQL_AVAILABLE = True
except ImportError:
    PYMSSQL_AVAILABLE = False
    pymssql = None
from .basicFunc import tuple2list, tuple2listodbc,repath,hostREmake
from .FileFunctions import mkdir


class TsDBdriver(object):
    # 基础属性，加入一个驱动版本的值，self._dver
    def __init__(self,host,uname,upwd,driver,basedb):
        self._dver = driver
        self._hst  = hostREmake(host)
        self._unm  = uname
        self._pwd  = upwd
        self._odb  = basedb
        self._conn  = None
        self._ReConnect()
    def _ReConnect(self):
        if self._dver == 'pymssql driver':
            if not PYMSSQL_AVAILABLE:
                raise ImportError("pymssql module is not available. Please install it using: pip install pymssql")
            if not self._conn:
                try:
                    self._conn = pymssql.connect(host=self._hst, database=self._odb, user=self._unm,password=self._pwd, charset='utf8')
                except Exception as ex:
                    ex_type, ex_val, ex_stack = sys.exc_info()
                    return ex_val
            else:
                pass
        else:
            if not self._conn:
                if self._unm == '' and self._pwd == '':
                    try:
                        # pyodbc.connect(Trusted_Connection='yes', driver='{ODBC Driver 17 for SQL Server}', server='.',
                        #                database='master')
                        self._conn = pyodbc.connect(f"Trusted_Connection=yes;driver={self._dver};server={self._hst}; database={self._odb}; autocommit=True;TrustServerCertificate=yes")
                    except Exception as ex:
                        ex_type, ex_val, ex_stack = sys.exc_info()
                        return ex_val
                else:
                    try:
                        self._conn = pyodbc.connect(f"driver={self._dver}; server={self._hst}; UID={self._unm};PWD={self._pwd}; database={self._odb}; autocommit=True;TrustServerCertificate=yes")
                    except Exception as ex:
                        ex_type, ex_val, ex_stack = sys.exc_info()
                        return ex_val
            else:
                pass
    def __del__(self):
        if self._conn:
            self._conn.close()
            self._conn = None
    def _NewCursor(self):
        if self._conn is None:
            return False
        else:
            cur = self._conn.cursor()
            if cur:
                return cur
            else:
                print("#Error# Get New Cursor Failed")
                return False
    def _DelCursor(self, cur):
        if cur:
            cur.close()
        # 检查sql语句
    def PermitedUpdateSql(self, sql):
        rt = True
        lrsql = sql.lower()
        sql_elems = lrsql.strip().split()
        # 判断sql单词个数
        if len(sql_elems) < 3:
            rt = False
        elif sql_elems[0] == 'update':
            if 'set' not in sql_elems:
                rt = False
            else:
                rt = True
        elif sql_elems[0] == 'delete':
            if 'from' not in sql_elems:
                rt = False
            else:
                rt = True
        elif sql_elems[0] == 'insert':
            if sql_elems[1] != 'into':
                rt = False
            else:
                rt = True
        return rt
    # 导出结果
    def Export(self, sql, file_name, colfg='||'):
        rt = self.Query(sql)
        if rt:
            with open(file_name, 'a') as fd:
                for row in rt:
                    ln_info = ''
                    for col in row:
                        ln_info += str(col) + colfg
                    ln_info += '\n'
                    fd.write(ln_info)
    # 查询
    def Query(self, sql, nStart=0, nNum=-1):
        if self._dver =='pymssql driver':
            rt = []
            cur = self._NewCursor()
            if not cur:
                return False
            cur.execute(sql)
            if (nStart == 0) and (nNum == 1):
                rt.append(cur.fetchone())
            else:
                rs = cur.fetchall()
                if nNum == -1:
                    rt.extend(rs[nStart:])
                else:
                    rt.extend(rs[nStart:nStart + nNum])
            self._DelCursor(cur)
            return rt
        else:
            rt = []
            cur = self._NewCursor()
            if not cur:
                return False
            self._conn.autocommit = True
            cur.execute(sql)
            try:
                rows = cur.fetchall()
            except:
                rows = None
                # this section will only return the last result from the query
                while cur.nextset():
                    try:
                        rows = cur.fetchall()
                    except Exception as e:
                        print("Skipping non rs message: {}".format(e))
                    continue
            ro = rows
            self._conn.autocommit = False
            if (nStart == 0) and (nNum == 1):
                rt.append(rows)
            else:
                rs = ro
                if nNum == -1:
                    rt.extend(rs[nStart:])
                else:
                    rt.extend(rs[nStart:nStart + nNum])
            self._DelCursor(cur)
            return rt
    # 更新
    def Exec(self, sql):
        rt = None
        cur = self._NewCursor()
        conn = self._conn
        if not cur:
            return rt
        if TsDBdriver.PermitedUpdateSql(self, sql) == False:
            return rt
        try:
            cur.execute(sql)
            conn.commit()
            # row = cur.rowcount
        except Exception as ex:
            ex_type, ex_val, ex_stack = sys.exc_info()
            return ex_val
        self._DelCursor(cur)
        # print('ok') 调试语句是否成功用的标记
        # print(cur.rowcount)
        if cur.rowcount > 0:
            return True
        elif cur.rowcount == 0 and ('update' in sql or 'insert' in sql):
            return False
        else:
            return True
    # 关闭游标
    def Exit(self):
        con = self._conn
        con.close()

    # 读取错误内容
    def ErrorMark(self, e):
        logging.info('**解析报错')
        if r'error 5(\xe6\x8b\x92\xe7\xbb\x9d\xe8\xae\xbf\xe9\x97\xae\xe3\x80\x82)' in e:
            return '错误5：拒绝访问'
        elif r'error 3(\xe7\xb3\xbb\xe7\xbb\x9f\xe6\x89\xbe\xe4\xb8\x8d\xe5\x88\xb0\xe6\x8c\x87\xe5\xae\x9a\xe7\x9a\x84\xe8\xb7\xaf\xe5\xbe\x84\xe3\x80\x82)' in e:
            return '错误3：系统找不到指定的路径'
        elif r'does not exist. Make sure that the name is entered correctly' in e:
            return '错误：备份的数据库不存在.请确认数据库名字是否填写错误'
        else:
            return e
    #功能1： 检查数据是否能连接
    def SQLcon(self):
        if self._dver == 'pymssql driver':
            try:
                con = pymssql.connect(host=self._hst, database=self._odb, user=self._unm,password=self._pwd, charset='utf8')
                return True
            except Exception as e:
                return False
        else:
            if self._unm == '' and self._pwd == '':
                try:
                    con = pyodbc.connect(f"Trusted_Connection=yes;driver={self._dver};server={self._hst}; database={self._odb}; autocommit=True;TrustServerCertificate=yes")
                    return True
                except Exception as e:
                    print(e)
                    return False
            else:
                try:
                    con = pyodbc.connect(f"driver={self._dver}; server={self._hst}; UID={self._unm};PWD={self._pwd}; database={self._odb}; autocommit=True;TrustServerCertificate=yes")
                    return True
                except Exception as e:
                    print(e)
                    return False
    # 功能2：查看是否存在某个数据库
    def ExistcheckDb(self, dbname):
        logging.info(f'**检测{dbname}是否存在数据列表中')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                con.autocommit(True)
                cur = con.cursor()
                sqlcheck = f"select * from sysdatabases where name = '{dbname}'"
                try:
                    cur.execute(sqlcheck)
                    rs = cur.fetchall()
                    con.autocommit(False)
                    cur.close()
                    if rs == []:
                        return False
                    else:
                        return True
                except Exception as e:
                    logging.error(f'**检测{dbname}是否存在数据列表中失败')
                    return (str(e))
                logging.info(f'**检测{dbname}是否存在数据列表中成功')
            else:
                logging.warning(f'**检测{dbname}是否存在数据列表过程中，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                cur = con.cursor()
                sqlcheck = f"select * from sysdatabases where name = '{dbname}'"
                try:
                    cur.execute(sqlcheck)
                    rs = cur.fetchall()
                    if rs == []:
                        return False
                    else:
                        return True
                except Exception as e:
                    logging.error(f'**检测{dbname}是否存在数据列表中失败')
                    return (str(e))
                logging.info(f'**检测{dbname}是否存在数据列表中成功')
            else:
                logging.warning(f'**检测{dbname}是否存在数据列表过程中，数据库连接中断')
                return 'Unconnect'
    #功能3： 检查是否重复
    def RepeatDB(self, dbname):
        logging.info(f'**检测数据库{dbname}是否重名')
        self._ReConnect()
        con = self._conn
        if self._dver =='pymssql driver':
            if con:
                rt = []
                sqlcheck = f"select * from sysdatabases where name = '{dbname}'"
                try:
                    cur = con.cursor()
                    con.autocommit(True)
                    cur.execute(sqlcheck)
                    rs = cur.fetchall()
                    con.autocommit(False)
                    cur.close()
                    rt.append(rs)
                    logging.info(f'**检测数据库{dbname}是否重名成功')
                except Exception as e:
                    logging.error(f'**检测数据库{dbname}是否重名失败，原因为:{e}')
                    return (str(e))
                logging.info(f'**检测数据库{dbname}是否重名结束')
                return rt
            else:
                logging.warning(f'**检测数据库{dbname}重名，途中连接中断')
                return 'Unconnect'
        else:
            if con:
                sqlcheck = f"select * from sysdatabases where name = '{dbname}'"
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sqlcheck)
                    rs = cur.fetchall()
                    con.autocommit = False
                    cur.close()
                    return rs
                    # logging.info(f'**检测数据库{dbname}是否重名成功')
                except Exception as e:
                    # logging.error(f'**检测数据库{dbname}是否重名失败，原因为:{e}')
                    return (str(e))
                    # logging.info(f'**检测数据库{dbname}是否重名结束')
            else:
                    # logging.warning(f'**检测数据库{dbname}重名，途中连接中断')
                return 'Unconnect'
    #功能4 加载全部的表名字
    def GetAlltb(self, dbname):
        logging.info(f'**获取数据库{dbname}所有的表名字')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                con.autocommit(True)
                cur = con.cursor()
                sql = f'''use [{dbname}]
                    select name from sys.objects  where type='U' order by name '''
                cur.execute(sql)
                rs = cur.fetchall()
                tb = tuple2list(rs)
                cur.close()
                logging.info(f'**获取数据库{dbname}所有的表名字成功')
                return tb
            else:
                logging.warning(f'**获取数据库{dbname}所有的表名字失败，数据库连接中断')
                return 'Unconnect'
        else:
            # 特别注意odbc不能随便用fetchall
            if con:
                cur = con.cursor()
                sql = f'''SET NOCOUNT ON;use [{dbname}];
                        select name from sys.objects  where type='U' order by name'''
                cur.execute(sql)
                rows = None
                # this section will only return the last result from the query
                while cur.nextset():
                    try:
                        rows = cur.fetchall()
                    except Exception as e:
                        print("Skipping non rs message: {}".format(e))
                    continue
                rs = rows
                tb = tuple2listodbc(rs)
                cur.close()
                logging.info(f'**获取数据库{dbname}所有的表名字成功')
                return tb
            else:
                logging.warning(f'**获取数据库{dbname}所有的表名字失败，数据库连接中断')
                return 'Unconnect'
    # 功能5 获取全部的数据库名字
    def DBlist(self,dbname):
        logging.info('**获取数据列表开始')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                sql = f'''SET NOCOUNT ON;
            use {dbname};
            select name from sysdatabases order by name
                '''
                con.autocommit(True)
                cur = con.cursor()
                cur.execute(sql)
                rt = cur.fetchall()
                dblist = tuple2list(rt)
                logging.info('**获取数据列表成功')
                return dblist
            else:
                logging.warning(f'**获取数据列表字失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'''SET NOCOUNT ON;
                use {dbname};
                select name from sys.databases order by name'''
                cur = con.cursor()
                cur.execute(sql)
                rows = None
                # this section will only return the last result from the query
                while cur.nextset():
                    try:
                        rows = cur.fetchall()
                    except Exception as e:
                        print("Skipping non rs message: {}".format(e))
                    continue
                rs = rows
                db = tuple2listodbc(rs)
                cur.close()
                logging.info(f'**获取数据列表成功')
                return db
            else:
                logging.warning(f'**获取数据列表失败，数据库连接中断')
                return 'Unconnect'
        # 备份数据库
    def BackupDB(self, dbname, backpath, newname):
        logging.info(f'**备份数据库{dbname}')
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                newfile = backpath + '\\' + newname
                newfile = os.path.abspath(newfile)
                # 备份数据库的脚本(with format是关键,是覆盖备份,如果有同名备份的话会被覆盖)
                sql = f"backup database {dbname} to disk='{newfile}' with format"
                # 校验备份目录是否合法以及存在
                dircheck = mkdir(backpath)
                if dircheck != 'Invalid FileName':
                    try:
                        cur = con.cursor()
                        con.autocommit(True)
                        cur.execute(sql)
                        con.autocommit(False)
                        cur.close()
                        logging.info(f'**备份数据库{dbname}成功')
                        return True
                    except Exception as e:
                        con.autocommit(False)
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'**备份数据库{dbname}失败，失败原因为{e}')
                        return res
                else:
                    logging.warning(f'**备份数据库{dbname}，备份路径非法')
                    return False
            else:
                logging.warning(f'**备份数据库{dbname}，备份路径非法')
                return 'Unconnect'
        else:
            if con:
                newfile = backpath + '\\' + newname
                newfile = os.path.abspath(newfile)
                # 备份数据库的脚本(with format是关键,是覆盖备份,如果有同名备份的话会被覆盖)
                sql = f"backup database {dbname} to disk = '{newfile}' with format"
                dircheck = mkdir(backpath)
                if dircheck != 'Invalid FileName':
                    try:
                        con.autocommit = True
                        cur = con.cursor()
                        cur.execute(sql)
                        con.commit()  # 记住 commit
                        time.sleep(5)
                        # row = cur.rowcount
                        logging.info(f'**备份数据库{dbname}成功')
                        return True
                    except Exception as ex:
                        ex_type, ex_val, ex_stack = sys.exc_info()
                        logging.error(f'**备份数据库{dbname}失败，失败原因为{ex_val}')
                        return False
                    self._DelCursor(cur)
                else:
                    logging.warning(f'**备份数据库{dbname}，备份路径非法')
                    return 'Unconnect'
            else:
                logging.warning(f'**备份数据库{dbname}，备份路径非法')
                return 'Unconnect'
    #功能5 备份数据库
    def BackupDBtest(self,dbname,backpath):
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            logging.info(f'**备份数据库{dbname}')
            if con:
                # 备份数据库的脚本(with format是关键,是覆盖备份,如果有同名备份的话会被覆盖)
                sql = f"backup database {dbname} to disk='{backpath}' with format"
                try:
                    cur = con.cursor()
                    con.autocommit(True)
                    cur.execute(sql)
                    con.autocommit(False)
                    cur.close()
                    logging.info(f'**备份数据库{dbname}成功')
                    return True
                except Exception as e:
                    con.autocommit(False)
                    cur.close()
                    logging.error(f'**备份数据库{dbname}失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**备份数据库{dbname}，备份路径非法')
                return 'Unconnect'
        else:
            sql = f"backup database {dbname} to disk = '{backpath}' with format"
            if con:
                try:
                    cur = con.cursor()
                    cur.execute(sql)
                    con.autocommit=True
                    con.commit()
                    time.sleep(3)
                    # row = cur.rowcount
                    logging.info(f'**备份数据库{dbname}成功')
                    return True
                except Exception as ex:
                    ex_type, ex_val, ex_stack = sys.exc_info()
                    logging.error(f'**备份数据库{dbname}失败，失败原因为{ex_val}')
                    return False
                self._DelCursor(cur)
            else:
                logging.warning(f'**备份数据库{dbname}，备份路径非法')
                return 'Unconnect'
    #功能6：还原数据库
    def RestoreDB(self, filename, dbname, oldlogiclist, newlogiclist):
        # logging.info(f'**还原数据库{dbname}')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                # 构建新的sql，通过修改文件位置保证物理文件不重复
                sql = f'''RESTORE DATABASE [{dbname}] FROM DISK = N'{filename}' WITH Replace,stats = 10
                       ,move '{oldlogiclist[0]}' to '{newlogiclist[0]}'
                       ,move '{oldlogiclist[1]}' to '{newlogiclist[1]}'
                       '''              # 检查同名数据库是否存在
                if self.RepeatDB(dbname) == [[]]:
                    try:
                        cur = con.cursor()
                        con.autocommit(True)
                        cur.execute(sql)
                        con.autocommit(False)
                        cur.close()
                        logging.info(f'**还原数据库{dbname}成功')
                        return True
                    except Exception as e:
                        con.autocommit(False)
                        cur.close()
                        res = str(e)
                        logging.error(f'**还原数据库{dbname}失败，失败原因为{e}')
                        raise Exception('恢复失败')
                else:
                    logging.warning(f'**还原数据库{dbname}失败，列表里有重名数据库')
                    return False
            else:
                logging.warning(f'**还原数据库{dbname}，途中数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                # 构建新的sql，通过修改文件位置保证物理文件不重复
                sql = f'''RESTORE DATABASE [{dbname}] FROM DISK = N'{filename}' WITH Recovery,Replace,stats = 10
                ,move '{oldlogiclist[0]}' to '{newlogiclist[0]}'
                ,move '{oldlogiclist[1]}' to '{newlogiclist[1]}'
                '''
                print(sql)
                # 检查同名数据库是否存在
                # print('repeat',self.RepeatDB(dbname))
                if self.RepeatDB(dbname) == [[]] or self.RepeatDB(dbname) == []:
                    try:
                        # 执行备份
                        cur = con.cursor()
                        con.autocommit = True
                        cur.execute(sql)
                        # 这一步很重要是还原语句执行后等待有返回结果操作，如果没有这一步，还原的数据库会一直显示状态为正在还原\
                        # (题外话：当时就是没有写这一步导致浪费了我一上午时间在测试这个一直显示数据库状态为正在还原中)
                        while cur.nextset():
                            pass
                        print("还原执行完成")
                        con.commit()  # 记住 commit
                        time.sleep(5)
                        cur.close()
                        logging.info(f'**还原数据库{dbname}成功')
                        con.autocommit = False
                        return True
                    except Exception as e:
                        con.autocommit = False
                        cur.close()
                        res = str(e)
                        logging.error(f'**还原数据库{dbname}失败，失败原因为{e}')
                        raise Exception('恢复失败')
                else:
                    logging.warning(f'**还原数据库{dbname}失败，列表里有重名数据库')
                    return False
            else:
                logging.warning(f'**还原数据库{dbname}，途中数据库连接中断')
                return 'Unconnect'
    #功能8：删除数据库
    def DeleteDB(self, dbname):
        logging.info(f'**删除数据库{dbname}')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                sqlonly = f'ALTER DATABASE [{dbname}] SET  SINGLE_USER WITH ROLLBACK IMMEDIATE'
                sql = f'''
                          USE master 
                          DROP DATABASE {dbname}
                           '''
                if self.RepeatDB(dbname) != [[]]:
                    try:
                        cur = con.cursor()
                        con.autocommit(True)
                        cur.execute(sqlonly)
                        time.sleep(3)
                        cur.execute(sql)
                        while cur.nextset():
                            pass
                        con.autocommit(False)
                        cur.close()
                        logging.info(f'**删除数据库{dbname}成功')
                        return True
                    except Exception as e:
                        con.autocommit(False)
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'**删除数据库{dbname}，失败原因为{e}')
                        return res
                else:
                    logging.warning(f'**删除数据库{dbname}结束，数据库列表中没有同名数据库')
                    return False
            else:
                logging.warning(f'**删除数据库{dbname}失败，数据库连接中断')
                return 'Unconnect'

        else:
            if con:
                sqlonly = f'ALTER DATABASE [{dbname}] SET  SINGLE_USER WITH ROLLBACK IMMEDIATE'
                sql = f'''
                      USE master 
                      DROP DATABASE {dbname}
                       '''
                if self.RepeatDB(dbname) == [[]] or self.RepeatDB(dbname) == []:
                    logging.warning(f'**删除数据库{dbname}结束，数据库列表中没有同名数据库')
                    return False
                else:
                    try:
                        cur = con.cursor()
                        con.autocommit = True
                        cur.execute(sqlonly)
                        time.sleep(3)
                        cur.execute(sql)
                        while cur.nextset():
                            pass
                        con.autocommit = False
                        cur.close()
                        logging.info(f'**删除数据库{dbname}成功')
                        return True
                    except Exception as e:
                        con.autocommit = False
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'**删除数据库{dbname}，失败原因为{e}')
                        return res
            else:
                logging.warning(f'**删除数据库{dbname}失败，数据库连接中断')
                return 'Unconnect'
    #功能9： 分离数据库
    def detachDB(self, dbname):
        logging.info(f'**分离{dbname}')
        self._ReConnect()
        con = self._conn
        if  self._dver == 'pymssql driver':
            if con:
                try:
                    con.autocommit(True)
                    cur = con.cursor()
                    sql = f'''
                    use master
                    exec sp_detach_db [{dbname}]
                    '''
                    cur.execute(sql)
                    cur.close()
                    logging.info(f'**分离{dbname}成功')
                    return True
                except Exception as e:
                    logging.error(f'**分离{dbname}失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**分离{dbname}失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                try:
                    cur = con.cursor()
                    sql = f'''
                    use master
                    exec sp_detach_db [{dbname}]
                    '''
                    con.autocommit = True
                    cur.execute(sql)
                    con.commit()
                    cur.close()
                    con.autocommit = False
                    logging.info(f'**分离{dbname}成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    logging.error(f'**分离{dbname}失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**分离{dbname}失败，数据库连接中断')
                return 'Unconnect'
    #功能10： 附加数据库(还是有文件权限问题）
    def AttachDB(self,dbname,oldlogfilelist):
        logging.info(f'**附加{dbname}')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                try:
                    con.autocommit(True)
                    cur = con.cursor()
                    sql = f'''CREATE DATABASE [{dbname}] ON 
                    ( FILENAME = N'{oldlogfilelist[0]}' ),
                    ( FILENAME = N'{oldlogfilelist[1]}' )
                    FOR ATTACH;
                           '''
                    cur.execute(sql)
                    RC = cur.rowcount
                    while cur.nextset():
                        pass
                    cur.close()
                    logging.info(f'**附加{dbname}成功')
                    return True
                except Exception as e:
                    # print(e)
                    logging.error(f'**附加{dbname}失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**附加{dbname}失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                try:
                    cur = con.cursor()
                    sql = f'''CREATE DATABASE [{dbname}] ON 
                    ( FILENAME = N'{oldlogfilelist[0]}' ),
                    ( FILENAME = N'{oldlogfilelist[1]}' )
                    FOR ATTACH;
                    '''
                    # print(sql)
                    con.autocommit = True
                    cur.execute(sql)
                    RC = cur.rowcount
                    while cur.nextset():
                        pass
                    cur.close()
                    con.autocommit = False
                    logging.info(f'**附加{dbname}成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    logging.error(f'**附加{dbname}失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**附加{dbname}失败，数据库连接中断')
                return 'Unconnect'
    #功能11：获取数据库列表里的物理文件位置
    def GetLogicallist(self, dbname):
        logging.info(f'**获取{dbname}的物理文件位置')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                con.autocommit(True)
                cur = con.cursor()
                # 核心点就在逻辑文件可能会出现和现有数据库重复的情况
                sql = f'''
                use master
                select ltrim(rtrim(filename)) from [{dbname}]..sysfiles where charindex('MDF',filename)>0  or charindex('LDF',filename)>0        
                '''
                try:
                    cur.execute(sql)
                    rt = cur.fetchall()
                    rs = [rt[0][0], rt[1][0]]
                    con.autocommit(False)
                    cur.close()
                    logging.info(f'**获取{dbname}的物理文件位置成功')
                    return rs
                except Exception as e:
                    logging.error(f'**获取{dbname}的物理文件位置失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取{dbname}的物理文件位置失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                con.autocommit = True
                cur = con.cursor()
                # 核心点就在逻辑文件可能会出现和现有数据库重复的情况
                sql = f'''
                use master
                select ltrim(rtrim(filename)) from [{dbname}]..sysfiles where charindex('MDF',filename)>0  or charindex('LDF',filename)>0        
                '''
                try:
                    cur.execute(sql)
                    rows = None
                    # this section will only return the last result from the query
                    while cur.nextset():
                        try:
                            rows = cur.fetchall()
                        except Exception as e:
                            print("Skipping non rs message: {}".format(e))
                        continue
                    rs = rows
                    rt = tuple2listodbc(rs)
                    rl = [rt[0], rt[1]]
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**获取{dbname}的物理文件位置成功')
                    return rl
                except Exception as e:
                    logging.error(f'**获取{dbname}的物理文件位置失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取{dbname}的物理文件位置失败，数据库连接中断')
                return 'Unconnect'
   # 获取数据库原始物理文件位置-通过bak格式的获取
    def LogicalData(self, dbname, dbpath):
        logging.info(f'**获取{dbpath}的{dbname}的数据逻辑文件位置')
        self._ReConnect()
        con = self._conn
        if self._dver =='pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                dbfile = dbpath + '\\' + dbname
                dbfile = os.path.abspath(dbfile)
                # 核心点就在逻辑文件可能会出现和现有数据库重复的情况
                sql = f"RESTORE FILELISTONLY from disk='{dbfile}'"
                try:
                    cur.execute(sql)
                    rt = cur.fetchall()
                    rs = [rt[0][0], rt[1][0]]
                    con.autocommit(False)
                    cur.close()
                    logging.info(f'**获取{dbpath}的{dbname}的数据逻辑文件位置成功')
                    return rs
                except Exception as e:
                    logging.error(f'**获取{dbpath}的{dbname}的数据逻辑文件位置失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取{dbpath}的{dbname}的数据逻辑文件位置失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                dbfile = dbpath + '\\' + dbname
                dbfile = os.path.abspath(dbfile)
                sql = f"RESTORE FILELISTONLY from disk='{dbfile}'"
                print(sql)
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql)
                    rt = cur.fetchall()
                    rs = [rt[0][0], rt[1][0]]
                    logging.info(f'**获取{dbpath}的{dbname}的数据逻辑文件位置成功')
                    cur.close()
                    con.autocommit = False
                    return rs
                except Exception as e:
                    logging.error(f'**获取{dbpath}的{dbname}的数据逻辑文件位置失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取{dbpath}的{dbname}的数据逻辑文件位置失败，数据库连接中断')
                return 'Unconnect'



    #功能12：获取bak中的physical名字
    def GetbakLogic(self, dbname, dbpath):
        logging.info(f'**获取{dbpath}的{dbname}的数据逻辑文件位置')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con:
                con.autocommit(True)
                cur = con.cursor()
                dbfile = dbpath + '\\' + dbname
                dbfile = os.path.abspath(dbfile)
                # 核心点就在逻辑文件可能会出现和现有数据库重复的情况
                sql = f"RESTORE FILELISTONLY from disk='{dbfile}'"
                try:
                    cur.execute(sql)
                    rt = cur.fetchall()
                    rs = [rt[0][0], rt[1][0]]
                    con.autocommit(False)
                    cur.close()
                    logging.info(f'**获取{dbpath}的{dbname}的数据物理名字成功')
                    return rs
                except Exception as e:
                    logging.error(f'**获取{dbpath}的{dbname}的数据物理名字失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取{dbpath}的{dbname}的数据物理名字失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                con.autocommit = True
                cur = con.cursor()
                # 核心点就在逻辑文件可能会出现和现有数据库重复的情况
                dbfile = dbpath + '\\' + dbname
                dbfile = os.path.abspath(dbfile)
                sql = f"RESTORE FILELISTONLY from disk='{dbfile}'"
                try:
                    cur.execute(sql)
                    rows = None
                    rows = cur.fetchall()
                    rs = rows
                    rt = tuple2listodbc(rs)
                    rl = [rt[0], rt[1]]
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**获取{dbname}的物理名字位置成功')
                    return rl
                except Exception as e:
                    logging.error(f'**获取{dbname}的物理名字位置失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取{dbpath}的{dbname}的数据物理名字失败，数据库连接中断')
                return 'Unconnect'
    #功能13：检测数据库损坏
    def DBCC(self,dbname):
        rt = []
        cur = self._NewCursor()
        conn = self._conn
        if self._dver == 'pymssql driver':
            if not cur:
                return '无法访问数据库'
            else:
                try:
                    cur.execute(f"SET NOCOUNT ON;dbcc checkdb('{dbname}')")
                    conn.commit()
                except Exception as ex:
                    ex_type, ex_val, ex_stack = sys.exc_info()
                    return False
                return True
        else:
            if not cur:
                return '无法访问数据库'
            else:
                try:
                    cur.execute(f"SET NOCOUNT ON;dbcc checkdb('{dbname}')")
                    conn.commit()
                except Exception as ex:
                    ex_type, ex_val, ex_stack = sys.exc_info()
                    return False
                return True
    '''
    导表功能重写
    '''
    # 读取版本号
    def VersionDB(self, Db):
        logging.info(f'**读取{Db}补丁版本号')
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                try:
                    con.autocommit(True)
                    cur = con.cursor()
                    sql = f'''use [{Db}]
                           if exists(select name from sys.objects  where type='U' and name = 'eap_accinformation1')
        select Value from eap_accinformation where caption like '版本号' and name = 'VersionNo'  
    else if exists(select name from sys.objects  where type='U' and name = 'eap_accinformation')
        if
         (select right(max(version),15) from SM_Upgrade  where itemtype = 'DLL' and status = '1') > (select max(version) from SM_Upgrade where ItemType = 'SQL' and status = '1')
         select right(max(version),15) from SM_Upgrade  where itemtype = 'DLL'
        else
          select max(version) from SM_Upgrade where ItemType = 'SQL'
                            '''
                    cur.execute(sql)
                    RS = cur.fetchall()
                    rs = tuple2list(RS)[0]
                    logging.info(f'**读取{Db}补丁版本号成功')
                    return rs
                except Exception as e:
                    logging.error(f'**读取{Db}补丁版本号，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**读取{Db}补丁版本号失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                try:
                    sql = f'''use [{Db}]
                               if exists(select name from sys.objects  where type='U' and name = 'eap_accinformation1')
            select Value from eap_accinformation where caption like '版本号' and name = 'VersionNo'  
        else if exists(select name from sys.objects  where type='U' and name = 'eap_accinformation')
            if
             (select right(max(version),15) from SM_Upgrade  where itemtype = 'DLL' and status = '1') > (select max(version) from SM_Upgrade where ItemType = 'SQL' and status = '1')
             select right(max(version),15) from SM_Upgrade  where itemtype = 'DLL'
            else
              select max(version) from SM_Upgrade where ItemType = 'SQL'
                                '''
                    cur = con.cursor()
                    cur.execute(sql)
                    rows = None
                    # this section will only return the last result from the query
                    while cur.nextset():
                        try:
                            rows = cur.fetchall()
                        except Exception as e:
                            print("Skipping non rs message: {}".format(e))
                        continue
                    rs = rows
                    db = tuple2listodbc(rs)
                    cur.close()
                    logging.info(f'**读取{Db}补丁版本号成功')
                    return db
                except Exception as e:
                    logging.error(f'**读取{Db}补丁版本号，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**读取{Db}补丁版本号失败，数据库连接中断')
                return 'Unconnect'
 # 清除Eap表
    def ClearBKtb(self,OriDB):
        logging.info(f'**清除{OriDB}的Eap表')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'''use [{OriDB}]
                    if exists (select * from sys.objects where object_id = object_id(N'[EAP_CJT_DefaultValue]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                    drop table [EAP_CJT_DefaultValue] 
                    if exists (select * from sys.objects where object_id = object_id(N'[EAP_CJT_ALLCONSTRAINT]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                    drop table [EAP_CJT_ALLCONSTRAINT] 
                    if exists (select * from sys.objects where object_id = object_id(N'[EAP_CJT_allindexs]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                    drop table [EAP_CJT_allindexs] 
                    if exists (select * from sys.objects where object_id = object_id(N'[checkdate]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                    drop table [checkdate]'''
                    cur.execute(sql)
                    RC = cur.rowcount
                    logging.info(f'**清除{OriDB}的Eap表成功')
                except Exception as e:
                    logging.info(f'**清除{OriDB}的Eap表失败，原因为{e}')
                    res = self.ErrorMark(str(e))
                    return res
            else:
                logging.warning(f'**清除{OriDB}的Eap表失败')
                return 'Unconnect'
        else:
            if con:
                sql = f'''use [{OriDB}]
                               if exists (select * from sys.objects where object_id = object_id(N'[EAP_CJT_DefaultValue]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                               drop table [EAP_CJT_DefaultValue] 
                               if exists (select * from sys.objects where object_id = object_id(N'[EAP_CJT_ALLCONSTRAINT]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                               drop table [EAP_CJT_ALLCONSTRAINT] 
                               if exists (select * from sys.objects where object_id = object_id(N'[EAP_CJT_allindexs]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                               drop table [EAP_CJT_allindexs] 
                               if exists (select * from sys.objects where object_id = object_id(N'[checkdate]') and OBJECTPROPERTY(object_id, N'IsUserTable') = 1) 
                               drop table [checkdate]'''
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql)
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**清除{OriDB}的Eap表成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'**清除{OriDB}的Eap表失败，失败原因为{e}')
                    return res
            else:
                logging.warning(f'**清除{OriDB}的Eap表失败')
                return 'Unconnect'
# EapMenu表补充ID字段
    def EapIDadd(self,brkDB):
        logging.info(f'**{brkDB}的EapMenu表补充ID字段')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'''use [{brkDB}]
                    if not exists(select * from sys.columns where object_id=object_id('Eap_MenuDefaultOption') and name='ID')   
                    Alter table Eap_MenuDefaultOption add [ID] [int] IDENTITY(1,1) NOT NULL'''
                    cur.execute(sql)
                    RC = cur.rowcount
                    logging.info(f'**{brkDB}的EapMenu表补充ID字段成功')
                    return True
                except Exception as e:
                    logging.error(f'**{brkDB}的EapMenu表补充ID字段失败，原因为:{e}')
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    # logging.error(f'**删除数据库{dbname}，失败原因为{e}')
                    return res
                    logging.info(f'**{brkDB}的EapMenu表补充ID字段结束')
            else:
                logging.warning(f'**{brkDB}的EapMenu表补充ID字段失败')
                return 'Unconnect'
        else:
            if con:
                sql = f'''use [{brkDB}]
                                if not exists(select * from sys.columns where object_id=object_id('Eap_MenuDefaultOption') and name='ID')   
                                Alter table Eap_MenuDefaultOption add [ID] [int] IDENTITY(1,1) NOT NULL'''
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql)
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**{brkDB}的EapMenu表补充ID字段成功')
                    return True
                except Exception as e:
                    logging.error(f'**{brkDB}的EapMenu表补充ID字段失败，原因为:{e}')
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    # logging.error(f'**删除数据库{dbname}，失败原因为{e}')
                    return res
                    logging.info(f'**{brkDB}的EapMenu表补充ID字段结束')
            else:
                logging.info(f'**{brkDB}的EapMenu表补充ID字段失败,途中连接中断')
                return 'Unconnect'
# 将离线状态改成在线
    def setOnline(self, brkdb):
        logging.info(f'**将{brkdb}从离线状态改成在线')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'''use master
                    ALTER DATABASE [{brkdb}] SET online WITH ROLLBACK AFTER 0'''
                    cur.execute(sql)
                    RC = cur.rowcount
                    logging.info(f'**将{brkdb}从离线状态改成在线成功')
                    return True
                except Exception as e:
                    logging.error(f'**将{brkdb}从离线状态改成在线失败，原因为:{e}')
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    # logging.error(f'**删除数据库{dbname}，失败原因为{e}')
                    return res
                    logging.info(f'**将{brkdb}从离线状态改成在线结束')
            else:
                logging.warning(f'**将{brkdb}从离线状态改成在线失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'''use master
                ALTER DATABASE [{brkdb}] SET online WITH ROLLBACK AFTER 0'''
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql)
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**将{brkdb}从离线状态改成在线成功')
                    return True
                except Exception as e:
                    logging.error(f'**将{brkdb}从离线状态改成在线失败，原因为:{e}')
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    # logging.error(f'**删除数据库{dbname}，失败原因为{e}')
                    return res
                    logging.info(f'**将{brkdb}从离线状态改成在线结束')
            else:
                logging.info(f'**将{brkdb}从离线状态改成在线失败,途中连接中断')
                return 'Unconnect'
# 获取所有需要的表名字
    def Checktb(self,brkdb):
        logging.info(f'**获取数据库{brkdb}所有的表名字')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'''use [{brkdb}]
                        select name from sys.objects  where type='U' and name not like 'temp_0%' and name not in ('EAP_CJT_ALLCONSTRAINT','EAP_CJT_DefaultValue','EAP_CJT_allindexs','checkdate') order by name '''
                    cur.execute(sql)
                    rs = cur.fetchall()
                    tb = tuple2list(rs)
                    logging.info(f'**获取数据库{brkdb}所有的表名字成功')
                    return tb
                except Exception as e:
                    logging.error(f'**获取数据库{brkdb}所有的表名字失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取数据库{brkdb}所有的表名字失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'''use [{brkdb}]
                select name from sys.objects  where type='U' and name not like 'temp_0%' and name not in ('EAP_CJT_ALLCONSTRAINT','EAP_CJT_DefaultValue','EAP_CJT_allindexs','checkdate') order by name '''
                con.autocommit = True
                cur = con.cursor()
                try:
                    cur.execute(sql)
                    rows = None
                    # this section will only return the last result from the query
                    while cur.nextset():
                        try:
                            rows = cur.fetchall()
                        except Exception as e:
                            print("Skipping non rs message: {}".format(e))
                        continue
                    rs = rows
                    rt = tuple2listodbc(rs)
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**获取数据库{brkdb}所有的表名字成功')
                    return rt
                except Exception as e:
                    logging.error(f'**获取数据库{brkdb}所有的表名字失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取数据库{brkdb}所有的表名字失败，数据库连接中断')
                return 'Unconnect'
# 生成testdb中转检测坏表
    def TestDb(self):
        logging.info('**生成临时检测坏表的testdb数据库')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            path0 = os.getcwd()
            path = repath(path0)
            testdbmdf = path +'\\temp\\testdb\\'+'testdb.mdf'
            testdbldf = path +'\\temp\\testdb\\'+'testdb_log.ldf'
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'''use master
                            if exists(select * from sysdatabases where name = 'testDB')
                            begin
                            drop database testDB
                            end
                            CREATE DATABASE testDB ON
                            ( NAME = 'testDB',
                            FILENAME = '{testdbmdf}',--指定数据库的物理文件位置（后缀名为：.mdf）
                            SIZE = 5,
                            FILEGROWTH = 10%
                            )
                            LOG ON
                            (
                                NAME = 'testDB_log',
                                FILENAME = '{testdbldf}',--指定数据库日志的物理文件位置（后缀名为：.ldf）
                                SIZE = 5,
                                FILEGROWTH = 10%
                            )
                            '''
                    cur.execute(sql)
                    RC = cur.rowcount
                    logging.info('**生成临时检测坏表的testdb数据库成功')
                    return RC
                except Exception as e:
                    logging.error(f'**生成临时检测坏表的testdb数据库失败，失败原因为{e}')
                    return False
            else:
                logging.warning('**生成临时检测坏表的testdb数据库失败，数据库连接中断')
                return 'Unconnect'
        else:
            path0 = os.getcwd()
            path = repath(path0)
            testdbmdf = path + '\\temp\\testdb\\' + 'testdb.mdf'
            testdbldf = path + '\\temp\\testdb\\' + 'testdb_log.ldf'
            if con:
                try:
                    cur = con.cursor()
                    sql =f'''use master
                            if exists(select * from sysdatabases where name = 'testDB')
                            begin
                            drop database testDB
                            end
                            CREATE DATABASE testDB ON
                            ( NAME = 'testDB',
                            FILENAME = '{testdbmdf}',--指定数据库的物理文件位置（后缀名为：.mdf）
                            SIZE = 5,
                            FILEGROWTH = 10%
                            )
                            LOG ON
                            (
                                NAME = 'testDB_log',
                                FILENAME = '{testdbldf}',--指定数据库日志的物理文件位置（后缀名为：.ldf）
                                SIZE = 5,
                                FILEGROWTH = 10%
                            )
                            '''
                    # print(sql)
                    con.autocommit = True
                    cur.execute(sql)
                    RC = cur.rowcount
                    while cur.nextset():
                        pass
                    cur.close()
                    con.autocommit = False
                    logging.info(f'**生成临时检测坏表的testdb数据库成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    logging.error(f'**生成临时检测坏表的testdb数据库失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**生成临时检测坏表的testdb数据库失败，数据库连接中断')
                return 'Unconnect'
# 生成查询坏表的语句
    def QuerySQL(self,brkdb,Lst):
        logging.info(f'**生成检测{brkdb}坏表的语句')
        sqllist = []
        for tb in Lst:
            sql = f'select  * into [{tb}] from [{brkdb}]..[{tb}]'
            sqllist.append(sql)
        logging.info(f'**生成检测{brkdb}坏表的语句成功')
        return sqllist
 # 获取坏表
    def ErrorTB(self,Lst):
        logging.info('**获取坏表')
        Errlist = []
        if self._dver == 'pymssql driver':
            for sql in Lst:
                try:
                    con = pymssql.connect(host=self._hst, database=self._odb, user=self._unm,password=self._pwd, charset='utf8')
                    con.autocommit(True)
                    cur = con.cursor()
                    sql1 = 'use testDB\n' + sql
                    print(sql1)
                    cur.execute(sql1)
                    cur.close()
                    print('查询结束')
                except Exception as e:
                    cur.close()
                    tbName0 = sql.split('..')
                    tbName1 = tbName0[-1]
                    tbName = tbName1[1:-1]
                    Errlist.append(tbName)
                    print(tbName)
            logging.warning(f'**损坏的表有：{Errlist}')
            return Errlist
        else:
            if self._unm == '' and self._pwd == '':
                for sql in Lst:
                    try:
                        con = pyodbc.connect( f"Trusted_Connection=yes;driver={self._dver};server={self._hst}; database={self._odb}; autocommit=True;TrustServerCertificate=yes")
                        con.autocommit = True
                        cur = con.cursor()
                        sql1 = 'use testDB\n' + sql
                        print(sql1)
                        cur.execute(sql1)
                        # cur.fetchall()
                        while cur.nextset():
                            pass
                        cur.close()
                        con.autocommit = False
                        print('nnn')
                    except Exception as e:
                        try:
                            con.autocommit = False
                            cur.close()
                            tbName0 = sql.split('..')
                            tbName1 = tbName0[-1]
                            tbName = tbName1[1:-1]
                            Errlist.append(tbName)
                            print(tbName, e)
                        except Exception as e:
                            print(3)
                            self.__del__()
                            self._ReConnect()
                            tbName0 = sql.split('..')
                            tbName1 = tbName0[-1]
                            tbName = tbName1[1:-1]
                            Errlist.append(tbName)
                            print(tbName, e)
                logging.warning(f'**损坏的表有：{Errlist}')
                return Errlist
            else:
                for sql in Lst:
                    try:
                        con = pyodbc.connect(f"driver={self._dver}; server={self._hst}; UID={self._unm};PWD={self._pwd}; database={self._odb}; autocommit=True;TrustServerCertificate=yes")
                        print(2)
                        con.autocommit = True
                        cur = con.cursor()
                        sql1 = 'use testDB\n' + sql
                        print(sql1)
                        cur.execute(sql1)
                        # cur.fetchall()
                        while cur.nextset():
                            pass
                        cur.close()
                        con.autocommit = False
                        print('nnn')
                    except Exception as e:
                        try:
                            con.autocommit =False
                            cur.close()
                            tbName0 = sql.split('..')
                            tbName1 = tbName0[-1]
                            tbName = tbName1[1:-1]
                            Errlist.append(tbName)
                            print(tbName, e)
                        except Exception as e:
                            print(3)
                            self.__del__()
                            self._ReConnect()
                            tbName0 = sql.split('..')
                            tbName1 = tbName0[-1]
                            tbName = tbName1[1:-1]
                            Errlist.append(tbName)
                            print(tbName,e)
                logging.warning(f'**损坏的表有：{Errlist}')
                return Errlist
 # 清除testdb表
    def DelDB(self):
        logging.info('**清除检测临时表testdb')
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'''USE MASTER  
                            if exists(select * from sysdatabases where name = 'testDB')
                            DECLARE @dbname SYSNAME    
                            SET @dbname = 'testDB'
                            DECLARE @s NVARCHAR(1000)    
                            DECLARE tb CURSOR LOCAL   
                            FOR  
                            SELECT s = 'kill   ' + CAST(spid AS VARCHAR)  
                            FROM   MASTER..sysprocesses  
                            WHERE  dbid = DB_ID(@dbname)    
                            OPEN   tb      
                            FETCH   NEXT   FROM   tb   INTO   @s    
                            WHILE @@fetch_status = 0  
                            BEGIN  
                            EXEC (@s)   
                            FETCH NEXT FROM tb INTO @s  
                            END    
                            CLOSE   tb    
                            DEALLOCATE   tb    
                            EXEC ('drop   database   [' + @dbname + ']')    
                            '''
                    cur.execute(sql)
                    RC = cur.rowcount
                    logging.info('**清除检测临时表testdb成功')
                    return RC
                except Exception as e:
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'**清除检测临时表testdb失败，失败原因为{e}')
                    return res
            else:
                logging.warning('**清除检测临时表testdb失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'''USE MASTER  
                                       if exists(select * from sysdatabases where name = 'testDB')
                                       DECLARE @dbname SYSNAME    
                                       SET @dbname = 'testDB'
                                       DECLARE @s NVARCHAR(1000)    
                                       DECLARE tb CURSOR LOCAL   
                                       FOR  
                                       SELECT s = 'kill   ' + CAST(spid AS VARCHAR)  
                                       FROM   MASTER..sysprocesses  
                                       WHERE  dbid = DB_ID(@dbname)    
                                       OPEN   tb      
                                       FETCH   NEXT   FROM   tb   INTO   @s    
                                       WHILE @@fetch_status = 0  
                                       BEGIN  
                                       EXEC (@s)   
                                       FETCH NEXT FROM tb INTO @s  
                                       END    
                                       CLOSE   tb    
                                       DEALLOCATE   tb    
                                       EXEC ('drop   database   [' + @dbname + ']')    
                                       '''
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql)
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**清除检测临时表testdb成功')
                    return True
                except Exception as e:
                    try:
                        con.autocommit = False
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'**清除检测临时表testdb失败，失败原因为{e}')
                        return res
                    except Exception as e:
                        self.__del__()
                        self._ReConnect()
                        res = self.ErrorMark(str(e))
                        logging.error(f'**清除检测临时表testdb失败--重置testdb状态，失败原因为{e}')
                        return res

            else:
                logging.warning(f'**清除检测临时表testdb失败，数据库连接中断')
                return 'Unconnect'
# 生成表保留默认约束
    def DefauConsave(self,oridb):
        logging.info(f'**保留{oridb}默认约束')
        self._ReConnect()
        con = self._conn
        print('con',con)
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'use [{oridb}]'
                    sql0 = '''
                         if exists(select 1 from sysobjects where id=OBJECT_ID('EAP_CJT_DefaultValue'))
                         begin drop table EAP_CJT_DefaultValue end
                         SELECT ' alter table '+ SO.NAME+ ' add default '+ SM.[TEXT] + ' for ['+ sc.name+']' as Defaultsql, 
                          T.name, SO.NAME AS "TableName",SC.NAME AS "ColumnName",SM.[TEXT] AS "DefaultValue"
                          into EAP_CJT_DefaultValue FROM dbo.sysobjects SO
                          INNER JOIN dbo.syscolumns SC ON SO.id = SC.id
                           INNER JOIN systypes T ON SC.xusertype = T.xusertype
                           LEFT JOIN dbo.syscomments SM ON SC.cdefault = SM.id
                           WHERE SO.xtype = 'U' and SM.[TEXT] is not null
                           ORDER BY SO.[name],SC.colid      
                         '''
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    RC = cur.rowcount
                    logging.info(f'**保留{oridb}默认约束成功')
                    return RC
                except Exception as e:
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****保留{oridb}默认约束失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**保留{oridb}默认约束失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'use [{oridb}]'
                sql0 = '''
                                     if exists(select 1 from sysobjects where id=OBJECT_ID('EAP_CJT_DefaultValue'))
                                     begin drop table EAP_CJT_DefaultValue end
                                     SELECT ' alter table '+ SO.NAME+ ' add default '+ SM.[TEXT] + ' for ['+ sc.name+']' as Defaultsql, 
                                      T.name, SO.NAME AS "TableName",SC.NAME AS "ColumnName",SM.[TEXT] AS "DefaultValue"
                                      into EAP_CJT_DefaultValue FROM dbo.sysobjects SO
                                      INNER JOIN dbo.syscolumns SC ON SO.id = SC.id
                                       INNER JOIN systypes T ON SC.xusertype = T.xusertype
                                       LEFT JOIN dbo.syscomments SM ON SC.cdefault = SM.id
                                       WHERE SO.xtype = 'U' and SM.[TEXT] is not null
                                       ORDER BY SO.[name],SC.colid      
                                     '''
                sql1 = sql + '\n' + sql0
                try:
                    print('开始')
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql1)
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    cur.close()
                    logging.info(f'****保留{oridb}默认约束成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****保留{oridb}默认约束失败，失败原因为{e}')
                    return False
            else:
                print('结束')
                logging.warning(f'****保留{oridb}默认约束失败，数据库连接中断')
                return 'Unconnect'
    # --保存约束信息
    def Consave(self, oridb):
        logging.info(f'**保留{oridb}约束信息')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'use [{oridb}]'
                    sql0 = '''
                             if exists(select 1 from sysobjects where id=OBJECT_ID('EAP_CJT_ALLCONSTRAINT'))
                             begin drop table EAP_CJT_ALLCONSTRAINT end
        
                             select * into EAP_CJT_ALLCONSTRAINT  from (
                             SELECT 'ALTER TABLE '+OBJECT_NAME(sf.fkeyid)+' DROP CONSTRAINT '+OBJECT_NAME(con.constid) as DropFKSQL ,
                                         'ALTER TABLE '+OBJECT_NAME(sf.fkeyid)+' ADD CONSTRAINT ' +OBJECT_NAME(con.constid)+' FOREIGN KEY('+fcol.name+') REFERENCES '+ OBJECT_NAME(sf.rkeyid)+'('+rcol.name+')'  as AddFKSQL
                                          FROM sysforeignkeys sf
                                            INNER JOIN sysconstraints con ON sf.constid = con.constid
                                            INNER JOIN sys.syscolumns fcol ON fcol.id = sf.fkeyid AND fcol.colid = sf.fkey
                                            INNER JOIN sys.syscolumns rcol ON rcol.id = sf.rkeyid AND rcol.colid = sf.rkey
                                    ) a    
                             '''
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    RC = cur.rowcount
                    logging.info(f'**保留{oridb}约束信息成功')
                    return RC
                except Exception as e:
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****保留{oridb}约束信息失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**保留{oridb}约束信息失败，连接中断')
                return 'Unconnect'
        else:
            print('读取')
            if con:
                print('读取进入')
                sql = f'use [{oridb}]'
                sql0 = '''
                                           if exists(select 1 from sysobjects where id=OBJECT_ID('EAP_CJT_ALLCONSTRAINT'))
                                           begin drop table EAP_CJT_ALLCONSTRAINT end

                                           select * into EAP_CJT_ALLCONSTRAINT  from (
                                           SELECT 'ALTER TABLE '+OBJECT_NAME(sf.fkeyid)+' DROP CONSTRAINT '+OBJECT_NAME(con.constid) as DropFKSQL ,
                                                       'ALTER TABLE '+OBJECT_NAME(sf.fkeyid)+' ADD CONSTRAINT ' +OBJECT_NAME(con.constid)+' FOREIGN KEY('+fcol.name+') REFERENCES '+ OBJECT_NAME(sf.rkeyid)+'('+rcol.name+')'  as AddFKSQL
                                                        FROM sysforeignkeys sf
                                                          INNER JOIN sysconstraints con ON sf.constid = con.constid
                                                          INNER JOIN sys.syscolumns fcol ON fcol.id = sf.fkeyid AND fcol.colid = sf.fkey
                                                          INNER JOIN sys.syscolumns rcol ON rcol.id = sf.rkeyid AND rcol.colid = sf.rkey
                                                  ) a    
                                           '''
                sql1 = sql + '\n' + sql0
                try:
                    print('判断0')
                    cur = con.cursor()
                    con.autocommit = True
                    print('判断1')
                    cur.execute(sql1)
                    print('判断2')
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    print('判断3')
                    cur.close()
                    print('判断4')
                    logging.info(f'****保留{oridb}约束信息成功')
                    return True
                except Exception as e:
                    print(e)
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****保留{oridb}约束信息失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'****保留{oridb}约束信息失败，数据库连接中断')
                return 'Unconnect'
    # 保存默认索引
    def IndexSave(self, oridb):
        logging.info(f'**保留{oridb}默认索引')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'use [{oridb}]'
                    sql0 = '''
                              if exists(select 1 from sysobjects where id=OBJECT_ID('EAP_CJT_allindexs'))
                             begin drop table EAP_CJT_allindexs end;
                             WITH tx AS
                                       (
                                          SELECT a.object_id
                             ,b.name AS schema_name
        
                             ,a.name AS table_name
                             ,c.name as ix_name
                             ,c.is_unique AS ix_unique
                             ,c.type_desc AS ix_type_desc
                             ,d.index_column_id
                             ,d.is_included_column
                             ,e.name AS column_name
                             ,f.name AS fg_name
                             ,d.is_descending_key AS is_descending_key
                             ,c.is_primary_key
                             ,c.is_unique_constraint
                                          FROM sys.tables AS a
                                              INNER JOIN sys.schemas AS b            ON a.schema_id = b.schema_id AND a.is_ms_shipped = 0
                                              INNER JOIN sys.indexes AS c            ON a.object_id = c.object_id
                                              INNER JOIN sys.index_columns AS d      ON d.object_id = c.object_id AND d.index_id = c.index_id
                                              INNER JOIN sys.columns AS e            ON e.object_id = d.object_id AND e.column_id = d.column_id
                                              INNER JOIN sys.data_spaces AS f        ON f.data_space_id = c.data_space_id
                                       )
                                       SELECT id = IDENTITY(int,1,1),
                             Drop_Index   = CASE WHEN (a.is_primary_key = 1 OR a.is_unique_constraint = 1)
        
                                              THEN ' if exists( SELECT 1 from  sysindexes where ID=OBJECT_ID( '+a.table_name+')  and name='+a.ix_name+' ) begin  ALTER TABLE ' + a.table_name + ' DROP CONSTRAINT ' + a.ix_name +' end '
                                              ELSE ' if  exists(select  1  from  sysindexes  where ID=OBJECT_ID( '+a.table_name+') and  name='+a.ix_name collate SQL_Latin1_General_CP1_CI_AS +') begin  DROP INDEX [' + a.ix_name collate SQL_Latin1_General_CP1_CI_AS + '] ON ' + a.schema_name + '.' + a.table_name +' end '  END
                             ,Create_Index = CASE WHEN (a.is_primary_key = 1 OR a.is_unique_constraint = 1)
                                              THEN 'ALTER TABLE ' + a.table_name + ' ADD CONSTRAINT ' + a.ix_name
                                                  + CASE WHEN a.is_primary_key = 1 THEN ' PRIMARY KEY '+ix_type_desc+' ' ELSE ' UNIQUE' END + '(' + indexColumns.ix_index_column_name + ')'
                                              ELSE 'CREATE ' + CASE WHEN a.ix_unique = 1 THEN 'UNIQUE ' ELSE '' END 
                                                  + a.ix_type_desc + ' INDEX [' + a.ix_name collate SQL_Latin1_General_CP1_CI_AS + '] ON ' + a.schema_name
                                                  + '.' + a.table_name + '(' + indexColumns.ix_index_column_name + ')'
                                                  + CASE WHEN IncludeIndex.ix_included_column_name IS NOT NULL THEN ' INCLUDE (' + IncludeIndex.ix_included_column_name + ')' ELSE '' END
                                                  + ' ON [' + a.fg_name +']' END
                             ,CASE WHEN a.ix_unique = 1 THEN 'UNIQUE' END AS ix_unique
                             ,a.ix_type_desc
                             ,a.ix_name
                             ,a.schema_name
                             ,a.table_name
                             ,indexColumns.ix_index_column_name
                             ,IncludeIndex.ix_included_column_name
                             ,a.fg_name
                             ,a.is_primary_key
                             ,a.is_unique_constraint
                             into EAP_CJT_allindexs
                                       FROM
                                       (
                                              SELECT DISTINCT
                             ix_unique
                             ,ix_type_desc
                             ,ix_name
                             ,schema_name
                             ,table_name
                             ,fg_name
                             ,is_primary_key
                             ,is_unique_constraint
                                              FROM tx
                                       ) AS a
                                       OUTER APPLY
                                       (
        
                                          SELECT ix_index_column_name
                                              = STUFF((
                                              SELECT ',' + column_name + CASE WHEN is_descending_key = 1 THEN ' DESC' ELSE '' END
                                                FROM tx AS b
                                              WHERE schema_name = a.schema_name
                                                  AND table_name=a.table_name
                                                  AND ix_name=a.ix_name
        
                                                  AND ix_type_desc=a.ix_type_desc
                                                  AND fg_name=a.fg_name
                                                  AND is_included_column=0
                                              ORDER BY index_column_id
                                                  FOR XML PATH('')
                                              ),1,1,'')
                             )IndexColumns
                                       OUTER APPLY
                                       (
                                              SELECT ix_included_column_name
                                                   = STUFF((
                                                       SELECT ',' + column_name
                                                        FROM tx AS b
                                                      WHERE schema_name = a.schema_name
                                                        AND table_name=a.table_name
                                                        AND ix_name=a.ix_name
                                                        AND ix_type_desc=a.ix_type_desc
                                                        AND fg_name=a.fg_name
                                                        AND is_included_column=1
                                                      ORDER BY index_column_id
                                                        FOR XML PATH('')
                                                      ), 1,1,'')
                             )IncludeIndex
                                       ORDER BY a.schema_name,a.table_name,a.ix_name; 
                             '''
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    RC = cur.rowcount
                    logging.info(f'**保留{oridb}默认索引成功')
                    return RC
                except Exception as e:
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****保留{oridb}默认索引失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**保留{oridb}默认索引失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'use [{oridb}]'
                sql0 = '''
                                          if exists(select 1 from sysobjects where id=OBJECT_ID('EAP_CJT_allindexs'))
                                         begin drop table EAP_CJT_allindexs end;
                                         WITH tx AS
                                                   (
                                                      SELECT a.object_id
                                         ,b.name AS schema_name

                                         ,a.name AS table_name
                                         ,c.name as ix_name
                                         ,c.is_unique AS ix_unique
                                         ,c.type_desc AS ix_type_desc
                                         ,d.index_column_id
                                         ,d.is_included_column
                                         ,e.name AS column_name
                                         ,f.name AS fg_name
                                         ,d.is_descending_key AS is_descending_key
                                         ,c.is_primary_key
                                         ,c.is_unique_constraint
                                                      FROM sys.tables AS a
                                                          INNER JOIN sys.schemas AS b            ON a.schema_id = b.schema_id AND a.is_ms_shipped = 0
                                                          INNER JOIN sys.indexes AS c            ON a.object_id = c.object_id
                                                          INNER JOIN sys.index_columns AS d      ON d.object_id = c.object_id AND d.index_id = c.index_id
                                                          INNER JOIN sys.columns AS e            ON e.object_id = d.object_id AND e.column_id = d.column_id
                                                          INNER JOIN sys.data_spaces AS f        ON f.data_space_id = c.data_space_id
                                                   )
                                                   SELECT id = IDENTITY(int,1,1),
                                         Drop_Index   = CASE WHEN (a.is_primary_key = 1 OR a.is_unique_constraint = 1)

                                                          THEN ' if exists( SELECT 1 from  sysindexes where ID=OBJECT_ID( '+a.table_name+')  and name='+a.ix_name+' ) begin  ALTER TABLE ' + a.table_name + ' DROP CONSTRAINT ' + a.ix_name +' end '
                                                          ELSE ' if  exists(select  1  from  sysindexes  where ID=OBJECT_ID( '+a.table_name+') and  name='+a.ix_name collate SQL_Latin1_General_CP1_CI_AS +') begin  DROP INDEX [' + a.ix_name collate SQL_Latin1_General_CP1_CI_AS + '] ON ' + a.schema_name + '.' + a.table_name +' end '  END
                                         ,Create_Index = CASE WHEN (a.is_primary_key = 1 OR a.is_unique_constraint = 1)
                                                          THEN 'ALTER TABLE ' + a.table_name + ' ADD CONSTRAINT ' + a.ix_name
                                                              + CASE WHEN a.is_primary_key = 1 THEN ' PRIMARY KEY '+ix_type_desc+' ' ELSE ' UNIQUE' END + '(' + indexColumns.ix_index_column_name + ')'
                                                          ELSE 'CREATE ' + CASE WHEN a.ix_unique = 1 THEN 'UNIQUE ' ELSE '' END 
                                                              + a.ix_type_desc + ' INDEX [' + a.ix_name collate SQL_Latin1_General_CP1_CI_AS + '] ON ' + a.schema_name
                                                              + '.' + a.table_name + '(' + indexColumns.ix_index_column_name + ')'
                                                              + CASE WHEN IncludeIndex.ix_included_column_name IS NOT NULL THEN ' INCLUDE (' + IncludeIndex.ix_included_column_name + ')' ELSE '' END
                                                              + ' ON [' + a.fg_name +']' END
                                         ,CASE WHEN a.ix_unique = 1 THEN 'UNIQUE' END AS ix_unique
                                         ,a.ix_type_desc
                                         ,a.ix_name
                                         ,a.schema_name
                                         ,a.table_name
                                         ,indexColumns.ix_index_column_name
                                         ,IncludeIndex.ix_included_column_name
                                         ,a.fg_name
                                         ,a.is_primary_key
                                         ,a.is_unique_constraint
                                         into EAP_CJT_allindexs
                                                   FROM
                                                   (
                                                          SELECT DISTINCT
                                         ix_unique
                                         ,ix_type_desc
                                         ,ix_name
                                         ,schema_name
                                         ,table_name
                                         ,fg_name
                                         ,is_primary_key
                                         ,is_unique_constraint
                                                          FROM tx
                                                   ) AS a
                                                   OUTER APPLY
                                                   (

                                                      SELECT ix_index_column_name
                                                          = STUFF((
                                                          SELECT ',' + column_name + CASE WHEN is_descending_key = 1 THEN ' DESC' ELSE '' END
                                                            FROM tx AS b
                                                          WHERE schema_name = a.schema_name
                                                              AND table_name=a.table_name
                                                              AND ix_name=a.ix_name

                                                              AND ix_type_desc=a.ix_type_desc
                                                              AND fg_name=a.fg_name
                                                              AND is_included_column=0
                                                          ORDER BY index_column_id
                                                              FOR XML PATH('')
                                                          ),1,1,'')
                                         )IndexColumns
                                                   OUTER APPLY
                                                   (
                                                          SELECT ix_included_column_name
                                                               = STUFF((
                                                                   SELECT ',' + column_name
                                                                    FROM tx AS b
                                                                  WHERE schema_name = a.schema_name
                                                                    AND table_name=a.table_name
                                                                    AND ix_name=a.ix_name
                                                                    AND ix_type_desc=a.ix_type_desc
                                                                    AND fg_name=a.fg_name
                                                                    AND is_included_column=1
                                                                  ORDER BY index_column_id
                                                                    FOR XML PATH('')
                                                                  ), 1,1,'')
                                         )IncludeIndex
                                                   ORDER BY a.schema_name,a.table_name,a.ix_name; 
                                         '''
                sql1 = sql + '\n' + sql0
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql1)
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    cur.close()
                    logging.info(f'****保留{oridb}默认索引成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****保留{oridb}默认索引失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'****保留{oridb}默认索引失败，数据库连接中断')
                return 'Unconnect'
  # --<3>.删除目标库的所有约束和所有表
    def DelConIndTab(self,oridb):
        logging.info(f'**删除{oridb}所有约束和所有表')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'use [{oridb}]'
                    sql0 = '''
                             delete  from EAP_CJT_allindexs where table_name like '%temp_0%'
                             --删除所有约束（在新帐套中执行）
                              DECLARE @DropFKSQL nvarchar(1000) 
                              SET @DropFKSQL=' '
                              WHILE @DropFKSQL IS NOT NULL
                              BEGIN
                                      SET @DropFKSQL = 
                                     (
                                         SELECT MIN(DropFKSQL)
                                         FROM    EAP_CJT_ALLCONSTRAINT 
                             WHERE  DropFKSQL> @DropFKSQL
                                     )
                             if(@DropFKSQL is not null)
                             begin
                             EXEC(@DropFKSQL)
                             end
                             end
                             --删除所有表（在新帐套中执行）
                             declare @sql varchar(8000)
                             while (select count(*) from sysobjects where type='U' and [name] not like 'EAP[_]CJT[_]%')>0
                             begin
                             SELECT @sql='drop table ' +'['+name+']'
                             FROM sysobjects
                             WHERE (type = 'U' and [name] not like 'EAP[_]CJT[_]%')
                             ORDER BY 'drop table ' + name
                             exec(@sql)
                             end 
                             '''
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    RC = cur.rowcount
                    logging.info(f'**删除{oridb}所有约束和所有表成功')
                    return RC
                except Exception as e:
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****删除{oridb}所有约束和所有表失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**删除{oridb}所有约束和所有表失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'use [{oridb}]'
                sql = f'use [{oridb}]'
                sql0 = '''
                                         delete  from EAP_CJT_allindexs where table_name like '%temp_0%'
                                         --删除所有约束（在新帐套中执行）
                                          DECLARE @DropFKSQL nvarchar(1000) 
                                          SET @DropFKSQL=' '
                                          WHILE @DropFKSQL IS NOT NULL
                                          BEGIN
                                                  SET @DropFKSQL = 
                                                 (
                                                     SELECT MIN(DropFKSQL)
                                                     FROM    EAP_CJT_ALLCONSTRAINT 
                                         WHERE  DropFKSQL> @DropFKSQL
                                                 )
                                         if(@DropFKSQL is not null)
                                         begin
                                         EXEC(@DropFKSQL)
                                         end
                                         end
                                         --删除所有表（在新帐套中执行）
                                         declare @sql varchar(8000)
                                         while (select count(*) from sysobjects where type='U' and [name] not like 'EAP[_]CJT[_]%')>0
                                         begin
                                         SELECT @sql='drop table ' +'['+name+']'
                                         FROM sysobjects
                                         WHERE (type = 'U' and [name] not like 'EAP[_]CJT[_]%')
                                         ORDER BY 'drop table ' + name
                                         exec(@sql)
                                         end 
                                         '''
                sql1 = sql + '\n' + sql0
                try:
                    cur = con.cursor()
                    con.autocommit = True
                    cur.execute(sql1)
                    while cur.nextset():
                        pass
                    con.autocommit = False
                    cur.close()
                    logging.info(f'****删除{oridb}所有约束和所有表成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    cur.close()
                    res = self.ErrorMark(str(e))
                    logging.error(f'****删除{oridb}所有约束和所有表失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'****删除{oridb}所有约束和所有表失败，数据库连接中断')
                return 'Unconnect'
 #生成插入语句需要的表名字
    def GetINsertTBN(self, brkdb, ErrorList):
        logging.info(f'**生成插入{brkdb}的表名字')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                sql = f'use [{brkdb}]'
                sql0 = f"select TABLE_NAME FROM  [{brkdb}].INFORMATION_SCHEMA.TABLES where  TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME NOT LIKE 'TEMP_0_%'"
                ERT = str(ErrorList)[1:-1]
                sqlEx = f"AND  TABLE_NAME NOT IN({ERT})"
                if len(ErrorList) > 0:
                    try:
                        sql1 = sql + '\n' + sql0 + sqlEx
                        cur.execute(sql1)
                        rs = cur.fetchall()
                        tb = tuple2list(rs)
                        return tb
                    except Exception as e:
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'****生成插入{brkdb}的表名字成功失败，失败原因为{e}')
                        return False
                else:
                    try:
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                        rs = cur.fetchall()
                        tb = tuple2list(rs)
                        return tb
                    except Exception as e:
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'****生成插入{brkdb}的表名字成功失败，失败原因为{e}')
                        return False
                logging.info(f'**生成插入{brkdb}的表名字成功')
            else:
                logging.warning(f'**生成插入{brkdb}的表名字失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                sql = f'use [{brkdb}]'
                sql0 = f"select TABLE_NAME FROM  [{brkdb}].INFORMATION_SCHEMA.TABLES where  TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME NOT LIKE 'TEMP_0_%'"
                ERT = str(ErrorList)[1:-1]
                sqlEx = f"AND  TABLE_NAME NOT IN({ERT})"
                if len(ErrorList) > 0:
                    try:
                        cur = con.cursor()
                        con.autocommit = True
                        sql1 = sql + '\n' + sql0 + sqlEx
                        cur.execute(sql1)
                        rows = None
                        # this section will only return the last result from the query
                        while cur.nextset():
                            try:
                                rows = cur.fetchall()
                            except Exception as e:
                                print("Skipping non rs message: {}".format(e))
                            continue
                        rs = rows
                        db = tuple2listodbc(rs)
                        cur.close()
                        logging.info(f'**生成插入{brkdb}的表名字成功')
                        return db
                    except Exception as e:
                        con.autocommit = False
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'****生成插入{brkdb}的表名字成功失败，失败原因为{e}')
                        return False
                else:
                    try:
                        cur = con.cursor()
                        con.autocommit = True
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                        rows = None
                        # this section will only return the last result from the query
                        while cur.nextset():
                            try:
                                rows = cur.fetchall()
                            except Exception as e:
                                print("Skipping non rs message: {}".format(e))
                            continue
                        rs = rows
                        db = tuple2listodbc(rs)
                        cur.close()
                        logging.info(f'**生成插入{brkdb}的表名字成功')
                        return db
                    except Exception as e:
                        con.autocommit = False
                        cur.close()
                        res = self.ErrorMark(str(e))
                        logging.error(f'****生成插入{brkdb}的表名字成功失败，失败原因为{e}')
                        return False
            else:
                logging.warning(f'**生成插入{brkdb}的表名字失败，数据库连接中断')
                return 'Unconnect'
# 生成插入语句
    def CreateINSQL(self,OTL,ErrorList, brkdb, bakdb):
        logging.info(f'**生成插入{brkdb}的sql语句')
        sqllist = []
        for tbO in OTL:
            sql = f'select * into [dbo].[{tbO}] from [{brkdb}].[dbo].[{tbO}]'
            sqllist.append(sql)
            # logging.info(f'insert good table sql add:{sql}')
        for tbE in ErrorList:
            sql = f'select * into [dbo].[{tbE}] from [{bakdb}].[dbo].[{tbE}]'
            sqllist.append(sql)
            # logging.info(f'insert Error table sql add:{sql}')
        logging.info(f'**生成插入{brkdb}的sql语句成功')
        return sqllist
 # 插入数据
    def InsertSQL(self,oridb, InL):
        logging.info(f'**向{oridb}插入数据')
        self._ReConnect()
        con = self._conn
        ErroINSQL = []
        if self._dver == 'pymssql driver':
            if con != False:
                for sql0 in InL:
                    try:
                        con.autocommit(True)
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                    except:
                        ErroINSQL.append(sql0)
                logging.error(f'**向{oridb}插入数据结束，插入失败的语句有{ErroINSQL}')
                return ErroINSQL
            else:
                logging.warning(f'**向{oridb}插入数据失败，数据连接中断')
                return 'Unconnect'
        else:
            if con:
                for sql0 in InL:
                    try:
                        con.autocommit= True
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                        RC = cur.rowcount
                        while cur.nextset():
                            pass
                        cur.close()
                        con.autocommit = False
                    except Exception as e:
                        con.autocommit = False
                        ErroINSQL.append(sql0)
                logging.error(f'**向{oridb}插入数据结束，插入失败的语句有{ErroINSQL}')
                return ErroINSQL
            else:
                logging.warning(f'**向{oridb}插入数据失败，数据库连接中断')
                return 'Unconnect'

  # 导表第四步 重建索引、约束
    # --建默认值约束（新帐套执行）
    # 获取默认约束脚本
    def RebuildDefaultSQL(self,oridb):
        logging.info(f'**获取重建{oridb}的默认约束')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'use [{oridb}]'
                    sql0 = 'select Defaultsql from EAP_CJT_DefaultValue'
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    rs = cur.fetchall()
                    RBSQLLst = tuple2list(rs)
                    logging.info(f'**获取重建{oridb}的默认约束成功')
                    return RBSQLLst
                except Exception as e:
                    logging.error(f'**获取重建{oridb}的默认约束失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取重建{oridb}的默认约束失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                con.autocommit = True
                cur = con.cursor()
                sql = f'use [{oridb}]'
                sql0 = 'select Defaultsql from EAP_CJT_DefaultValue'
                sql1 = sql + '\n' + sql0
                try:
                    cur.execute(sql1)
                    rows = None
                    # this section will only return the last result from the query
                    while cur.nextset():
                        try:
                            rows = cur.fetchall()
                        except Exception as e:
                            print("Skipping non rs message: {}".format(e))
                        continue
                    rs = rows
                    rt = tuple2listodbc(rs)
                    # rl = [rt[0], rt[1]]
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**获取重建{oridb}的默认约束成功')
                    return rt
                except Exception as e:
                    logging.error(f'**获取重建{oridb}的默认约束失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取重建{oridb}的默认约束失败，数据库连接中断')
                return 'Unconnect'
    #     执行重建默认约束的脚本
    def RebuildDCons(self,oridb, RSL):
        logging.info(f'**重建{oridb}默认约束')
        self._ReConnect()
        con = self._conn
        ErrorDCons = []
        if self._dver == 'pymssql driver':
            if con != False:
                for sql0 in RSL:
                    try:
                        con.autocommit(True)
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                    except:
                        ErrorDCons.append(sql0)
                logging.error(f'**重建{oridb}默认约束结束，失败的默认约束语句为{ErrorDCons}')
                return ErrorDCons
            else:
                logging.warning(f'**重建{oridb}默认约束失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                for sql0 in RSL:
                    try:
                        con.autocommit = True
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                        RC = cur.rowcount
                        while cur.nextset():
                            pass
                        cur.close()
                        con.autocommit = False
                    except Exception as e:
                        con.autocommit = False
                        ErrorDCons.append(sql0)
                    logging.error(f'**重建{oridb}默认约束结束，插入失败的语句有{ErrorDCons}')
                    return ErrorDCons
            else:
                logging.warning(f'**重建{oridb}默认约束失败，数据库连接中断')
                return 'Unconnect'
    #   获取重建索引的脚本
    def RebuildInxSQL(self,oridb):
        logging.info(f'**获取重建{oridb}的索引')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'use [{oridb}]'
                    sql0 = 'SELECT Create_Index FROM    EAP_CJT_allindexs'
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    rs = cur.fetchall()
                    RBSQLLst = tuple2list(rs)
                    logging.info(f'**获取重建{oridb}的索引成功')
                    return RBSQLLst
                except Exception as e:
                    logging.error(f'**获取重建{oridb}的索引失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取重建{oridb}的失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                con.autocommit = True
                cur = con.cursor()
                sql = f'use [{oridb}]'
                sql0 = 'SELECT Create_Index FROM    EAP_CJT_allindexs'
                sql1 = sql + '\n' + sql0
                try:
                    cur.execute(sql1)
                    rows = None
                    # this section will only return the last result from the query
                    while cur.nextset():
                        try:
                            rows = cur.fetchall()
                        except Exception as e:
                            print("Skipping non rs message: {}".format(e))
                        continue
                    rs = rows
                    rt = tuple2listodbc(rs)
                    # rl = [rt[0], rt[1]]
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**获取重建{oridb}的索引成功')
                    return rt
                except Exception as e:
                    logging.error(f'**获取重建{oridb}的索引失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取重建{oridb}的索引失败，数据库连接中断')
                return 'Unconnect'
    #     执行重建索引的脚本
    def RebuildInx(self,oridb, RSL):
        logging.info(f'**重建{oridb}索引')
        self._ReConnect()
        con = self._conn
        ErrorInx = []
        if self._dver == 'pymssql driver':
            if con != False:
                for sql0 in RSL:
                    try:
                        con.autocommit(True)
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                    except:
                        ErrorInx.append(sql0)
                logging.error(f'**重建{oridb}索引结束，失败的索引语句为{ErrorInx}')
                return ErrorInx
            else:
                logging.warning(f'**重建{oridb}索引失败，数据连接中断')
                return 'Unconnect'
        else:
            if con:
                for sql0 in RSL:
                    try:
                        con.autocommit = True
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                        RC = cur.rowcount
                        while cur.nextset():
                            pass
                        cur.close()
                        con.autocommit = False
                    except Exception as e:
                        con.autocommit = False
                        ErrorInx.append(sql0)
                    logging.error(f'**重建{oridb}索引结束，失败的索引语句为{ErrorInx}')
                    return  ErrorInx
            else:
                logging.warning(f'**重建{oridb}索引失败，数据连接中断')
                return 'Unconnect'
    #   获取重建约束的脚本
    def RebuildConsSQL(self,oridb):
        logging.info(f'**获取重建{oridb}的约束')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                con.autocommit(True)
                cur = con.cursor()
                try:
                    sql = f'use [{oridb}]'
                    sql0 = 'SELECT AddFKSQL FROM EAP_CJT_ALLCONSTRAINT'
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    rs = cur.fetchall()
                    RBSQLLst = tuple2list(rs)
                    logging.info(f'**获取重建{oridb}的约束成功')
                    return RBSQLLst
                except Exception as e:
                    logging.error(f'**获取重建{oridb}的约束失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取重建{oridb}的约束失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                con.autocommit = True
                cur = con.cursor()
                sql = f'use [{oridb}]'
                sql0 = 'SELECT AddFKSQL FROM EAP_CJT_ALLCONSTRAINT'
                sql1 = sql + '\n' + sql0
                try:
                    cur.execute(sql1)
                    rows = None
                    # this section will only return the last result from the query
                    while cur.nextset():
                        try:
                            rows = cur.fetchall()
                        except Exception as e:
                            print("Skipping non rs message: {}".format(e))
                        continue
                    rs = rows
                    rt = tuple2listodbc(rs)
                    # rl = [rt[0], rt[1]]
                    con.autocommit = False
                    cur.close()
                    logging.info(f'**获取重建{oridb}的约束成功')
                    return rt
                except Exception as e:
                    logging.error(f'**获取重建{oridb}的约束失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**获取重建{oridb}的约束失败，数据库连接中断')
                return 'Unconnect'
    #     执行重建约束的脚本
    def RebuildCons(self,oridb, RSL):
        logging.info(f'**重建{oridb}约束')
        self._ReConnect()
        con = self._conn
        ErrorCons = []
        if self._dver == 'pymssql driver':
            if con != False:
                for sql0 in RSL:
                    try:
                        con.autocommit(True)
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                    except:
                        ErrorCons.append(sql0)
                logging.error(f'**重建{oridb}约束结束，重建失败的约束语句为{ErrorCons}')
                return ErrorCons
            else:
                logging.warning(f'**重建{oridb}约束失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                for sql0 in RSL:
                    try:
                        con.autocommit = True
                        cur = con.cursor()
                        sql = f'use [{oridb}]'
                        sql1 = sql + '\n' + sql0
                        cur.execute(sql1)
                        RC = cur.rowcount
                        while cur.nextset():
                            pass
                        cur.close()
                        con.autocommit = False
                    except Exception as e:
                        con.autocommit = False
                        ErrorCons.append(sql0)
                logging.error(f'**重建{oridb}约束结束，重建失败的约束语句为{ErrorCons}')
                return ErrorCons
            else:
                logging.warning(f'**重建{oridb}约束失败，数据库连接中断')
                return 'Unconnect'
    #   创日期表
    def Enddate(self,oridb):
        logging.info(f'**在{oridb}中记录导表日期')
        self._ReConnect()
        con = self._conn
        if self._dver =='pymssql driver':
            if con != False:
                timedate = str(time.strftime('%Y.%m.%d', time.localtime(time.time())))
                try:
                    con.autocommit(True)
                    cur = con.cursor()
                    sql = f'use [{oridb}]'
                    sql0 = f'''
                    create table checkdate
                    (xfsj varchar(60))
                    insert into checkdate values ('{timedate}')
                    select * from sys.indexes
                    dbcc useroptions 
                    '''
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    RC = cur.rowcount
                    logging.info(f'**在{oridb}中记录导表日期成功')
                    return RC
                except Exception as e:
                    logging.error(f'**在{oridb}中记录导表日期失败，失败原因为{e}')
                    res = self.ErrorMark(str(e))
                    return res
            else:
                logging.warning(f'**在{oridb}中记录导表日期失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                timedate = str(time.strftime('%Y.%m.%d', time.localtime(time.time())))
                try:
                    cur = con.cursor()
                    sql = f'use [{oridb}]'
                    sql0 = f'''
                                       create table checkdate
                                       (xfsj varchar(60))
                                       insert into checkdate values ('{timedate}')
                                       select * from sys.indexes
                                       dbcc useroptions 
                                       '''
                    sql1 = sql + '\n' + sql0
                    # print(sql)
                    con.autocommit = True
                    cur.execute(sql1)
                    RC = cur.rowcount
                    while cur.nextset():
                        pass
                    cur.close()
                    con.autocommit = False
                    logging.info(f'**在{oridb}中记录导表日期成功')
                    return RC
                except Exception as e:
                    con.autocommit = False
                    logging.error(f'**在{oridb}中记录导表日期失败，失败原因为{e}')
                    res = self.ErrorMark(str(e))
                    return res
            else:
                logging.warning(f'**在{oridb}中记录导表日期失败，数据库连接中断')
                return 'Unconnect'
    #   允许快照打开
    def FlashOpen(self, oridb):
        logging.info(f'**在{oridb}中允许快照打开')
        self._ReConnect()
        con = self._conn
        if self._dver =='pymssql driver':
            if con != False:
                try:
                    con.autocommit(True)
                    cur = con.cursor()
                    sql = f'use master'
                    sql0 = f'ALTER DATABASE [{oridb}] SET READ_COMMITTED_SNAPSHOT ON WITH NO_WAIT'
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    RC = cur.rowcount
                    logging.info(f'**在{oridb}中允许快照打开成功')
                    return RC
                except Exception as e:
                    logging.error(f'**在{oridb}中允许快照打开失败，失败原因为{e}')
                    res = self.ErrorMark(str(e))
                    return res
            else:
                logging.warning(f'**在{oridb}中允许快照打开失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                try:
                    cur = con.cursor()
                    sql = f'use master'
                    sql0 = f'ALTER DATABASE [{oridb}] SET READ_COMMITTED_SNAPSHOT ON WITH NO_WAIT'
                    sql1 = sql + '\n' + sql0
                    # print(sql)
                    con.autocommit = True
                    cur.execute(sql1)
                    RC = cur.rowcount
                    while cur.nextset():
                        pass
                    cur.close()
                    con.autocommit = False
                    logging.info(f'**在{oridb}中允许快照打开成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    logging.error(f'**在{oridb}中允许快照打开失败，失败原因为{e}')
                    return False
            else:
                logging.warning(f'**在{oridb}中允许快照打开失败，数据库连接中断')
                return 'Unconnect'
    #   允许快照独立
    def FlashSeparate(self,oridb):
        logging.info(f'**在{oridb}中允许快照独立')
        self._ReConnect()
        con = self._conn
        if self._dver == 'pymssql driver':
            if con != False:
                try:
                    con.autocommit(True)
                    cur = con.cursor()
                    sql = f'use master'
                    sql0 = f'ALTER DATABASE [{oridb}] SET ALLOW_SNAPSHOT_ISOLATION ON'
                    sql1 = sql + '\n' + sql0
                    cur.execute(sql1)
                    RC = cur.rowcount
                    logging.info(f'**在{oridb}中允许快照独立成功')
                    return RC
                except Exception as e:
                    logging.error(f'**在{oridb}中允许快照独立失败，失败原因为{e}')
                    res = self.ErrorMark(str(e))
                    return res
            else:
                logging.warning(f'**在{oridb}中允许快照独立失败，数据库连接中断')
                return 'Unconnect'
        else:
            if con:
                try:
                    cur = con.cursor()
                    sql = f'use master'
                    sql0 = f'ALTER DATABASE [{oridb}] SET ALLOW_SNAPSHOT_ISOLATION ON'
                    sql1 = sql + '\n' + sql0
                    # print(sql)
                    con.autocommit = True
                    cur.execute(sql1)
                    RC = cur.rowcount
                    while cur.nextset():
                        pass
                    cur.close()
                    con.autocommit = False
                    logging.info(f'**在{oridb}中允许快照独立成功')
                    return True
                except Exception as e:
                    con.autocommit = False
                    logging.error(f'**在{oridb}中允许快照独立失败，失败原因为{e}')
                    res = self.ErrorMark(str(e))
                    return res
            else:
                logging.warning(f'**在{oridb}中允许快照独立失败，数据库连接中断')
                return 'Unconnect'
    
    # 获取所有数据库列表
    def getAllDatabases(self):
        """获取所有数据库列表"""
        self._ReConnect()
        con = self._conn
        
        if con:
            try:
                cur = con.cursor()
                sql = "SELECT name FROM sys.databases WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')"
                
                if self._dver == 'pymssql driver':
                    con.autocommit(True)
                    cur.execute(sql)
                    rs = cur.fetchall()
                    con.autocommit(False)
                else:
                    cur.execute(sql)
                    rs = cur.fetchall()
                
                cur.close()
                
                # 提取数据库名称
                databases = [row[0] for row in rs]
                return databases
                
            except Exception as e:
                logging.error(f'获取数据库列表失败: {e}')
                return 'Unconnect'
        else:
            logging.warning('获取数据库列表失败，数据库连接中断')
            return 'Unconnect'

if __name__ == '__main__':
    driver ='{ODBC Driver 18 for SQL Server}'
    # driver = 'pymssql driver'

    # driver = '{Easysoft ODBC-SQL Server}'
    host = '.'
    uname = ''
    upwd = ''
    basedb = 'master'
    A = TsDBdriver(host,uname,upwd,driver,basedb)
    print(A.SQLcon())




    # dbname = 'testc'
    # path ='G:\\123.bak'
    # filename = 'E:\\testc.bak'
    # # oldlogiclist= ['Ufmodel','Ufmodel_LOG']
    # dbpath = 'E:'
    # dbname ='testc.bak'
    # oldlogfilelist = ['E:\\testc\\testc.mdf','E:\\testc\\testc.ldf']
    # newlogiclist = ['E:\\testc\\testc.mdf','E:\\testc\\testc.ldf']
    # a = TsDBdriver(driver,host,uname,upwd,basedb)
    # b = a.RepeatDB(dbname)
    # # rs = a.GetLogicallist(dbname)
    # # rs = a.RestoreDB(filename, dbname, oldlogiclist, newlogiclist)
    # # rs = a.DeleteDB(dbname)
    # # rs = a.detachDB(dbname)
    # # rs = a.AttachDB(dbname,oldlogfilelist)
    # # rs = a.DBlist(dbname)
    # # rs = a.GetbakLogic(dbname, dbpath)
    # rs = a.DBCC('brk1')
    # print(rs)