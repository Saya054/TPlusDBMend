import sqlite3,sys
from .basicFunc import *
import logging
class BaseDBfunc(object):
    def __init__(self,dbfile):
        # dbname包含了路径的
        self._dbfile = dbfile
        self._conn = None
        self._ReConnect()
    def _ReConnect(self):
        if not self._conn:
            try:
                self._conn = sqlite3.connect(self._dbfile,check_same_thread=False)
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
    # 更新
    def Exec(self, sql):
        rt = None
        cur = self._NewCursor()
        conn = self._conn
        if not cur:
            return rt
        if self.PermitedUpdateSql(self, sql) == False:
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
    #独立功能
    '''
    初始化创建database
    '''
    def CreateConfigTB(self):
        con = self._conn
        logging.info('config文件生成--创建Config表')
        if con:
            # 构建新的sql，通过修改文件位置保证物理文件不重复
            sql = f'''create table Config(host varchar(120)	
                    ,usr varchar(10),pwd varchar(240)
                    ,driver varchar(120),adminlogin bit default 0,
                    autocomplete bit default 0,manualadd bit default 0,theme varchar(60),version varchar(20),identication varchar(20))
                      '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                cur.close()
                logging.info('config文件生成--创建Config表成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'config文件生成--创建Config表失败，失败原因为{e}')
                return f'创建失败，失败原因为 {e}'
        else:
            logging.warning('config文件生成--创建Config表失败，连接中断')
            return 'Unconnect'
    def CreateDefaultConfTB(self):
        con = self._conn
        logging.info('config文件生成--创建Config表')
        if con:
            # 构建新的sql，通过修改文件位置保证物理文件不重复
            sql = f'''create table DefaultConf(brokename  varchar(120)	
                           ,originame  varchar(120),sparename  varchar(120)
                           ,brokesavepath  varchar(600),originsavepath  varchar(600),
                           repairsavepath varchar(600),sparesavepath  varchar(600),brokelogicpath varchar(600),
                            originlogicpath varchar(600),sparelogicpath varchar(600)
                            )
                             '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                cur.close()
                logging.info('config文件生成--创建Defaultconfig表成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'config文件生成--创建Defaultconfig表失败，失败原因为{e}')
                return f'创建失败，失败原因为 {e}'
        else:
            logging.warning('config文件生成--创建Defaultconfig表失败，连接中断')
            return 'Unconnect'
    def CreateProgressInfoTB(self):
        con = self._conn
        logging.info('config文件生成--创建progressinfo表')
        if con:
            # 构建新的sql，通过修改文件位置保证物理文件不重复
            sql = f'''create table progressinfo(progress int,bakresult varchar(10),status varchar(120))
                      '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                # time.sleep(5)
                cur.close()
                logging.info('config文件生成--创建progressinfo表成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'config文件生成--创建progressinfo表失败,失败原因为{e}')
                return f'创建失败，失败原因为 {e}'
        else:
            logging.warning('config文件生成--创建progressinfo表失败，连接中断')
            return 'Unconnect'
    def DeleteConfigTB(self):
        con = self._conn
        logging.info('config文件初始化--删除config表内容')
        if con:

            sql = f'''delete from config
                             '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                # time.sleep(5)
                cur.close()
                logging.info('config文件初始化--删除config表内容成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'config文件初始化--删除config表失败，失败原因为{e}')
                return f'清空失败，失败原因为 {e}'
        else:
            logging.warning('config文件初始化--删除config表内容失败,连接中断')
            return 'Unconnect'
    def InsertDefaultConfig(self):
        con = self._conn
        logging.info('config文件初始化--向config表插入初始数据')
        if con:
            sql = f'''insert into config(host,usr,pwd,driver,adminlogin,autocomplete,manualadd,theme,version,identication)
            values('127.0.0.1','','','pymssql driver','1','0','0','cosmo','V4.01','friend')
                      '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                cur.close()
                logging.info('config文件初始化--向config表插入初始数据成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'config文件初始化--向config表插入初始数据失败，失败原因为{e}')
                return f'插入失败，失败原因为 {e}'
        else:
            logging.warning('config文件初始化--向config表插入初始数据失败，连接中断')
            return 'Unconnect'
    def getConfig(self,keyword):
        con = self._conn
        logging.info(f'加载config--获取config中的{keyword}字段数据')
        if con:
            sql = f'''select {keyword} from config'''
            try:
                cur = con.cursor()
                cur.execute(sql)
                rs = cur.fetchall()
                con.commit()  # 记住 commit
                if len(rs) > 0:
                    rd = tuple2listodbc(rs)[0]
                    cur.close()
                    logging.info(f'加载config--获取config中的{keyword}字段数据成功，结果为{rd}')
                    return rd
                else:
                    cur.close()
                    logging.info(f'加载config--获取config中的{keyword}字段数据成功，但是并未查到数据')
                    return None
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'加载config--获取config中的{keyword}字段数据失败，失败原因为{e}')
                return f'获取失败，失败原因为 {e}'

        else:
            logging.warning(f'加载config--获取config中的{keyword}字段数据失败，连接中断')
            return None
    def getDefaultConfig(self,keyword):
        con = self._conn
        logging.info(f'加载config--获取config中的{keyword}字段数据')
        if con:
            sql = f'''select {keyword} from DefaultConf'''
            try:
                cur = con.cursor()
                cur.execute(sql)
                rs = cur.fetchall()
                con.commit()  # 记住 commit
                if len(rs) > 0:
                    rd = tuple2listodbc(rs)[0]
                    cur.close()
                    logging.info(f'加载config--获取defaultconfig中的{keyword}字段数据成功，结果为{rd}')
                    return rd
                else:
                    cur.close()
                    logging.info(f'加载config--获取defaultconfig中的{keyword}字段数据成功，但是并未查到数据')
                    return None
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'加载config--获取defaultconfig中的{keyword}字段数据失败，失败原因为{e}')
                return f'获取失败，失败原因为 {e}'

        else:
            logging.warning(f'加载config--获取defaultconfig中的{keyword}字段数据失败，连接中断')
            return None
    def SaveConfig(self,host,usr,pwd,driver,adminstate,autocomplete,manualadd,theme):
        con = self._conn
        logging.info(f'保存config--保存配置文件')
        if con:
            try:
                cur = con.cursor()
                sql = f'''  UPDATE config set host = '{host}',usr = '{usr}',pwd ='{pwd}',driver = '{driver}',
                    adminlogin ={adminstate},autocomplete ={autocomplete},manualadd = {manualadd},theme = '{theme}'
                                          '''
                print(sql)
                cur.execute(sql)
                RC = cur.rowcount
                con.commit()
                if RC == 0:
                    logging.info(f'保存config--保存配置文件成功，但是0行受到影响')
                    cur.close()
                    return None
                else:
                    logging.info(f'保存config--保存配置文件成功')
                    cur.close()
                    return True
            except Exception as e:
                logging.warning(f'保存config--保存配置文件失败，失败原因为{e}')
                return False
        else:
            logging.warning(f'保存config--保存配置文件失败，连接中断')
            return 'Unconnect'
    #初始化progressinfo表
    def DeleteprogressinfoTB(self):
        con = self._conn
        logging.info(f'progressinfo初始化--删除progressinfo信息')
        if con:
            sql = f'''delete from progressinfo
                               '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                # time.sleep(5)
                cur.close()
                logging.info(f'progressinfo初始化--删除progressinfo信息成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'progressinfo初始化--删除progressinfo信息失败，失败原因为{e}')
                return f'清空失败，失败原因为 {e}'
        else:
            logging.warning(f'progressinfo初始化--删除progressinfo信息失败，连接中断')
            return 'Unconnect'
    def InsertDefaultprogressinfo(self):
        con = self._conn
        logging.info(f'progressinfo初始化--插入初始数据')
        if con:
            sql = f'''insert into progressinfo(progress,bakresult,status)
              values('0','0','')
                        '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                cur.close()
                logging.info(f'progressinfo初始化--插入初始数据成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'progressinfo初始化--插入初始数据失败，失败原因为{e}')
                return f'插入失败，失败原因为 {e}'
        else:
            logging.info(f'progressinfo初始化--插入初始数据失败，连接中断')
            return 'Unconnect'
    def getprogressinfo(self):
        con = self._conn
        # logging.info(f'加载progressinfo--读取progressinfo信息')
        if con:
            sql = f'''select progress,bakresult,status from progressinfo'''
            try:
                cur = con.cursor()
                cur.execute(sql)
                rs = cur.fetchall()
                con.commit()  # 记住 commit
                if len(rs) > 0:
                    rd = list(rs)
                    cur.close()
                    # logging.info(f'加载progressinfo--读取progressinfo信息成功，信息为{rd}')
                    return rd
                else:
                    cur.close()
                    # logging.info(f'加载progressinfo--读取progressinfo信息成功，但是返回信息为空')
                    return None
            except Exception as e:
                cur.close()
                res = str(e)
                # logging.warning(f'加载progressinfo--读取progressinfo信息失败，失败原因为{e}')
                return f'获取失败，失败原因为 {e}'
        else:
            # logging.warning(f'加载progressinfo--读取progressinfo信息失败，连接中断')
            return 'Unconnect'
    def Insertprogressinfo(self,progress,bakresult):
        con = self._conn
        logging.info(f'保存progressinfo--插入progressinfo信息')
        if con:
            try:
                cur = con.cursor()
                sql = f'''  insert into progressinfo(progress,bakresult)
                        values('{progress}','{bakresult}')
                                            '''
                print(sql)
                cur.execute(sql)
                RC = cur.rowcount
                con.commit()
                if RC == 0:
                    cur.close()
                    logging.info(f'保存progressinfo--插入progressinfo信息成功，但是0行受到影响')
                    return None
                else:
                    cur.close()
                    logging.info(f'保存progressinfo--插入progressinfo信息成功')
                    return True
            except Exception as e:
                print(e)
                logging.warning(f'保存progressinfo--插入progressinfo信息失败，失败原因为{e}')
                return False
        else:
            logging.warning(f'保存progressinfo--插入progressinfo信息失败，连接中断')
            return 'Unconnect'
    def DeleteDefaultconfTB(self):
        con = self._conn
        logging.info(f'Defaultconf初始化--删除Defaultconf信息')
        if con:
            sql = f'''delete from DefaultConf
                                       '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                # time.sleep(5)
                cur.close()
                logging.info(f'Defaultconf初始化--删除Defaultconf信息成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'Defaultconf初始化--删除Defaultconf信息失败，失败原因为{e}')
                return f'清空失败，失败原因为 {e}'
        else:
            logging.warning(f'Defaultconf初始化--删除Defaultconf信息失败，连接中断')
            return 'Unconnect'
    def  InsertDefaultdfconf(self):
        con = self._conn
        logging.info(f'progressinfo初始化--插入初始数据')
        if con:
            sql = f'''insert into DefaultConf(brokename,originame,sparename
                           ,brokesavepath,originsavepath,
                           repairsavepath,sparesavepath,brokelogicpath,
                            originlogicpath,sparelogicpath)
                     values('broken','origin','origin1','./Data/broken/zipfile','./Data/orifile/zipfile','./Data/repaired','./Data/bakfile/zipfile','./Data/broken/logicfile'
                    ,'./Data/orifile/logicfile','./Data/bakfile/logicfile')
                               '''
            try:
                cur = con.cursor()
                cur.execute(sql)
                con.commit()  # 记住 commit
                cur.close()
                logging.info(f'progressinfo初始化--插入初始数据成功')
                return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'progressinfo初始化--插入初始数据失败，失败原因为{e}')
                return f'插入失败，失败原因为 {e}'
        else:
            logging.info(f'progressinfo初始化--插入初始数据失败，连接中断')
            return 'Unconnect'
    def CheckconfigTB(self):
        con = self._conn
        logging.info(f'校验config--校验是否为正常的config表')
        if con:
            sql = f'''select host,usr,pwd,driver,adminlogin,autocomplete,manualadd,theme,version,identication from config
               '''
            print(sql)
            try:
                cur = con.cursor()
                cur.execute(sql)
                rs = cur.fetchall()
                con.commit()  # 记住 commit
                if len(rs) > 0:
                    rd = list(rs)
                    cur.close()
                    logging.info(f'校验config--校验是否为正常的config表通过')
                    return True
                else:
                    cur.close()
                    logging.info(f'校验config--校验是否为正常的config表通过')
                    return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'校验config--校验是否为正常的config表失败，失败原因为{e}')
                return False
        else:
            logging.warning(f'校验config--校验是否为正常的config表失败，连接中断')
            return 'Unconnect'
    def CheckprogressinfoTB(self):
        con = self._conn
        logging.info(f'校验progressinfo--校验是否为正常的progressinfo表')
        if con:
            sql = f'''
              select progress,bakresult,status from progressinfo
               '''
            print(sql)
            try:
                cur = con.cursor()
                cur.execute(sql)
                rs = cur.fetchall()
                con.commit()  # 记住 commit
                if len(rs) > 0:
                    rd = list(rs)
                    cur.close()
                    logging.info(f'校验progressinfo--校验是否为正常的progressinfo表通过')
                    return True
                else:
                    cur.close()
                    logging.info(f'校验progressinfo--校验是否为正常的progressinfo表通过')
                    return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'校验progressinfo--校验是否为正常的progressinfo表失败，失败原因为{e}')
                return False
        else:
            logging.warning(f'校验progressinfo--校验is否为正常的progressinfo表失败，连接中断')
            return 'Unconnect'
    def CheckDefaultConfTB(self):
        con = self._conn
        logging.info(f'校验defaultconf--校验是否为正常的defaultconf表')
        if con:
            sql = f'''
              select brokename,originame,sparename
                           ,brokesavepath,originsavepath,
                           repairsavepath,sparesavepath,brokelogicpath,
                            originlogicpath,sparelogicpath from DefaultConf
               '''
            print(sql)
            try:
                cur = con.cursor()
                cur.execute(sql)
                rs = cur.fetchall()
                con.commit()  # 记住 commit
                if len(rs) > 0:
                    rd = list(rs)
                    cur.close()
                    logging.info(f'校验defaultconf--校验是否为正常的defaultconf表通过')
                    return True
                else:
                    cur.close()
                    logging.info(f'校验defaultconf--校验是否为正常的defaultconf表通过')
                    return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'校验defaultconf--校验是否为正常的defaultconf表失败，失败原因为{e}')
                return False
    def WriteProgress(self,progress,bakresult,status):
        con = self._conn
        logging.info(f'保存config--保存配置文件')
        if con:
            try:
                cur = con.cursor()
                sql = f'''  UPDATE progressinfo set progress = '{progress}',bakresult = '{bakresult}',status ='{status}'
                                                '''
                print(sql)
                cur.execute(sql)
                RC = cur.rowcount
                con.commit()
                if RC == 0:
                    logging.info(f'写入progress--写入进度成功，但是0行受到影响')
                    cur.close()
                    return None
                else:
                    logging.info(f'写入progress--写入进度成功')
                    cur.close()
                    return True
            except Exception as e:
                logging.warning(f'写入progress--写入进度失败，失败原因为{e}')
                return False
        else:
            logging.warning(f'写入progress--写入进度失败，连接中断')
            return 'Unconnect'
    def Dropprogress(self):
        con = self._conn
        logging.info(f'校验progressinfo--校验是否为正常的progressinfo表')
        if con:
            sql = f'''
                     drop table progressinfo
                      '''
            print(sql)
            try:
                cur = con.cursor()
                cur.execute(sql)
                rs = cur.fetchall()
                con.commit()  # 记住 commit
                if len(rs) > 0:
                    rd = list(rs)
                    cur.close()
                    logging.info(f'校验progressinfo--校验是否为正常的progressinfo表通过')
                    return True
                else:
                    cur.close()
                    logging.info(f'校验progressinfo--校验是否为正常的progressinfo表通过')
                    return True
            except Exception as e:
                cur.close()
                res = str(e)
                logging.warning(f'校验progressinfo--校验是否为正常的progressinfo表失败，失败原因为{e}')
                return False
        else:
            logging.warning(f'校验progressinfo--校验是否为正常的progressinfo表失败，连接中断')
            return 'Unconnect'
    def UpdateVersion(self,version):
        con = self._conn
        logging.info(f'保存config--保存配置文件')
        if con:
            try:
                cur = con.cursor()
                sql = f'''  UPDATE config set version = {version}'
                                                 '''
                print(sql)
                cur.execute(sql)
                RC = cur.rowcount
                con.commit()
                if RC == 0:
                    logging.info(f'保存config--保存配置文件成功，但是0行受到影响')
                    cur.close()
                    return None
                else:
                    logging.info(f'保存config--保存配置文件成功')
                    cur.close()
                    return True
            except Exception as e:
                logging.warning(f'保存config--保存配置文件失败，失败原因为{e}')
                return False
        else:
            logging.warning(f'保存config--保存配置文件失败，连接中断')
            return 'Unconnect'
if __name__  == '__main__':
    file = 'config.db'
    A = BaseDBfunc(file)
    # a = A.InsertDefaultprogressinfo()
    a = A.DeleteDefaultconfTB()

    c = A.InsertDefaultdfconf()
    # c = A.InsertDefaultConfig()

    print(c, type(c))