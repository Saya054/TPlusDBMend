from DataDrivers import  TsDBdriver
import basicFunc
import FileFunctions
import CheckXML
import os,logging
from baseDBFunc import BaseDBfunc
'''
为导表修复写的基础修复功能
'''
# 校验数据库连接
def DBCon(hst,usr,pwd,driver,dbN):
    con = TsDBdriver(hst,usr,pwd,driver,dbN).SQLcon()
    if con:
        return True
    else:
        return False
# 检测数据库模式下数据库名字是否都选择了
def DBNameExist(brkdb,oridb,bakdb):
    Dbcheck = basicFunc.Existdata(brkdb) and basicFunc.Existdata(oridb) and basicFunc.Existdata(bakdb)
    if Dbcheck == False:
        return False
    else:
        return True
# 检查数据库名字是否重复
def DBNameRepeat(brkdb,oridb,bakdb):
    if brkdb == oridb or brkdb == bakdb or  oridb==bakdb:
        return False
    else:
        return True
# 检验数据库模式下几个数据库是否能够直接连接
def DBNameCon(hst,usr,pwd,driver,brkdb,oridb,bakdb):
    brkCon = TsDBdriver(hst,usr,pwd,driver,brkdb).SQLcon()
    oriCon = TsDBdriver(hst,usr,pwd,driver,oridb).SQLcon()
    bakCon = TsDBdriver(hst,usr,pwd,driver,bakdb).SQLcon()
    Conres = brkCon and oriCon and bakCon
    if not Conres:
        return False
    else:
        return True
# 校验数据库名字是否能连接上
# 比对数据库版本
def DBVersionCompare(hst,usr,pwd,driver,dbN,brkdb,oridb,bakdb):
    try:
        brkcon = TsDBdriver(hst,usr,pwd,driver,dbN)
        brkVer = brkcon.VersionDB(brkdb)
        oricon = TsDBdriver(hst,usr,pwd,driver,dbN)
        oriVer = oricon.VersionDB(oridb)
        bakcon = TsDBdriver(hst,usr,pwd,driver,dbN)
        bakVer = bakcon.VersionDB(bakdb)
        if (brkVer != 'Unconnect' and brkVer != False) and (oriVer != 'Unconnect' and oriVer != False) and (bakVer != 'Unconnect' and bakVer != False):
            if brkVer != oriVer:
                return False
            elif brkVer != bakVer:
                return False
            else:
                return True
    except:
        return False
# 清除冗余数据
def EapRepair(hst,usr,pwd,driver,dbN,brkdb,oridb):
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Eapclear = con.ClearBKtb(oridb)
    except Exception as e:
        return  False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        EapIDadd = con.EapIDadd(brkdb)
    except Exception as e:
        return  False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        SetOnline = con.setOnline(brkdb)
    except Exception as e:
        return  False
    return True
# 检测坏表
def CheckBKDB(hst,usr,pwd,driver,dbN,brkdb):
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Alltablelist = con.Checktb(brkdb)
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        testdb = con.TestDb()
        if testdb == 'Unconnect':
            return False
        else:
            pass
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Sqllist = con.QuerySQL(brkdb, Alltablelist)
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Errorlist = con.ErrorTB(Sqllist)
        if len(Errorlist) == 0:
            return '[]'
        else:
            return Errorlist
    except Exception as e:
        print('cccc',e)
        return False
# 删除测试用空库
def DelTestDB(hst, usr, pwd, driver,dbN):
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        deldb = con.DelDB()
        if deldb == 'Unconnect':
            return False
    except Exception as e:
        return False
# 空账解体
def DisAsseDB(hst,usr,pwd,driver,dbN,oridb):
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Dconstrsave = con.DefauConsave(oridb)
        print('Dconstrsave')
        if Dconstrsave == 'Unconnect':
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Constrsave = con.Consave(oridb)
        print('Constrsave')
        if Constrsave == 'Unconnect':
            print('错误1')
            return False
    except Exception as e:
        print('错误2',e)
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Indexsave = con.IndexSave(oridb)
        print('Indexsave')
        if Indexsave == 'Unconnect':
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        DeleteAll = con.DelConIndTab(oridb)
        print('DeleteAll')
        if DeleteAll == 'Unconnect':
            return False
    except Exception as e:
        return False
    return True
#空账插入数据
def InSertDB(hst,usr,pwd,driver,dbN,oridb,brkdb,bakdb,ErrorList):
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        # 这里其实是所有的表，而没有排除坏表
        ALLlist = con.Checktb(brkdb)
        OKlist = list(set(ALLlist) - set(ErrorList))
        logging.info('OKlist')
        if ALLlist == 'Unconnect':
            logging.info('导入空账，Allist')
            return False
    except Exception as e:
        logging.info('导入空账，卡住步骤1',e)
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Insertb = con.GetINsertTBN(brkdb, ErrorList)
        logging.info('Insertb')
        if Insertb == 'Unconnect':
            logging.info('导入空账，Insertb')
            return False
    except Exception as e:
        logging.info('导入空账，卡住步骤2',e)
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        SQLlist = con.CreateINSQL(OKlist, ErrorList, brkdb, bakdb)
        logging.info('SQLlist')
        if SQLlist == 'Unconnect':
            logging.info('导入空账，SQLlist')
            return False
    except Exception as e:
        logging.info('导入空账，卡住步骤3',e)
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Insert = con.InsertSQL(oridb, SQLlist)
        logging.info('Insert')
        if Insert == 'Unconnect':
            logging.info('导入空账，Insert')
            return False
        elif len(Insert) > 0:
            logging.info('导入空账，len(Insert)')
            return False
    except Exception as e:
        logging.info('导入空账，卡住步骤4', e)
        return False
    return True
# 重建数据库结构
def RebuildDB(hst,  usr, pwd,driver,dbN, oridb):
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        DefaultSQLlist = con.RebuildDefaultSQL(oridb)
        logging.info('DefaultSQLlist')
        if DefaultSQLlist == 'Unconnect':
            print()
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        RebuildDefault = con.RebuildDCons( oridb,DefaultSQLlist)
        logging.info('RebuildDefault')
        if RebuildDefault == 'Unconnect':
            return False
        elif len(RebuildDefault)>0:
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        IndexSQLlist = con.RebuildInxSQL( oridb)
        logging.info('IndexSQLlist')
        if IndexSQLlist == 'Unconnect':
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        RebuildIndex = con.RebuildInx(oridb,IndexSQLlist)
        logging.info('RebuildIndex')
        if RebuildIndex == 'Unconnect':
            return False
        elif len(RebuildIndex)>0:
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        ConstrSQLlist = con.RebuildConsSQL( oridb)
        logging.info('ConstrSQLlist')
        if ConstrSQLlist == 'Unconnect':
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        RebuildConstr = con.RebuildCons( oridb,ConstrSQLlist)
        logging.info('RebuildConstr')
        if RebuildConstr == 'Unconnect':
            print('重建约束报错1')
            return False
        elif len(RebuildConstr) >0:
            print('重建约束报错2')
            return False
    except Exception as e:
        print('重建约束报错3',e)
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Enddate = con.Enddate(oridb)
        logging.info('Enddate')
        if Enddate == 'Unconnect':
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        FlashOpen = con.FlashOpen(oridb)
        logging.info('FlashOpen')
        if FlashOpen == 'Unconnect':
            return False
    except Exception as e:
        return False
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        FlashSeparate = con.FlashSeparate(oridb)
        logging.info('FlashSeparate')
        if FlashSeparate == 'Unconnect':
            return False
    except Exception as e:
        return False
    return True
# ZIP模式的修复功能
def ZipFileExist(file1,file2,file3):
    res1 = FileFunctions.Existfiles(file1)
    res2 = FileFunctions.Existfiles(file2)
    res3 = FileFunctions.Existfiles(file3)
    if res1 and res2 and res3:
        return True
    else:
        return False
# ZIP模式下解压并比对数据版本
def ZipExCompareVersion(brkfile,orifile,bakfile):
#        检验ZIP包是否是T+的格式
    logging.info('*开始解压并比对版本')
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    filename =  'AdditionalXml.xml'
    brkzipfile = FileFunctions.Repath(baseconfig.getDefaultConfig('brokesavepath'))
    orizipfile = FileFunctions.Repath(baseconfig.getDefaultConfig('originsavepath'))
    bakzipfile = FileFunctions.Repath(baseconfig.getDefaultConfig( 'sparesavepath'))
    logging.info('*开始读取zip结构')
    try:
        # logging.info('开始读取zip包内文件')
        RBdbNL = basicFunc.getzipfilename(brkfile)
        ROdbNL = basicFunc.getzipfilename(orifile)
        RSdbNL = basicFunc.getzipfilename(bakfile)
        RBdbN = list(set(RBdbNL) - set([filename]))[0]
        ROdbN = list(set(ROdbNL) - set([filename]))[0]
        RSdbN = list(set(RSdbNL) - set([filename]))[0]
        logging.info('*读取zip结构成功')
    except Exception as e:
        logging.error('*读取zip结构失败，zip非T+备份，或无法解压')
        mes = 'zip包不是正常的T+备份文件、缺失了xml文件或备份本体'
        return [False, mes]
    # 解压文件
    logging.info('*开始解压zip')
    try:
        zip1 = basicFunc.unzip_file(brkfile, brkzipfile)
        print(f'zip1 = basicFunc.unzip_file({brkfile}, {brkzipfile})')
        zip2 = basicFunc.unzip_file(orifile, orizipfile)
        print(f'zip1 = basicFunc.unzip_file({orifile}, {orizipfile})')
        zip3 = basicFunc.unzip_file(bakfile, bakzipfile)
        print(f'zip1 = basicFunc.unzip_file({bakfile}, {bakzipfile})')
        # logging.info('step1 zip complete')
        logging.info('*解压zip成功')
    except Exception as e:
        logging.error(f'*解压zip失败，失败原因为：{e}')
        # logging.error(f'step1 zip failed,error:{str(e)}')
        mes = '解压失败：'+ str(e)
        return [False,mes]
#     比对xml文件
#     logging.info('step2 start')
    logging.info('*开始比对XML文件')
    try:
        VersionData1 = CheckXML.getData(brkzipfile, filename, 'Version')
        VersionData2 = CheckXML.getData(orizipfile, filename, 'Version')
        VersionData3 = CheckXML.getData(bakzipfile, filename, 'Version')
        VerNumData1 = CheckXML.getData(brkzipfile, filename, 'VersionNum')
        VerNumData2 = CheckXML.getData(orizipfile, filename, 'VersionNum')
        VerNumData3 = CheckXML.getData(bakzipfile, filename, 'VersionNum')
        DBverData1_base = CheckXML.getData(brkzipfile, filename, 'DBVersionNo')
        DBverData2_base = CheckXML.getData(orizipfile, filename, 'DBVersionNo')
        DBverData3_base = CheckXML.getData(bakzipfile, filename, 'DBVersionNo')
        DBnumData1 = CheckXML.DBVresign(DBverData1_base)
        DBnumData2 = CheckXML.DBVresign(DBverData2_base)
        DBnumData3 = CheckXML.DBVresign(DBverData3_base)
        res1 = (VersionData1 == VersionData2 and VersionData1 == VersionData3)
        res2 = (VerNumData1 == VerNumData2 and VerNumData1 == VerNumData3)
        res3 = (DBnumData1 == DBnumData2 and DBnumData1 == DBnumData3)
        if not (res1 and res2 and res3):
            # logging.error('step2 failed1')
            mes = '坏账、空账、备用账套的环境不一致'
            logging.warning('*比对结束，坏账、空账、备用账套的环境不一致')
            return [False,mes]
        else:
            logging.info('*比对结束，坏账、空账、备用账套的环境完全一致')
            # logging.info('step2 complete')
            return [True,'OK']
    except Exception as e:
        logging.error(f'*比对失败，失败原因为:{e}')
        # logging.error('step2 failed')
        mes = '读取版本信息失败'
        return [False,mes]
    logging.info('*解压并比对版本通过')
# zip的解压数据恢复数据
def ZipRestore(brkfile,orifile,bakfile,hst, usr,pwd,driver,dbN):
    # 先删除数据库
    # logging.info('step3 start')
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    BdbN = baseconfig.getDefaultConfig('brokename')
    OdbN = baseconfig.getDefaultConfig('originame')
    SdbN = baseconfig.getDefaultConfig('sparename')
    Bfilename = baseconfig.getDefaultConfig('brokesavepath')
    Ofilename = baseconfig.getDefaultConfig('originsavepath')
    Sfilename = baseconfig.getDefaultConfig('sparesavepath')
    Blogicfile = os.path.abspath(baseconfig.getDefaultConfig('brokelogicpath'))
    Ologicfile = os.path.abspath(baseconfig.getDefaultConfig('originlogicpath'))
    Slogicfile =os.path.abspath(baseconfig.getDefaultConfig('sparelogicpath'))
    Blogicmdf =  Blogicfile + '\\' + BdbN +'.mdf'
    Blogicldf =  Blogicfile + '\\' + BdbN +'.ldf'
    Ologicmdf = Ologicfile + '\\' + OdbN + '.mdf'
    Ologicldf = Ologicfile + '\\' + OdbN + '.ldf'
    Slogicmdf = Slogicfile + '\\' + SdbN + '.mdf'
    Slogicldf = Slogicfile + '\\' + SdbN + '.ldf'
    con = con = TsDBdriver(hst, usr, pwd,driver, dbN)
    E1 =  con.ExistcheckDb(BdbN)
    E2 =  con.ExistcheckDb(OdbN)
    E3 =  con.ExistcheckDb(SdbN)
    filename = 'AdditionalXml.xml'
    RBdbNL = basicFunc.getzipfilename(brkfile)
    ROdbNL = basicFunc.getzipfilename(orifile)
    RSdbNL = basicFunc.getzipfilename(bakfile)
    RBdbN = list(set(RBdbNL) - set([filename]))[0]
    ROdbN = list(set(ROdbNL) - set([filename]))[0]
    RSdbN = list(set(RSdbNL) - set([filename]))[0]
    BRfilename = os.path.abspath(Bfilename)+'\\'+RBdbN
    ORfilename = os.path.abspath(Ofilename)+'\\'+ROdbN
    SRfilename = os.path.abspath(Sfilename)+'\\'+RSdbN
    Blogiclist = [Blogicmdf, Blogicldf]
    Ologiclist = [Ologicmdf, Ologicldf]
    Slogiclist = [Slogicmdf, Slogicldf]
    if E1 != [[]]:
        # logging.info('step3 Bdb exist')
        try:
            # con = DbFunction.DBRepairserver(hst,  usr, pwd, dbN)
            D1 = con.DeleteDB(BdbN)
            # logging.info('step3 Bdb delete complete')
        except:
            # logging.error('step3 Bdb delete failed')
            return [False,'坏账数据库清理失败']
    if E2!= [[]]:
        # logging.info('step3 Odb exist')
        try:
            # con = DbFunction.DBRepairserver(hst,  usr, pwd, dbN)
            D2 = con.DeleteDB(OdbN)
            # logging.info('step3 Odb delete complete')
        except:
            # logging.error('step3 Odb delete failed')
            return [False,'空账数据库清理失败']
    if E3!= [[]]:
        # logging.info('step3 Sdb exist')
        try:
            # con = DbFunction.DBRepairserver(hst,  usr, pwd, dbN)
            D3 = con.DeleteDB(SdbN)
            # logging.info('step3 Sdb delete complete')
        except:
            # logging.error('step3 Sdb delete failed')
            return [False,'备用账套数据库清理失败']
    # 再恢复
    #得到原始数据库物理文件路径
    # logging.info('step3 logicfile get start')
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Logiclist1 = con.LogicalData(RBdbN,Bfilename)
        Logiclist2 = con.LogicalData(ROdbN,Ofilename)
        Logiclist3 = con.LogicalData(RSdbN,Sfilename)
    except Exception as e:
        print(e)
        return [False,'获取原始物理文件位置失败']
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        Restore1 = con.RestoreDB(BRfilename,BdbN,Logiclist1,Blogiclist)
        Restore2 = con.RestoreDB(ORfilename,OdbN,Logiclist2,Ologiclist)
        Restore3 = con.RestoreDB(SRfilename,SdbN,Logiclist3,Slogiclist)
    except Exception as e:
        return [False,'恢复数据失败']
    return [True,'恢复成功']
#  xml拷贝\origin备份\打包到zip包里,再移动到对应文件夹.
def ZipRecompact(hst,usr,pwd,driver,dbN,brkfile):
    logging.info('*开始重新打包修复后的备份')
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    #先拷贝xml文件
    oriname = baseconfig.getDefaultConfig('originame')
    bksfile =  baseconfig.getDefaultConfig('brokesavepath')
    rprfile =  baseconfig.getDefaultConfig('repairsavepath')
    rRprfile = os.path.abspath(rprfile)
    rbroFilename = FileFunctions.getFilename(brkfile)
    filename = 'AdditionalXml.xml'
    logging.info('*重新打包-开始打包xml文件')
    try:
        Trans1 = FileFunctions.transform(bksfile,filename,rprfile,filename)
        logging.info('*重新打包-xml文件打包成功')
    except Exception as e:
        logging.error(f'*重新打包-xml文件打包失败，失败原因为：{e}')
        return False
    #备份数据库到新文件夹中，并以老名字命名
    logging.info('*重新打包-打包备份文件')
    try:
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        BackupDB = con.BackupDB(oriname,rRprfile,rbroFilename)
        if BackupDB == 'Unconnect':
            logging.warning('*重新打包-打包备份文件途中，数据库连接中断')
            return False
        logging.info('*重新打包-打包备份文件成功')
    except Exception as e:
        logging.error(f'*重新打包-打包备份文件失败，失败原因为：{e}')
        return False
    # 打包
    logging.info('*重新打包-重新压缩')
    try:
        REzip = basicFunc.zip_file(rprfile)
        logging.info('*重新打包-重新压缩成功')
    except Exception as e:
        logging.error(f'*重新打包-重新压缩失败，失败原因为：{e}')
        return False
    # 重命名并移动到对应的文件夹下
    logging.info('*重新打包-重命名并移动到OKzip下')
    try:
        OKfile = './Data/OKzip'
        parentpath = FileFunctions.getparentpath(rprfile)
        newfilename = rprfile.split('/')[-1] +'.zip'
        repairedname = rbroFilename+'(repaired).zip'
        Trans2 = FileFunctions.transform(parentpath,newfilename,OKfile,repairedname)
        logging.info('*重新打包-重命名并移动到OKzip下成功')
    except Exception as e:
        logging.error(f'*重新打包-重命名并移动到OKzip下失败，失败原因为：{e}')
        return False
    # 把zip包移动到OKzip目录后，自动删掉repaired文件夹下的东西
    logging.info('*重新打包-删除多余的数据')
    try:
        Deldata = FileFunctions.del_file(rprfile)
        logging.info('*重新打包-删除多余的数据成功')
    except Exception as e:
        logging.error(f'*重新打包-删除多余的数据失败，失败原因为：{e}')
        return False
    logging.info('*重新打包修复后的备份成功')
    return True
# 清除数据库冗余
def ClearData(hst,usr, pwd,driver,dbN):
    logging.info('*开始zip模式下，清除冗余数据')
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
#     删除数据库
    bksfile =baseconfig.getDefaultConfig('brokesavepath')
    orifile = baseconfig.getDefaultConfig('originsavepath')
    sprfile = baseconfig.getDefaultConfig('sparesavepath')
    brkdb = baseconfig.getDefaultConfig('brokename')
    oridb = baseconfig.getDefaultConfig('originame')
    bakdb = baseconfig.getDefaultConfig('sparename')
    bklogicfile = baseconfig.getDefaultConfig('brokelogicpath')
    orlogicfile = baseconfig.getDefaultConfig('originlogicpath')
    splogicfile = baseconfig.getDefaultConfig('sparelogicpath')
    try:
        logging.info('*开始删除数据库')
        con = TsDBdriver(hst, usr, pwd,driver, dbN)
        delDB1 = con.DeleteDB(brkdb)
        delDB2 = con.DeleteDB(oridb)
        delDB3 = con.DeleteDB(bakdb)
        if delDB1 == 'Unconnect' or  delDB2 == 'Unconnect' or  delDB3 == 'Unconnect':
            logging.warning('*删除数据库失败（数据库连接中断）')
            return False
    except Exception as e:
        logging.error(f'*删除数据库失败，失败原因为{e}')
        return False
#     删除文件
    logging.info('*开始删除文件目录')
    try:
        remove1 = FileFunctions.removefile(bksfile)
        remove2 = FileFunctions.removefile(orifile)
        remove2 = FileFunctions.removefile(sprfile)
        logging.info('*删除文件目录成功')
    except Exception as e:
        logging.error(f'*删除文件目录失败，失败原因为{e}')
        return False
    logging.info('*开始创建zip包保存目录')
    try:
        newdir1 = FileFunctions.mkdir(bksfile)
        newdir2 = FileFunctions.mkdir(orifile)
        newdir3 = FileFunctions.mkdir(sprfile)
        logging.info('*创建zip包保存目录成功')
    except Exception as e:
        logging.error(f'*创建zip包保存目录失败，失败原因为{e}')
        return False
    logging.info('*开始创建物理文件目录')
    try:
        newlogicdir1 = FileFunctions.mkdir(bklogicfile)
        newlogicdir2 = FileFunctions.mkdir(orlogicfile)
        newlogicdir3 = FileFunctions.mkdir(splogicfile)
        logging.info('*创建物理文件目录成功')
    except Exception as e:
        logging.error(f'*创建物理文件目录成功，失败原因为{e}')
        return False
    logging.info('*zip模式下，清除冗余数据成功')
    return True

if __name__ == '__main__':
    brkfile = 'G:/test/培训测试/264117.zip'
    orifile = 'G:/test/培训测试/264117（1）.zip'
    bakfile = 'G:/test/培训测试/264117（1）.zip'
    hst = '.'
    usr = 'sa'
    pwd = '123'
    driver = '{ODBC Driver 18 for SQL Server}'
    driver = 'pymssql driver'
    dbN = 'master'
    a = ZipRestore(brkfile, orifile, bakfile, hst, usr, pwd, driver, dbN)
    print(a)