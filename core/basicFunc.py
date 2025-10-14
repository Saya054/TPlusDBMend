import pyodbc
try:
    import pywintypes
    from win32gui import *
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
import gzip
from .FileFunctions import mkdir,getFilename,getRealFilename,Existfiles,getparentpath,removefile,Repath
# from ImgResource import Monkey
# from AutoStart import AutoRun
import datetime, logging
import os,heapq
import configparser
import zipfile
import ast
import time
try:
    import rarfile
except ImportError:
    rarfile = None
def hostREmake(hst):
    if hst.replace(' ','') == '127.0.0.1':
        return '.'
    else:
        return hst

def RebuildPercent(p):
    if isinstance(p,int):
        pct = (3-len(str(p))) * ' '+str(p) +'%'
        return pct
    else:
        return '  0%'
''' 
基本功能1：类型、格式转换
'''
# 类型转换1：str转换到List
def strToList(str_list):
    try:
        newlist = ast.literal_eval(str_list)
        return newlist
    except:
        return False
'''
用来按保留天数删除数据用的
'''
def get_dirlist(file_dir):
    if Existfiles(file_dir):
        for root, dirs, files in os.walk(file_dir):
            # print('root',root) #当前目录路径
            # print('++++++')
            # print('dirs',dirs) #当前路径下所有子目录
            # print('++++++')
            # print('files',files) #当前路径下所有非目录子文件
            if root == file_dir:
                return dirs
    else:
        return False
def get_dirnewlist(file_dir):
    dirnamelist = get_dirlist(file_dir)
    dirnewlist = []
    if not dirnamelist:
        return False
    else:
        for dir in dirnamelist:
            if len(dir) == 12 and dir.isdigit() == True:
                dirnewlist.append(dir)
        return dirnewlist
def get_remainlist(file_dir,days):
    dirnewlist = get_dirnewlist(file_dir)
    if not dirnewlist:
        return False
    else:
        if abs(days) == 0:
            return dirnewlist
        else:
            if len(dirnewlist)>= days:
                Remain_list = heapq.nlargest(days, dirnewlist)
                return Remain_list
            else:
                return dirnewlist
def get_Removelist(file_dir,days):
    dirnewlist = get_dirnewlist(file_dir)
    Remain_list = get_remainlist(file_dir,days)
    if not Remain_list:
        return False
    else:
        Remove_list = list(set(dirnewlist)-set(Remain_list))
        return Remove_list

def Removebackup(file_dir,days):
    if str(days).isdigit():
        basefile = RepairBakfile(file_dir)
        remain_name_list = get_Removelist(file_dir,days)
        if not remain_name_list:
            pass
        else:
            for remain_name in remain_name_list:
                remove_file = basefile + '\\' + remain_name
                try:
                    removefile( remove_file)
                    print( remove_file)
                except Exception as e:
                    print('删除失败',e)
    else:
        pass
# 检测config里一些【是与否】模式用的
def checkMode(data):
    if data == '0' or data == '1':
        return True
    else:
        return False
# 获取日志对应字段用的
def getConfig(CigType,CigKey):
    path = os.getcwd()
    path = repath(path)
    filename = 'config.ini'
    file = path +'\\config\\'+filename
    cf = configparser.ConfigParser()
    cf.read(file)
    value = cf.get(f"{CigType}",f"{CigKey}")
    return (value)
# 保存config文件用的
def saveConf(type,basekey,newvalue):
    path = os.getcwd()
    path = repath(path)
    filename = 'config.ini'
    file = path + '\\config\\' + filename
    cf = configparser.ConfigParser()
    cf.read(file)  #
    try:
        cf.set(type,basekey,newvalue)
        cf.write(open(file, 'w'))#这个写入很关键
        return True
    except Exception as e:
        print(e)
        return e
'''
基本功能2：数据清洗-去重、去制表符号
'''
# 数值转换：去除空格、回车等制表符号
def Realdata(data):
    if str(data).replace("\n", "").replace("\t", "").replace(" ", "") == ''  or data is None:
        data =''
        return data
    else:
        return data

# list去除多余的数据（如果为空不去除）
def ListRemove(list,data):
    if data is None or str(data).replace("\n", "").replace("\t", "").replace(" ", "") == '':
        return list
    elif data in list:
        list.remove(data)
        return list
    else:
        return list

# 读进度用的功能
def ReadProcess():
    path = os.getcwd()
    path = repath(path)
    filename = 'process.txt'
    file = path + '\\temp\\' + filename
    with open(file, "r", encoding='UTF-8') as f:
        data = f.readline()
        return data
# 写进度用的功能
def WriteProcess(info):
    path = os.getcwd()
    path = repath(path)
    filename = 'process.txt'
    file = path + '\\temp\\' + filename
    info = str(info)
    try:
        with open(file, "w", encoding='UTF-8') as f:
            f.write(info)
            return True
    except Exception as e:
        return str(e)

'''
特殊功能1：处理zip包功能
'''
# 解压（后面夹的utf_8和cp437是为了避免解压乱码，实际是用rename的方式，去改那个解压出来的乱码名字）
def unzip_file(zip_src, dst_dir):
    zip_src = Repath(zip_src)
    dst_dir = Repath(dst_dir)
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            try:
                newfile = file.encode('cp437').decode('gbk')
                fz.extract(file, dst_dir)
                oldfilename = dst_dir +'/'+ file
                newfilename = dst_dir +'/'+ newfile
                try:
                    os.rename(oldfilename,newfilename)
                    print(f'os.rename({oldfilename},{newfilename})')
                except:
                    raise Exception('Rename failed')
            except:
                newfile = file.encode('utf-8').decode('utf-8')
                fz.extract(file,dst_dir)
    else:
        raise Exception(f'{zip_src} is not zipfile')
#压缩
def zip_file(src_dir):
    zip_name = src_dir +'.zip'
    z = zipfile.ZipFile(zip_name,'w',zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        fpath = dirpath.replace(src_dir,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
    z.close()
# gzip
def gzip_file(src_file,zip_file):
    filesrc = getFilename(src_file)
    f = open(f"{src_file}", "rb")
    value = f.read()
    f.close()
    gz_file = gzip.GzipFile(filename=f"{filesrc}", mode="wb",compresslevel = 9, fileobj = open(f"{zip_file}", "wb"))
    gz_file.write(value)
    gz_file.close()
# rar
def unrar(rar_file, dir_name):
    # rarfile需要unrar支持, linux下pip install unrar, windows下在winrar文件夹找到unrar,加到path里
    if not rarfile:
        raise ImportError("rarfile module is not available. Please install it using: pip install rarfile")
    rarobj = rarfile.RarFile(rar_file)
    rarobj.extractall(dir_name)
# 用来返回压缩包里实际的压缩文件名，避免zip包被改过名字的烦恼
def getzipfilename(zip_src):
    r = zipfile.is_zipfile(zip_src)
    if r:
        filelist =[]
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            try:
                newfile = file.encode('cp437').decode('gbk')
            except:
                newfile = file.encode('utf-8').decode('utf-8')
            filelist.append(newfile)
        return filelist
    else:
        raise Exception(f'{zip_src} is not zipfile')
'''
数据库模块需要的转换功能
'''
# 类型转换1：str转换到List
def strToList(str_list):
    try:
        newlist = ast.literal_eval(str_list)
        return newlist
    except:
        return False

# 类型转换2：把tuple转换到list
def tuple2list(Lst):
    newLst = []
    if isinstance(Lst,list):
        for a in Lst:
            if isinstance(a, tuple):
                newLst.append(a[0])
        return newLst
    else:
        return []
def tuple2listodbc(Lst):
    newLst = []
    if isinstance(Lst, list):
        for a in Lst:
            if isinstance(tuple(a), tuple):
                newLst.append(a[0])
        return newLst
    else:
        return []
def tuple2listpros(Lst):
    newLst = []
    if isinstance(Lst, list):
        if  isinstance(Lst[0], tuple):
            for a in Lst[0]:
                newLst.append(a)
            return newLst
        else:
            return []
    else:
        return []
# 格式转换1：把相对路径转绝对路径用的，因为数据库的脚本里需要的是绝对路径
def repath(path):
    newpath = path.replace('/','\\')
    return newpath
'''
额外写的，获取数据库驱动列表的
'''
def GetOdbcdriver():
    driver_names = ['{'+ x +'}' for x in pyodbc.drivers() if x.endswith('SQL Server')]
    if driver_names:
        return driver_names
    else:
        print('(No suitable driver found. Cannot connect.)')
        return []
# 定义Odbc实例
def DriverList():
    baselist = ['pymssql driver']
    odbclist =GetOdbcdriver()
    try:
        driverlist = baselist + odbclist
        return driverlist
    except:
        return baselist


'''
特殊功能2：工具重开检测
'''


# 防止重开
def checkRestart(winTitle):
    if not WIN32_AVAILABLE:
        # 如果win32gui不可用，默认允许启动
        return True
    
    titles = set()

    def foo(hwnd, nouse):
        # 去掉下面这句就所有都输出了，但是我不需要那么多
        if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
            titles.add(GetWindowText(hwnd))
    EnumWindows(foo, 0)
    lt = [t for t in titles if t]
    lt.sort()
    if winTitle in lt:
        return False
    else:
        return True
'''
基本功能3：判断功能
'''
# 判断框里是否有数据的
def Existdata(data):
    if str(data).replace("\n", "").replace("\t", "").replace(" ", "") == ''  or data is None:
        return False
    else:
        return True
'''
将list合并，然后去重，正常排序
'''
def DriverlistConbine(a,lstb):
    lst1 = [a]
    if a in lstb:
        lstb.remove(a)
    else:
        lstb
    return lst1+lstb
'''
theme合并
'''
def ThemelistConbine(a,lstb):
    lst1 = [a]
    if a in lstb:
        lstb.remove(a)
    else:
        lstb
    return lst1 + lstb
'''
gzip bak文件
'''
def gzip_file(src_file,zip_file):
    filesrc = getFilename(src_file)
    f_ungz = open(src_file,'rb')
    gz_file = gzip.GzipFile(filename=f"{filesrc}", mode="wb",compresslevel = 9, fileobj = open(f"{zip_file}", "wb"))
    gz_file.writelines(f_ungz)
    f_ungz.close()
    gz_file.close()

'''
写LST
'''
# 写lst用
def WriteLst(Lst,bakpath):
    filename = 'UfErpAct.Lst'
    file = bakpath + filename
    Lst = str(Lst)
    try:
        with open(file, "w", encoding='UTF-8') as f:
            f.write(Lst)
            return True
    except Exception as e:
        return str(e)
'''
bakplanfile补齐
'''
def RepairBakfile(filepath):
    if str(filepath)[-1] != '\\':
        return filepath + '\\'
    else:
        return filepath
# 获取日志的用的
def getlogs(file,type):
    files = os.listdir(file)
    logs =[]
    for a in files:
        if a.endswith(f'.{type}'):
            logs.append(a)
    return  logs
# 用来判断日志里，哪个是最新的日志（比较time用的，这里用的max方法，可能在2021-6-7和2021-06-07比较的时候会出问题）
def getNewlogs(file,type):
    logs = getlogs(file,type)
    times = []
    for log in logs:
        name = log.replace('.log','')
        try:
            timedata = time.strptime(name,"%Y-%m-%d")
            times.append(name)
        except:
            pass
    if len(times) > 0:
        return max(times)
    else:
        return False
'''
初始化功能模块
'''
# 初始化ICO
def InitICO():
    try:
        # src = Monkey()
        # with open('monkey.ico', 'wb') as f:
        #     f.write(src)
        return True
    except Exception as e:
        return False
# 初始化开机自动启动的功能
def InitAuto(switch,Exepath):
    if Existfiles(Exepath):
        appFullname = getRealFilename(Exepath)
        appFrontname =getFilename(Exepath)
        apploction = getparentpath(Exepath)
        if switch== 1:
            # AutoRun(switch="open",  # 开：open # 关：close
            # zdynames=appFullname,  # 当前文件名的名称如：newsxiao.py
            # current_file=appFrontname,  # 获得文件名的前部分,如：newsxiao
            # abspath=apploction) # 当前文件路径
            pass
        elif switch == 0:
                # AutoRun(switch="close",  # 开：open # 关：close
                #         zdynames=appFullname,  # 当前文件名的名称如：newsxiao.py
                #         current_file=appFrontname,  # 获得文件名的前部分,如：newsxiao
                #         abspath=apploction)  # 当前文件路径
                pass
        else:
            pass
    else:
        pass
'''
初始化日志系统
'''
def logstart():
    logname = datetime.datetime.now().strftime('%Y-%m-%d')
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    createfile = mkdir('.\logs')  # 生成日志
    logging.basicConfig(filename=f'./logs/{logname}.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.info('日志系统初始化！')
if __name__ == '__main__':
    from baseDBFunc import BaseDBfunc
    import FileFunctions
    brkfile = 'G:/test/培训测试/264117.zip'
    orifile = 'G:/test/培训测试/264117（1）.zip'
    bakfile = 'G:/test/培训测试/264117（1）.zip'
    configfile = 'config.db'
    baseconfig = BaseDBfunc(configfile)
    filename = 'AdditionalXml.xml'
    brkzipfile = baseconfig.getDefaultConfig('brokesavepath')
    orizipfile = baseconfig.getDefaultConfig('originsavepath')
    bakzipfile = baseconfig.getDefaultConfig('sparesavepath')
    try:
        print(1)
        zip1 = unzip_file(brkfile, brkzipfile)
        print(2)
        print(f'zip2 = unzip_file({orifile}, {orizipfile})')
        zip2 = unzip_file(orifile, orizipfile)
        print(3)
        zip3 = unzip_file(bakfile, bakzipfile)
        # logging.info('step1 zip complete')
        print('*解压zip成功')
    except Exception as e:
        print(f'*解压zip失败，失败原因为：{e}')
        # logging.error(f'step1 zip failed,error:{str(e)}')
        mes = '解压失败：' + str(e)

    # zip2 = unzip_file('G:/test/培训测试/264117（1）.zip','./Data/orifile/zipfile')
    # print(zip2)
