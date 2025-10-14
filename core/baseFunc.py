# 把查询所有表的内容转换为list格式用（因为结果都是（a，）的形式）
import configparser
import shutil,os
import time
import datetime,logging
from win32gui import *
# 防止重复开启
def checkRestart():
    titles = set()
    def foo(hwnd,nouse):
      #去掉下面这句就所有都输出了，但是我不需要那么多
      if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
        titles.add(GetWindowText(hwnd))
    EnumWindows(foo, 0)
    lt = [t for t in titles if t]
    lt.sort()
    if 'TplusDBMend  ' in lt:
        return  False
    else:
        return True
# 确认是否有文件夹存在用的，没有就自动创建
def mkdir(path):
    path = repath(path)
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
# 查询表的时候得到的结果大都是tuple的形式，需要转成list
def tuple2list(Lst):
    newLst = []
    for a in Lst:
        if isinstance(a,tuple):
            newLst.append(a[0])
    return newLst
# mkdir基础版本，用来确认是否存在对应文件用的
def ExistFile(path,filename,type):
    path = repath(path)
    file = path +'\\'+filename+'.'+type
    res = os.path.exists(file)
    if not res:
        return False
    else:
        return True
# 判断是否有对应文件夹用的
def ExistFloader(path):
    path = repath(path)
    folder =  os.path.exists(path)
    if not folder:
        return False
    else:
        return True
# 根据文件路径值去除类型后缀，得到文件名字
def getFilePathList(path, filetype):
    pathList = []
    path = repath(path)
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(filetype):
                pathList.append(os.path.join(root, file))
    return pathList  # 输出以filetype为后缀的列表
# 获取日志对应字段用的
def getConfig(CigType,CigKey):
    path = os.getcwd()
    path = repath(path)
    filename = 'config.ini'
    file = path +'\\config\\'+filename
    cf = configparser.ConfigParser()
    cf.read(file)  #
    value = cf.get(f"{CigType}",f"{CigKey}")
    return (value)
# 检测config里一些是与否模式用的
def checkMode(data):
    if data == '0' or data == '1':
        return True
    else:
        return False
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
        return e
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
        # print(times)
        return max(times)
    else:
        return False
# 从路径中剥离文件名字用的
def getFilename(filepath):
    filepath = repath(filepath)
    if filepath != '':
        filewhole = filepath.split('\\')[-1]
        filename = filewhole.split('.')[0]
        return filename
    else:
        return False
# 把相对路径转绝对路径用的，因为数据库的脚本里需要的是绝对路径
def repath(path):
    newpath = path.replace('/','\\')
    return newpath
# 移动文件用的方法
def transform(path1,filename1,path2,filename2):
    path1 = repath(path1)
    path2 = repath(path2)
    filepath1 = path1 +'\\'+filename1
    filepath2 = path2 +'\\'+filename2
    try:
        shutil.move(filepath1, filepath2)
        return True
    except Exception as e:
        return False
# 获取上级目录用的
def getparentpath(path):
    parent_path = os.path.dirname(path)
    return parent_path
# 删除文件用的
def removefile(path):
    try:
        shutil.rmtree(path)
        return True
    except Exception as e:
        return False
# 删除文件夹下文件
def del_file(path_data):
    path_data = repath(path_data)
    for i in os.listdir(path_data) :# os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data + "\\" + i#当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data) == True:#os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)
# 程序开启文件时，
def initializationfile():
    logging.info('文件系统初始化开始')
    # 首先初始化各个文件夹
    logfile = mkdir('./logs')
    Fontfile = mkdir('./Fonts')
    iconfile = mkdir('./icon')
    sourcefile = mkdir('./source')
    configfile = mkdir('./config')
    helpfile = mkdir('./Help')
    videofile = mkdir('./Help/Video')
    docfile =  mkdir('./Help/Doc')
    datafile = mkdir('./data')
    okfile = mkdir('./OKzip')
    statementfile = mkdir('./statement')
    tempfile = mkdir('./temp')
    logging.info('文件系统初始化完成')
def initializationdocument():
    logging.info('关键文档初始化开始')
    logging.info('配置文件初始化开始')
    # 配置生成
    path = './config'
    filename = 'config'
    type = 'ini'
    configset = ExistFile(path,filename,type)
    if not configset:
        logging.waring('检测到没有config文件，开始重新生成配置文件')
        with open(".\\data\\config.ini", "w") as f:
            f.write(r'''
[SQL-config]
host = 127.0.0.1
port = 1433
user = sa
password = 123
brokename = broken
originame = origin
sparename = origin1

[File-config]
brokesavepath = .\broken
originsavepath = .\origin
repairsavepath = .\repaired
sparesavepath = .\origin1
brokelogicpath = .\broken\data
originlogicpath = .\origin\data
sparelogicpath = .\origin1\data

[Other-config]
repairmode = 0
dataclearmode = 1
autoupdate = 0

[Version-config]
version = V 2.00  
            ''')
        logging.info('config生成成功')
    else:
        logging.info('检测到config文件，开始重置版本号')
        ver = saveConf('Version-config', 'version', 'V 2.00')
    logging.info('软件使用协议文件初始化开始')
    # statement生成
    path = './statement'
    filename = 'softstatement'
    type = 'txt'
    statementset = ExistFile(path, filename, type)
    if not statementset:
        logging.warning('没有检测到软件协议文件，开始自动生成')
        with open(".\\data\\config.ini", "w") as f:
            f.write(r'''
        　请务必认真阅读和理解本《软件许可使用协议》(以下简称《协议》)中规定的所有权利和限制。除非您接受本《协议》条款，否则您无权下载、安装或使用本”软件”及其相关服务。您一旦安装、复制、下载、访问或以其它方式使用本软件产品，将视为对本《协议》的接受，即表示您同意接受本《协议》各项条款的约束。如果您不同意本《协议》中的条款，请不要安装、复制或使用本软件。

　　1. 权利声明

　　本”软件”的一切知识产权，以及与”软件”相关的所有信息内容，包括但不限于：文字表述及其组合、图标、图饰、图像、图表、色彩、界面设计、版面框架、有关数据、附加程序、印刷材料或电子文档等均为作者所有，受著作权法和国际著作权条约以及其他知识产权法律法规的保护。

　　2. 许可范围

　　2.1 下载、安装和使用：本软件为免费软件，用户可以非商业性、无限制数量地下载、安装及使用本软件。

　　2.2 复制、分发和传播：用户可以非商业性、无限制数量地复制、分发和传播本软件产品。但必须保证每一份复制、分发和传播都是完整和真实的, 包括所有有关本软件产品的软件、电子文档, 版权和商标，亦包括本协议。

　　3. 权利限制

　　3.1 禁止反向工程、反向编译和反向汇编：用户不得对本软件产品进行反向工程(Reverse Engineer)、反向编译(Decompile)或反向汇编(Disassemble)，同时不得改动编译在程序文件内部的任何资源。除法律、法规明文规定允许上述活动外，用户必须遵守此协议限制。

　　3.2 组件分割:本软件产品是作为一个单一产品而被授予许可使用, 用户不得将各个部分分开用于任何目的。

　　3.3 个别授权: 如需进行商业性的销售、复制、分发，包括但不限于软件销售、预装、捆绑等，必须获得作者的授权和许可。

　　3.4 保留权利：本协议未明示授权的其他一切权利仍归作者所有，用户使用其他权利时必须获得作者的书面同意。

　　4. 用户使用须知

　　4.1 本软件提供以定时关机为代表的计划任务功能：多种定时方式执行关机/注销/重启/锁定xx/待机/打开文件(或URL)/复合任务，立即关机/注销/重启/锁定xx/待机，自动同步网络标准时间，方便的计划任务工具等功能。

　　4.2 本软件仅适用于Windows XP/Vista/7操作系统，软件可随操作系统启动而自动运行，以便随时提供所有功能服务并减少响应时间。如果用户在安装本软件后因任何原因欲放弃使用，可删除本软件。

　　4.3 本软件由作者提供产品支持。

　　4.4 软件的修改和升级：作者保留为用户提供本软件的修改、升级版本的权利。

　　4.5 本软件不含有任何旨在破坏用户计算机数据和获取用户隐私信息的恶意代码，不含有任何跟踪、监视用户计算机的功能代码，不会监控用户网上、网下的行为，不会收集用户使用其它软件、文档等个人信息，不会泄漏用户隐私。

　　4.6 用户应在遵守法律及本协议的前提下使用本软件。用户无权实施包括但不限于下列行为：

　　4.6.1 不得删除或者改变本软件上的所有权利管理电子信息;

　　4.6.2 不得故意避开或者破坏著作权人为保护本软件著作权而采取的技术措施;

　　4.6.3 用户不得利用本软件误导、欺骗他人;

　　4.6.4 违反国家规定，对计算机信息系统功能进行删除、修改、增加、干扰，造成计算机信息系统不能正常运行，

　　4.6.5 未经允许，进入计算机信息网络或者使用计算机信息网络资源

　　4.6.6 未经允许，对计算机信息网络功能进行删除、修改或者增加的;

　　4.6.7 未经允许，对计算机信息网络中存储、处理或者传输的数据和应用程序进行删除、修改或者增加;

　　4.6.8 破坏本软件系统或网站的正常运行，故意传播计算机病毒等破坏性程序;

　　4.6.9 其他任何危害计算机信息网络安全的。

　　4.7 对于从非作者指定站点下载的本软件产品以及从非作者发行的介质上获得的本软件产品，作者无法保证该软件是否感染计算机病毒、是否隐藏有伪装的特洛伊木马程序或者黑客软件，使用此类软件，将可能导致不可预测的风险，建议用户不要轻易下载、安装、使用，作者不承担任何由此产生的一切法律责任。

　　4.7.1 不得使用本软件发布违反国家法律的非法广告信息，如色情，赌博等，其造成的一切后果与本作者无关，请自觉营造和谐良性的网络营销环境。违法行为一经发现，本作者有权终止服务并追究法律责任。

　　4.8 隐私权保护：为了更好地改进软件和服务，在用户启动本软件时，本软件会向作者服务器报告软件所在计算机的唯一标识，具体报告方法为访问服务器的一个页面，服务器根据该页面的被访问次数统计软件使用次数。作者不会将此数据与用户的个人身份信息相关联。

　　5.免责与责任限制

　　5.1 本软件经过详细的测试，但不能保证与所有的软硬件系统完全兼容，不能保证本软件完全没有错误。如果出现不兼容及软件错误的情况，用户可登录软件官网论坛将情况报告作者，获得技术支持。如果无法解决兼容性问题，用户可以删除本软件。

　　5.2 使用本软件产品风险由用户自行承担，在适用法律允许的最大范围内，对因使用或不能使用本软件所产生的损害及风险，包括但不限于直接或间接的个人损害、商业赢利的丧失、贸易中断、商业信息的丢失或任何其它经济损失，作者不承担任何责任。

　　5.3 对于因电信系统或互联网网络故障、计算机故障或病毒、信息损坏或丢失、计算机系统问题或其它任何不可抗力原因而产生损失，作者不承担任何责任。

　　5.4 用户违反本协议规定，对作者公司造成损害的。作者有权采取包括但不限于中断使用许可、停止提供服务、限制使用、法律追究等措施。

　　6 . 法律及争议解决

　　6.1 本协议适用中华人民共和国法律。

　　6.2 因本协议引起的或与本协议有关的任何争议，各方应友好协商解决;协商不成的，任何一方均可将有关争议提交至郑州仲裁委员会并按照其届时有效的仲裁规则仲裁;仲裁裁决是终局的，对各方均有约束力。

　　7. 其他条款

　　7.1 如果本协议中的任何条款无论因何种原因完全或部分无效或不具有执行力，或违反任何适用的法律，则该条款被视为删除，但本协议的其余条款仍应有效并且有约束力。

　　7.2 作者有权根据有关法律、法规的变化以及公司经营状况和经营策略的调整等修改本协议。修改后的协议会随附于新版本软件。当发生有关争议时，以最新的协议文本为准。如果不同意改动的内容，用户可以自行删除本软件。如果用户继续使用本软件，则视为您接受本协议的变动。

　　7.3 本协议的一切解释权与修改权归作者。 
                    ''')
        logging.info('协议文件生成成功！')
    logging.info('备用账套路径文件初始化开始')
#  sparefile文件生成
    path = './data'
    filename = 'Sparepath'
    type = 'txt'
    configset = ExistFile(path, filename, type)
    if not configset:
        logging.warning('备用账套路径文件不存在，开始重新生成')
        with open(".\\data\\config.ini", "w") as f:
            f.write('')
        logging.info('备用账套路径文件生成成功')
    logging.info('文档初始化结束')
# 开启日志用的，（但实际不调用这个函数一样开启了，不明所以）
def logstart():
    logging.info('日志系统初始化开始！')
    logname = datetime.datetime.now().strftime('%Y-%m-%d')
    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
    createfile =  mkdir('.\logs')# 生成日志
    logging.basicConfig(filename=f'.\logs\{logname}.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
    logging.info('日志系统初始化结束！')

# 日志启动，不晓得为啥不能通过调用方法启动
logname = datetime.datetime.now().strftime('%Y-%m-%d')
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
createfile = mkdir('.\logs')
logging.basicConfig(filename=f'.\logs\{logname}.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
