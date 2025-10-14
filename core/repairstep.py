import dbfunc
import CheckXML
import zippack
import baseFunc
import repairfunc
import re
import logging
# step0校验函数（校验数据库连接、路径是否存在、数据库名字是否合理）
def step0checksql(hst,pot,usr,pwd):
    logging.info('step0 sql start')
    dbN = 'master'
    con =  dbfunc.SQLcon(hst, pot, usr, pwd, dbN)
    if con:
        logging.info('step0 sql complete')
        return True
    else:
        # print('SQL Error,cannot connect')
        logging.error('step0 sql failed')
        return False
def step0checkpath(path):
    logging.info('step0 path start')
    fileExist = baseFunc.ExistFloader(path)
    if fileExist:
        logging.info('step0 path complete')
        return True
    else:
        logging.error('step0 path failed')
        # print('File Error,file not exists')
        return False
def step0checkname(name):
    logging.info('step0 name start')
    if re.match(r'(^_([a-zA-Z0-9]_?)*$)|(^[a-zA-Z](_?[a-zA-Z0-9])*_?$)',name):
        logging.info('step0 name complete')
        return  True
    else:
        logging.error('step0 name failed')
        # print('DBname Error,not an invalid name')
        return False
# step1 解压文件到对应路径
def step1(brofile,orifile,sparfile):
    logging.info('step1 zip start')
    bksfile = baseFunc.getConfig('File-config', 'brokesavepath')
    orsfile = baseFunc.getConfig('File-config', 'originsavepath')
    spsfile = baseFunc.getConfig('File-config', 'sparesavepath')
    try:
        zip1 = zippack.unzip_file(brofile,bksfile)
        zip2 = zippack.unzip_file(orifile,orsfile)
        zip3 = zippack.unzip_file(sparfile,spsfile)
        logging.info('step1 zip complete')
        return True
    except Exception as e:
        logging.error(f'step1 zip failed,error:{str(e)}')
        return False
# step2比对xml文件
def step2(path1,path2,filename):
    logging.info('step2 start')
    try:
        VersionData1 = CheckXML.getData(path1,filename,'Version')
        VersionData2 = CheckXML.getData(path2,filename,'Version')
        VerNumData1 = CheckXML.getData(path1,filename,'VersionNum')
        VerNumData2 = CheckXML.getData(path2, filename,'VersionNum')
        DBverData1_base = CheckXML.getData(path1, filename,'DBVersionNo')
        DBverData2_base =CheckXML.getData(path2, filename,'DBVersionNo')
        DBnumData1 = CheckXML.DBVresign(DBverData1_base)
        DBnumData2 = CheckXML.DBVresign(DBverData2_base)
        if VersionData1 !=  VersionData2 or  VerNumData1 !=VerNumData2 or DBnumData1 != DBnumData2:
            logging.error('step2 failed1')
            return False
        else:
            logging.info('step2 complete')
            return True
    except:
        logging.error('step2 failed')
        return 'Error'
# step3恢复数据库,并删除同名数据库
def step3(BdbN,OdbN,SdbN,RBdbN,ROdbN,RSdbN,Bfilename,Ofilename,Sfilename,Blogicfile,Ologicfile,Slogicfile,hst,pot,usr,pwd,dbN):
    # 先删除数据库
    logging.info('step3 start')
    E1 =  dbfunc.ExistcheckDb(BdbN,hst,pot,usr,pwd,dbN)
    E2 =  dbfunc.ExistcheckDb(OdbN,hst,pot,usr,pwd,dbN)
    E3 =  dbfunc.ExistcheckDb(SdbN,hst,pot,usr,pwd,dbN)
    if E1:
        logging.info('step3 Bdb exist')
        try:
            D1 = dbfunc.DeleteDB(BdbN, hst, pot, usr, pwd, dbN)
            logging.info('step3 Bdb delete complete')
        except:
            logging.error('step3 Bdb delete failed')
            return False
    if E2:
        logging.info('step3 Odb exist')
        try:
            D2 = dbfunc.DeleteDB(OdbN, hst, pot, usr, pwd, dbN)
            logging.info('step3 Odb delete complete')
        except:
            logging.error('step3 Odb delete failed')
            return False
    if E3:
        logging.info('step3 Sdb exist')
        try:
            D3 = dbfunc.DeleteDB(SdbN, hst, pot, usr, pwd, dbN)
            logging.info('step3 Sdb delete complete')
        except:
            logging.error('step3 Sdb delete failed')
            return False
    # 再恢复
    #得到原始数据库物理文件路径
    logging.info('step3 logicfile get start')
    try:
        Logiclist1 = dbfunc.LogicalData(RBdbN,Bfilename,hst,pot,usr,pwd,dbN)
        Logiclist2 = dbfunc.LogicalData(ROdbN,Ofilename,hst,pot,usr,pwd,dbN)
        Logiclist3 = dbfunc.LogicalData(RSdbN,Sfilename,hst,pot,usr,pwd,dbN)
        logging.info('step3 logicfile get!')
    except Exception as e:
        logging.error(f'step3 logicfile get failed,error:{str(e)}')
        return False
    logging.info('step3 restore get start')
    try:
        Restore1 = dbfunc.RestoreDB(RBdbN,Bfilename,BdbN,Blogicfile,Logiclist1,hst,pot,usr,pwd,dbN)
        Restore2 = dbfunc.RestoreDB(ROdbN,Ofilename,OdbN,Ologicfile,Logiclist2,hst,pot,usr,pwd,dbN)
        Restore3 = dbfunc.RestoreDB(RSdbN,Sfilename,SdbN,Slogicfile,Logiclist3,hst,pot,usr,pwd,dbN)
        logging.info('step3 restore complete')
    except Exception as e:
        logging.error(f'step3 restore failed,error:{str(e)}')
        return False
    logging.info('step3 complete')
    return True
def step3mid(hst,pot,usr,pwd,dbN,Bdb):
    logging.info('step3.5 start')
    try:
        Eapclear = repairfunc.ClearBKtb(hst,pot,usr,pwd,dbN,Bdb)
        # print('Eap_CJT table Clear!')
        # print(Eapclear)
    except Exception as e:
        # print('Eap_CJT table Clear Failed!')
        logging.error(f'step3.5 error1:{str(e)}')
        return  False
    try:
        EapIDadd = repairfunc.EapIDadd(hst,pot,usr,pwd,dbN,Bdb)
        # print('Eap_MenuDefaultOption ID Add!')
        # print(EapIDadd)
    except Exception as e:
        # print('Eap_MenuDefaultOption ID Add Failed!')
        logging.error(f'step3.5 error2:{str(e)}')
        return  False
    logging.info('Step3.5 complete')
    return True
# step4用select * 遍历所有表,找出报错的坏表
def step4(hst,pot,usr,pwd,dbN,Bdb):
    logging.info('step4 start')
    try:
        Alltablelist = repairfunc.Checktb(hst,pot,usr,pwd,dbN,Bdb)
        # print(Alltablelist)
    except Exception as e:
        # print('获取全部表失败')
        logging.error(f'step4 error1:{str(e)}')
        return  False
    try:
        testdb = repairfunc.TestDb(hst,pot,usr,pwd,dbN)
        if testdb =='Unconnect':
            logging.error('step4 unconnect')
            return False
    except Exception as e:
        # print('创建空库失败')
        logging.error(f'step4 error2:{str(e)}')
        return  False
    try:
        Sqllist = repairfunc.QuerySQL(Bdb,Alltablelist)
        # print(Sqllist)
    except Exception as e:
        # print('生成语句失败')
        logging.error(f'step4 error3:{str(e)}')
        return False
    logging.info('step4 get errorlist')
    try:
        Errorlist =  repairfunc.ErrorTB(hst, pot, usr, pwd, dbN, Sqllist)
        # print(Errorlist)
        if len(Errorlist) ==0:
            logging.info('step4 no errorlist')
            logging.info('step4 complete')
            return True
        else:
            logging.info(f'step4 errorlist:{Errorlist}')
            logging.info('step4 complete')
            return Errorlist
    except Exception as e:
        # print('获取损坏表错误！')
        logging.error(f'step4 errorlist failed,error3:{str(e)}')
        return False
def step4mid(hst,pot,usr,pwd,dbN):
    try:
        deldb = repairfunc.DelDB(hst, pot, usr, pwd, dbN)
        if deldb == 'Unconnect':
            logging.error('step4 unconnect')
            return False
    except Exception as e:
    # print('删除空库失败')
        logging.error(f'step4 error4:{str(e)}')
        return False
# step5空账解体
def step5(hst,pot,usr,pwd,dbN,Odb):
    logging.info('step5 start')
    try:
        Dconstrsave = repairfunc.DefauConsave(hst,pot,usr,pwd,dbN,Odb)
        if Dconstrsave == 'Unconnect':
            logging.error('step5 unconnect')
            return False
    except Exception as e:
        logging.error(f'step5 error1:{str(e)}')
        return False
    try:
        Constrsave = repairfunc.Consave(hst,pot,usr,pwd,dbN,Odb)
        if Constrsave == 'Unconnect':
            logging.error('step5 unconnect')
            return False
    except Exception as e:
        logging.error(f'step5 error2:{str(e)}')
        return False
    try:
        Indexsave = repairfunc.IndexSave(hst,pot,usr,pwd,dbN,Odb)
        if Indexsave == 'Unconnect':
            logging.error('step5 unconnect')
            return False
    except Exception as e:
        logging.error(f'step5 error3:{str(e)}')
        return False
    try:
        DeleteAll = repairfunc.DelConIndTab(hst, pot, usr, pwd, dbN, Odb)
        if DeleteAll == 'Unconnect':
            logging.error('step5 unconnect')
            return False
    except Exception as e:
        logging.error(f'step5 error4:{str(e)}')
        return False
    logging.info('step5 complete')
    return True
# step6 插入数据到空账
def step6(hst,pot,usr,pwd,dbN,Bdb,Odb,Ndb):
    logging.info('step6 start')
    try:
        Errolist = step4(hst,pot,usr,pwd,dbN,Bdb)
        # print('step6','Errolist:',Errolist)
        if Errolist == 'Unconnect':
            # print("坏账连接断开")
            logging.error('step6 unconnect')
            return False
    except Exception as e:
        logging.error(f'step6 error1:{str(e)}')
        return False
    if Errolist == True:
        Errolist = []
    try:
        # 这里其实是所有的表，而没有排除坏表
        ALLlist = repairfunc.Checktb(hst,pot,usr,pwd,dbN,Bdb)
        # print('所有',ALLlist)
        OKlist = list(set(ALLlist)-set(Errolist))
        print('Allist:',ALLlist)
        print('Errolist:',Errolist)
        print('OKlist:',OKlist)
        if ALLlist == 'Unconnect':
            # print('断开连接2')
            logging.error('step6 unconnect')
            return False
    except Exception as e:
        logging.error(f'step6 error2:{str(e)}')
        return False
    try:
        Insertb = repairfunc.GetINsertTBN(hst, pot, usr, pwd, dbN, Bdb,Errolist)
        # print('插入的表',Insertb)
        if Insertb == 'Unconnect':
            logging.error('step6 unconnect')
            # print('断开连接2')
            return False
    except Exception as e:
        logging.error(f'step6 error3:{str(e)}')
        return False
    try:
        SQLlist = repairfunc.CreateINSQL(OKlist,Errolist,Bdb,Ndb)
        # print('插入脚本',SQLlist)
        if SQLlist == 'Unconnect':
            # print('断开连接3')
            logging.error('step6 unconnect')
            return False
    except Exception as e:
        logging.error(f'step6 error4:{str(e)}')
        return False
    try:
        Insert = repairfunc.InsertSQL(hst,pot,usr,pwd,dbN,Odb,SQLlist)
        if Insert == 'Unconnect':
            # print('断开连接4')
            logging.error('step6 unconnect')
            return False
        elif len(Insert)>0:
            logging.error(f'step 6 insert error，insert error list:{Insert}')
            return False
    except Exception as e:
        logging.error(f'step6 error5:{str(e)}')
        return False
    logging.info('step6 complete')
    return True
# step7约束重建
def step7(hst, pot, usr, pwd, dbN, Odb):
    logging.info('step7 start')
    try:
        DefaultSQLlist = repairfunc.RebuildDefaultSQL(hst, pot, usr, pwd, dbN, Odb)
        if DefaultSQLlist == 'Unconnect':
            logging.error('step7 unconnect')
            return False
    except Exception as e:
        logging.error(f'step7 error1:{str(e)}')
        return False
    try:
        RebuildDefault = repairfunc.RebuildDCons(hst, pot, usr, pwd, dbN, Odb,DefaultSQLlist)
        if RebuildDefault == 'Unconnect':
            logging.error('step7 unconnect')
            return False
        elif len(RebuildDefault)>0:
            logging.error(f'step 7 rebuild default constraint error，default constraint error list:{RebuildDefault}')
            return False
    except Exception as e:
        logging.error(f'step7 error2:{str(e)}')
        return False
    try:
        IndexSQLlist = repairfunc.RebuildInxSQL(hst, pot, usr, pwd, dbN, Odb)
        if IndexSQLlist == 'Unconnect':
            return False
    except Exception as e:
        logging.error(f'step7 error3:{str(e)}')
        return False
    try:
        RebuildIndex = repairfunc.RebuildInx(hst, pot, usr, pwd, dbN, Odb,IndexSQLlist)
        if RebuildIndex == 'Unconnect':
            logging.error('step7 unconnect')
            return False
        elif len(RebuildIndex)>0:
            logging.error(f'step 7 rebuild index error，index error list:{RebuildIndex}')
            return False
    except Exception as e:
        logging.error(f'step7 error4:{str(e)}')
        return False
    try:
        ConstrSQLlist = repairfunc.RebuildConsSQL(hst, pot, usr, pwd, dbN, Odb)
        if ConstrSQLlist == 'Unconnect':
            logging.error('step7 unconnect')
            return False
    except Exception as e:
        logging.error(f'step7 error5:{str(e)}')
        return False
    try:
        RebuildConstr = repairfunc.RebuildCons(hst, pot, usr, pwd, dbN, Odb,ConstrSQLlist)
        if RebuildConstr == 'Unconnect':
            logging.error('step7 unconnect')
            return False
        elif len(RebuildConstr) >0:
            logging.error(f'step 7 rebuild constraint error，constraint error list:{RebuildConstr}')
            return False
    except Exception as e:
        logging.error(f'step7 error6:{str(e)}')
        return False
    try:
        Enddate = repairfunc.Enddate(hst,pot,usr,pwd,dbN,Odb)
        if Enddate == 'Unconnect':
            logging.error('step7 unconnect')
            return False
    except Exception as e:
        logging.error(f'step7 error7:{str(e)}')
        return False
    try:
        FlashOpen = repairfunc.FlashOpen(hst,pot,usr,pwd,dbN,Odb)
        if FlashOpen == 'Unconnect':
            logging.error('step7 unconnect')
            return False
    except Exception as e:
        logging.error(f'step7 error8:{str(e)}')
        return False
    try:
        FlashSeparate = repairfunc.FlashSeparate(hst, pot, usr, pwd, dbN, Odb)
        if FlashSeparate == 'Unconnect':
            logging.error('step7 unconnect')
            return False
    except Exception as e:
        logging.error(f'step7 error9:{str(e)}')
        return False
    logging.info('step7 complete')
    return True
# step8 xml拷贝\origin备份\打包到zip包里,再移动到对应文件夹.
def step8(bksfile,filename,rprfile,hst,pot,usr,pwd,dbN,rbroFilename,oriname):
    #先拷贝xml文件
    logging.info('step8 start')
    try:
        Trans1 = baseFunc.transform(bksfile,filename,rprfile,filename)
        # print("先拷贝xml文件")
    except Exception as e:
        logging.error(f'step8 copy error:{str(e)}')
        # print('拷贝失败')
        return False
    #备份数据库到新文件夹中，并以老名字命名
    try:
        BackupDB = dbfunc.BackupDB(oriname,rprfile,rbroFilename,hst,pot,usr,pwd,dbN)
        if BackupDB == 'Unconnect':
            logging.error('step8 uconnect')
            return False
    except Exception as e:
        logging.error(f'step8 backup error:{str(e)}')
        return False
    #打包
    try:
        REzip = zippack.zip_file(rprfile)
    except Exception as e:
        logging.error(f'step8 zipfile error:{str(e)}')
        return False
    # 重命名并移动到对应的文件夹下
    try:
        OKfile = './OKzip'
        parentpath = baseFunc.getparentpath(rprfile)
        newfilename = rprfile.split('\\')[-1] +'.zip'
        repairedname = rbroFilename+'(repaired).zip'
        Trans2 = baseFunc.transform(parentpath,newfilename,OKfile,repairedname)
    except Exception as e:
        logging.error(f'step8 transform error:{str(e)}')
        return False
    # 把zip包移动到OKzip目录后，自动删掉repaired文件夹下的东西
    try:
        Deldata = baseFunc.del_file(rprfile)
    except Exception as e:
        logging.error(f'step8 removedata error:{str(e)}')
        return False
    logging.info('step8 complete')
    return True
# step final清除垃圾数据,(不包括repaired目录下的文件)
def Clear(brkname,oriname,sprname,bksfile,orifile,sprfile,bklogicfile,orlogicfile,splogicfile,hst, pot, usr, pwd,dbN):
#     删除数据库
    logging.info('Clear mode start')
    try:
        delDB1 = dbfunc.DeleteDB(brkname, hst, pot, usr, pwd, dbN)
        delDB2 = dbfunc.DeleteDB(oriname, hst, pot, usr, pwd, dbN)
        delDB3 = dbfunc.DeleteDB(sprname, hst, pot, usr, pwd, dbN)
        if delDB1 == 'Unconnect' or  delDB2 == 'Unconnect' or  delDB3 == 'Unconnect':
            return False
    except Exception as e:
        logging.error(f'Clear Error1:{str(e)}')
        return False
#     删除文件
    try:
        remove1 = baseFunc.removefile(bksfile)
        remove2 = baseFunc.removefile(orifile)
        remove2 = baseFunc.removefile(sprfile)
    except Exception as e:
        logging.error(f'Clear Error2:{str(e)}')
        return False
    try:
        newdir1 = baseFunc.mkdir(bksfile)
        newdir2 = baseFunc.mkdir(orifile)
        newdir3 = baseFunc.mkdir(sprfile)
    except Exception as e:
        logging.error(f'Clear Error3:{str(e)}')
        return False
    try:
        newlogicdir1 = baseFunc.mkdir(bklogicfile)
        newlogicdir2 = baseFunc.mkdir(orlogicfile)
        newlogicdir3 = baseFunc.mkdir(splogicfile)
    except Exception as e:
        logging.error(f'Clear Error4:{str(e)}')
        return False
    logging.info('Clear mode complete')
    return True

