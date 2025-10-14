from .RepairFunc import *
from .basicFunc import WriteProcess,getConfig
from .baseDBFunc import BaseDBfunc
from .DataDrivers import TsDBdriver
import logging,time
'''
获取所有表
'''
def getAlllist(hst,usr,pwd,driver,dbN,brkdb):
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        # 这里其实是所有的表，而没有排除坏表
        ALLlist = con.Checktb(brkdb)
        if ALLlist == 'Unconnect':
            return []
        else:
            return ALLlist
    except Exception as e:
        return []

'''
数据库模式的修复功能
'''
# 修复前的校验
def PreDBrepair(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb):
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
# 校验数据库连接是否通过step1
    logging.info('修复前校验开始...')
    logging.info('修复前校验-数据库连接校验开始...')
    time.sleep(1)
    baseconfig.WriteProgress('5','0','校验数据库连接')
    step1 = DBCon(hst,usr,pwd,driver,dbN)
    if not step1:
        baseconfig.WriteProgress('0', '-1', '校验失败：数据库连接不通过')
        logging.warning('修复前校验-数据库连接校验失败')
        return [False,'Error1']
    else:
        # 校验所有的数据库是否都选择了step2
        logging.info('修复前校验-数据库连接校验成功')
        logging.info('修复前校验-数据是否全部选择校验...')
        time.sleep(1)
        baseconfig.WriteProgress('10', '0', '修复前校验-数据是否全部选择校验...')
        step2 = DBNameExist(brkdb,oridb,bakdb)
        if step2 == False:
            baseconfig.WriteProgress('0', '-1', '校验失败：有数据未选择')
            logging.warning('修复前校验-数据是否全部选择校验失败')
            return [False,'Error2']
        else:
            # 校验是否重名step3
            logging.info('修复前校验-数据是否全部选择校验通过')
            logging.info('修复前校验-数据库重名校验...')
            time.sleep(1)
            baseconfig.WriteProgress('20', '0', '校验数据库是否重名')
            step3 = DBNameRepeat(brkdb,oridb,bakdb)
            if step3 == False:
                baseconfig.WriteProgress('0', '-1', '校验失败：存在同名数据库')
                logging.warning('修复前校验-数据库重名校验失败')
                return [False, 'Error3']
            else:
                logging.info('修复前校验-数据库重名校验通过')
                logging.info('修复前校验-所选数据库是否连接校验...')
                # 校验数据库名字是否能连接上step4
                time.sleep(1)
                baseconfig.WriteProgress('30', '0', '校验数据库是否都能连接')
                step4 =  DBNameCon(hst,usr,pwd,driver,brkdb,oridb,bakdb)
                if not step4:
                    baseconfig.WriteProgress('0', '-1', '校验失败：有数据库无法连接')
                    logging.warning('修复前校验-数据库重名校验失败')
                    return [False,'Error4']
                else:
                    time.sleep(1)
                    baseconfig.WriteProgress('40', '0', '校验数据成功')
                    logging.info('修复前校验-数据库重名校验成功')
                    logging.info('修复前校验全部通过')
                    return [True,'PreFinish']
# 获取损坏的表
def NowDBRepair(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb):
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    #比对版本
    logging.info('获取损坏表步骤开始...')
    logging.info('获取损坏表-比对数据库补丁版本号...')
    time.sleep(1)
    baseconfig.WriteProgress('45', '0', '比对数据库补丁版本号')
    step1 = DBVersionCompare(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb)
    if not step1:
        logging.warning('获取损坏表-比对数据库补丁版本号不通过')
        baseconfig.WriteProgress('0', '-1', '比对数据库失败：补丁号不一致')
        return [False,'Error5']
    else:
        # 清除Eap表信息
        logging.info('获取损坏表-比对数据库补丁版本号通过')
        logging.info('获取损坏表-清除Eap表残留信息...')
        time.sleep(1)
        baseconfig.WriteProgress('50', '0', '清除Eap表残留信息')
        step2 = EapRepair(hst,usr,pwd,driver,dbN,brkdb,oridb)
        if not step2:
            baseconfig.WriteProgress('0', '-1', 'Eap表信息清除失败')
            logging.warning('获取损坏表-清除Eap表残留信息失败')
            return [False,'Error6']
        else:
            # 检查坏表
            logging.info('获取损坏表-清除Eap表残留信息成功')
            logging.info('获取损坏表-检测损坏的表名...')
            time.sleep(1)
            baseconfig.WriteProgress('60', '0', '检测损坏的表名')
            step3 = CheckBKDB(hst,usr,pwd,driver,dbN,brkdb)
            if not step3:
                logging.warning('获取损坏表-检测损坏的表名失败')
                baseconfig.WriteProgress('0', '-1', '检测损坏的表名失败')
                return  [False,'Error7']
            else:
                logging.info('获取损坏表-检测损坏的表名成功')
                logging.info('获取损坏表全部完成')
                time.sleep(1)
                baseconfig.WriteProgress('70', '0', '成功获取损坏表名')
                # 删除testdb
                step4 = DelTestDB(hst, usr, pwd, driver,dbN)
                return [True,step3]
# 修复前+损坏表的合并流程
def UnionDBRepair(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb):
    # 开始修复（校验数据）
    processFst = PreDBrepair(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb)
    if processFst[0] == False:
        MesF = ErrorMes(processFst[1])
        return [False,MesF]
    else:
        # 获取坏表
        processScd = NowDBRepair(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb)
        if processScd[0] == False:
            MesS = ErrorMes(processScd[1])
            return [False,MesS]
        else:
            return [True,processScd[1]]
# 开始数据修复
def AfterDBRepair(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb,ErrorList,Repairmode):
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    # 解体空账
    logging.info('后续修复流程开始...')
    logging.info('后续修复-空账解体开始...')
    time.sleep(1)
    baseconfig.WriteProgress('75', '0', '空账解体开始')
    step1 = DisAsseDB(hst,usr,pwd,driver,dbN,oridb)
    if not step1:
        logging.warning('后续修复-空账解体失败')
        baseconfig.WriteProgress('0', '-1', '空账解体失败')
        return [False, 'Error8']
    else:
        # 导入数据
        logging.info('后续修复-空账解体完成')
        logging.info('后续修复-向空账导入数据...')
        time.sleep(1)
        baseconfig.WriteProgress('80', '0', '向空账导入数据')
        step2 = InSertDB(hst,usr,pwd,driver,dbN,oridb,brkdb,bakdb,ErrorList)
        if not step2:
            logging.warning('后续修复-向空账导入数据失败')
            baseconfig.WriteProgress('0', '-1', '向空账导入数据失败')
            return [False, 'Error9']
        else:
            logging.info('后续修复-向空账导入数据成功')
            logging.info('后续修复-重建数据库结构...')
            time.sleep(1)
            baseconfig.WriteProgress('85', '0', '重建数据库结构')
            # 重建结构
            step3 =  RebuildDB(hst, usr, pwd,driver,dbN, oridb)
            if not step3:
                logging.warning('后续修复-重建数据库结构失败')
                baseconfig.WriteProgress('0', '-1', '重建数据库结构失败')
                return [False, 'Error10']
            else:
                time.sleep(1)
                baseconfig.WriteProgress('90', '0', '重建数据库结构成功')
                logging.info('后续修复-重建数据库结构成功')
                logging.info('后续修复完成')
                time.sleep(1)
                if Repairmode == 'DBmode':
                    baseconfig.WriteProgress('100', '1', '修复完成')
                    return [True,'AfterFinish']
                else:
                    return [True,'AfterFinish']
'''  
ZIP模式的修复功能
'''
# zip包的前期修复校验
def PreZipRepair(hst,usr,pwd,driver,dbN,brkfile,orifile,bakfile):
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    logging.info('修复前校验开始...')
    logging.info('修复前校验-数据库连接校验开始...')
    # 校验数据库连接是否通过step1
    time.sleep(1)
    baseconfig.WriteProgress('5', '0', '校验数据库连接')
    step1 = DBCon(hst, usr, pwd,driver, dbN)
    if not step1:
        logging.warning('修复前校验-数据库连接校验不通过.')
        baseconfig.WriteProgress('0', '-1', '校验失败：数据库连接不通过')
        return [False,'Error1']
    else:
        logging.info('修复前校验-数据库连接校验通过')
        logging.info('修复前校验-账套是否选择校验开始...')
        # 校验所有的数据库是否都选择了
        time.sleep(1)
        baseconfig.WriteProgress('10', '0', '校验空账、坏账、备用账套路径是否选择了')
        step2  = ZipFileExist(brkfile,orifile,bakfile)
        if not step2:
            logging.warning('修复前校验-账套是否选择校验失败')
            baseconfig.WriteProgress('0', '-1', '校验失败：对应路径的账套zip不存在\n或者空账、坏账、备用账套没有选择')
            return [False, 'Error11']
        #将数据都解压到对应位置并且去恢复
        else:
            logging.info('修复前校验-账套是否选择校验通过')
            logging.info('修复前校验-解压并比对版本号...')
            time.sleep(1)
            baseconfig.WriteProgress('20', '0', '开始解压，并比对版本')
            step3 = ZipExCompareVersion(brkfile,orifile,bakfile)
            if step3[0] != True:
                logging.warning('修复前校验-解压并比对版本号不通过')
                mes = step3[1]
                baseconfig.WriteProgress('0', '-1', '解压、比对版本失败')
                return [False,'Error12']
            else:
                time.sleep(1)
                baseconfig.WriteProgress('25', '0', '解压、比对版本成功')
                logging.info('修复前校验-解压并比对版本号通过')
                logging.info('修复前校验全部完成')
                return [True,'PreFinish']
# 开始恢复数据并获取坏表
def NowZipRepair(hst, usr, pwd,driver,dbN,brkfile,orifile,bakfile):
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    logging.info('获取损坏表步骤开始...')
    logging.info('获取损坏表-恢复数据开始...')
    time.sleep(1)
    baseconfig.WriteProgress('30', '0', '开始恢复数据')
    step1 = ZipRestore(brkfile,orifile,bakfile,hst,  usr, pwd,driver,dbN)
    brkdb = baseconfig.getDefaultConfig('brokename')
    oridb = baseconfig.getDefaultConfig('originame')
    if step1[0] != True:
        logging.warning('获取损坏表-恢复数据失败')
        mes = step1[1]
        baseconfig.WriteProgress('0', '-1', '恢复数据失败')
        return [False,'Error13']
    else:
        logging.info('获取损坏表-恢复数据成功')
        logging.info('获取损坏表-清除Eap表残留信息...')
        time.sleep(1)
        baseconfig.WriteProgress('40', '0', '清除Eap表残留信息')
        step2 = EapRepair(hst,usr,pwd,driver,dbN,brkdb,oridb)
        if not step2:
            logging.warning('获取损坏表-清除Eap表残留信息失败')
            baseconfig.WriteProgress('0', '-1', 'Eap表信息清除失败')
            return [False, 'Error6']
        else:
            # 检查坏表
            logging.info('获取损坏表-清除Eap表残留信息成功')
            logging.info('获取损坏表-检测损坏的表名...')
            time.sleep(1)
            baseconfig.WriteProgress('50', '0', '检测损坏的表名')
            step3 = CheckBKDB(hst,usr,pwd,driver,dbN,brkdb)
            if not step3:
                logging.warning('获取损坏表-检测损坏的表名失败')
                baseconfig.WriteProgress('0', '-1', '检测损坏的表名失败')
                return [False, 'Error7']
            else:
                logging.info('获取损坏表-检测损坏的表名成功')
                logging.info('获取损坏表全部完成')
                time.sleep(1)
                baseconfig.WriteProgress('60', '0', '成功获取损坏表名')
                step4 = DelTestDB(hst, usr, pwd, driver,dbN)
                return [True, step3]
# 前期校验+恢复+检测坏表
def UnionZipRepair(hst,usr, pwd,driver,dbN,brkfile,orifile,bakfile):
    # 开始修复
    processFst = PreZipRepair(hst,usr,pwd,driver,dbN,brkfile,orifile,bakfile)
    if processFst[0] == False:
        MesF = ErrorMes(processFst[1])
        return [False, MesF]
    else:
        processScd = NowZipRepair(hst,usr, pwd,driver, dbN,brkfile,orifile,bakfile)
        if processScd[0] == False:
            MesS = ErrorMes(processScd[1])
            return [False, MesS]
        else:
            return [True, processScd[1]]
# 后续打包
def AfterZipPack(hst, usr, pwd,driver,dbN,brkfile,ErrorList,clearmode,Repairmode):
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    logging.info('后续修复流程开始...')
    logging.info('后续修复-开始数据库后续修复模式...')
    time.sleep(1)
    baseconfig.WriteProgress('65', '0', '开始数据库修复模式')
    brkdb = baseconfig.getDefaultConfig('brokename')
    oridb = baseconfig.getDefaultConfig('originame')
    bakdb = baseconfig.getDefaultConfig('sparename')
    step1 = AfterDBRepair(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb,ErrorList,Repairmode)
    if step1[0] != True:
        logging.warning('后续修复-开始数据库后续修复模式失败')
        mes = ErrorMes(step1[1])
        baseconfig.WriteProgress('0', '-1', '数据导表失败')
        return [False,mes]
    else:
        logging.info('后续修复-开始数据库后续修复模式完成')
        logging.info('后续修复-账套重新打包...')
        time.sleep(1)
        baseconfig.WriteProgress('92', '0', '账套重新打包')
        step2 = ZipRecompact(hst,usr,pwd,driver,dbN,brkfile)
        if step2 == False:
            logging.warning('后续修复-账套重新打包失败')
            mes = '账套打包失败,请自行打包数据\n修复后的数据是数据库[origin]'
            baseconfig.WriteProgress('0', '-1', 'mes')
            return [False, mes]
        else:
            logging.info('后续修复-打包后冗余模式判断')
            logging.info('后续修复-清除冗余模式开启...')
            time.sleep(1)
            baseconfig.WriteProgress('95', '0', '清除冗余数据')
            step4 = ClearData(hst,  usr, pwd,driver,dbN)
            time.sleep(1)
            baseconfig.WriteProgress('100', '1', '修复结束')
            return [True,'After-Finish']

'''
根据错误码显示报错内容
'''
def ErrorMes(Error):
    if Error == 'Error1':
        mes1 = '数据库连接失败：请检查\n1、实例名、用户名、密码是否错误\n2、Tcp\Ip协议是否开启'
        return mes1
    elif Error =='Error2':
        mes2 = '有数据库未选择：\n请检查坏账、空账、\n备用账套数据库是否选择！'
        return mes2
    elif Error =='Error3':
        mes3 = '有数据库选择重复：\n请检查坏账、空账、备用账套\n数据库是否选择重复了！\n（三者不能同名）'
        return mes3
    elif Error =='Error4':
        mes4 = '数据无法访问：\n请检查空账、坏账、备用账套\n的数据库是否质疑！'
        return mes4
    elif Error =='Error5':
        mes5 = '补丁版本号不一致:\n请检查空账、坏账、备用账套\n的补丁号是否一致！'
        return mes5
    elif Error =='Error6':
        mes6 = '清除Eap表失败：\n1、请检查空账备份\n是否也存在损坏问题（小助手检查）\n2、请检查坏账备份是否无法访问'
        return mes6
    elif Error =='Error7':
        mes7 = '检查损坏表失败：\n请检查坏账备份是否无法访问\n(双击对应数据库无法展开\n表名字的列表)'
        return mes7
    elif Error =='Error8':
        mes8 = '空账解体失败：\n请检查空账是否存在损坏！'
        return mes8
    elif Error =='Error9':
        mes9 = '插入数据失败,请检查：\n1、是否空账备份损坏\n2、是否备用账套损坏'
        return mes9
    elif Error =='Error10':
        mes10 ='结构重建失败：\n请查看日志判断原因！'
        return mes10
    elif Error == 'Error11':
        mes11 = '有路径错误：\n空账、坏账、备用账套未选择\n或者选择的路径不存在对应文件'
        return mes11
    elif Error == 'Error12':
        mes12 = '解压、比对版本不通过：\n1、所选账套的zip无法解压\n2、所选账套的zip不是xml+备份文件\n的组合方式\n3、账套之间的环境不一致\n(数据库版本、补丁号、T+版本）'
        return mes12
    elif Error == 'Error13':
        mes13  = '数据库恢复失败：\n1、zip包下的数据备份损坏严重\n2、数据库中存在同名数据库\n或者物理文件被占用'
        return mes13
    else:
        mes = '未知错误！！'
        return mes


if __name__ =='__main__':
    # hst = '127.0.0.1'
    # usr = 'sa'
    # pwd = '123'
    # driver = '{ODBC Driver 18 for SQL Server}'
    # # driver = '{SQL Server}'
    # # driver = 'pymssql driver'
    #
    # dbN = 'master'
    # brkdb = 'broken'
    # oridb = 'origin'
    # bakdb = 'origin1'
    #
    # a = UnionDBRepair(hst, usr, pwd, driver, dbN, brkdb, oridb, bakdb)
    # print(a)

    a = os.path.abspath('./Data')
    print(a)