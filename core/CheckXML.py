import xml.dom.minidom
def getData(path,filename,mark):
    '''
    path: represents the file that contains unzip_files
    filename: represents the xml-file from the zip
    mark: represents the mark in the xml to locate data
    '''
    xmlpathfile = path + '\\' + filename
    # print(xmlpathfile)
    # 加载xml各个元素信息
    dom = xml.dom.minidom.parse(f'{xmlpathfile}')
    root = dom.documentElement
    # 获取数据
    Oridata =  dom.getElementsByTagName(f'{mark}')
    Atddata =  Oridata[0]
    Findata =  Atddata.firstChild.data
    return Findata
# 数据库版本转换函数
def DBVresign(DBVdata):
    DBVnum = DBVdata
    VersionNum = DBVstr2int(DBVdata)
    RVNum = DBRstr2int(DBVdata)
    #判断版本是否为sql2008之前的版本
    if DBVnum[1] == '.':
        # print('Sqlserver版本是SQL2008以前的版本')
        if DBVnum[0] == '8' :
            if VersionNum in range(1,384):
                # print('SQL 2000 RTM')
                return 'SQL Server 2000'
            elif VersionNum in range(384,534):
                # print('SQL 2000 SP1')
                return 'SQL Server 2000'
            elif VersionNum in range(534,760):
                # print('SQL 2000 SP2')
                return 'SQL Server 2000'
            elif VersionNum in range(760,2039):
                # print('SQL 2000 SP3')
                return 'SQL Server 2000'
            elif VersionNum > 2038:
                # print('SQL 2000 SP4')
                return 'SQL Server 2000'
        elif DBVnum[0] == '9':
            if VersionNum in range(1, 2047):
                # print('SQL 2005 RTM')
                return 'SQL Server 2005'
            elif VersionNum in range(2047, 3042):
                # print('SQL 2005 SP1')
                return 'SQL Server 2005'
            elif VersionNum in range(3042, 4035):
                # print('SQL 2005 SP2')
                return 'SQL Server 2005'
            elif VersionNum in range(4035, 5000):
                # print('SQL 2005 SP3')
                return 'SQL Server 2005'
            elif VersionNum > 4999:
                # print('SQL 2005 SP4')
                return 'SQL Server 2005'
    else:
        print('Sqlserver版本是SQL2008以后的版本')
        if DBVnum[0:2] == '10' and RVNum =='00'  :
            if VersionNum in range(1,2531):
                # print('SQL 2008 RTM')
                return 'SQL Server 2008'
            elif VersionNum in range(2531,4000):
                # print('SQL 2008 SP1')
                return 'SQL Server 2008'
            elif VersionNum in range(4000,5500):
                # print('SQL 2008 SP2')
                return 'SQL Server 2008'
            elif VersionNum in range(5500,6535):
                # print('SQL 2008 SP3')
                return 'SQL Server 2008'
            elif VersionNum > 6535:
                # print('SQL 2008 SP4')
                return 'SQL Server 2008'
        elif DBVnum[0:2] == '10' and RVNum == '50':
            if VersionNum in range(1, 2500):
                # print('SQL 2008 R2 RTM')
                return 'SQL Server 2008'
            elif VersionNum in range(2500, 4000):
                # print('SQL 2008 R2 SP1')
                return 'SQL Server 2008'
            elif VersionNum in range(4000, 6000):
                # print('SQL 2008 R2 SP2')
                return 'SQL Server 2008'
            elif VersionNum in range(6000, 6529):
                # print('SQL 2008 R2 SP3')
                return 'SQL Server 2008'
            elif VersionNum > 6529:
                # print('SQL 2008 R2 SP4')
                return 'SQL Server 2008'
        elif DBVnum[0:2] == '11':
            if VersionNum in range(1, 3000):
                # print('SQL 2012 RTM')
                return 'SQL Server 2012'
            elif VersionNum in range(3000, 5058):
                # print('SQL 2012 SP1')
                return 'SQL Server 2012'
            elif VersionNum in range(5058, 6020):
                # print('SQL 2012 SP2')
                return 'SQL Server 2012'
            elif VersionNum in range(6020, 7001):
                # print('SQL 2012 SP3')
                return 'SQL Server 2012'
            elif VersionNum > 7000:
                # print('SQL 2012 SP4')
                return 'SQL Server 2012'
        elif DBVnum[0:2] == '12':
            if VersionNum in range(1, 4100):
                # print('SQL 2014 RTM')
                return 'SQL Server 2014'
            elif VersionNum in range(4100, 5000):
                # print('SQL 2014 SP1')
                return 'SQL Server 2014'
            elif VersionNum in range(5000, 6024):
                # print('SQL 2014 SP2')
                return 'SQL Server 2014'
            elif VersionNum in range(6024, 6329):
                # print('SQL 2014 SP3')
                return 'SQL Server 2014'
            elif VersionNum > 6329:
                # print('SQL 2014 SP4')
                return 'SQL Server 2014'
        elif DBVnum[0:2] == '13':
            if VersionNum in range(1, 4001):
                # print('SQL 2016 RTM')
                return 'SQL Server 2016'
            elif VersionNum in range(4001, 5149):
                # print('SQL 2016 SP1')
                return 'SQL Server 2016'
            elif VersionNum in range(5149, 5888):
                # print('SQL 2016 SP2')
                return 'SQL Server 2016'
            elif VersionNum > 5888:
                # print('SQL 2016 SP3')
                return 'SQL Server 2016'
        elif DBVnum[0:2] == '14':
                # print('SQL 2017')
                return 'SQL Server 2017'
        elif DBVnum[0:2] == '15':
                # print('SQL 2019')
                return 'SQL Server 2019'
        else:
            # print('New SQL server Version')
            return 'New Version'
# 用来分离数据库版本号
def DBVstr2int(DBdata):
    NumList = DBdata.split('.')
    VersionMK = NumList[2]
    VersionNum = int(VersionMK)
    return VersionNum
def DBRstr2int(DBdata):
    NumList = DBdata.split('.')
    RVMK = NumList[1]
    RVNum = RVMK
    return RVNum

if __name__ == '__main__':
    path = 'E:\\T+\\broken'
    filename = 'AdditionalXml.xml'
    mark = 'DBVersionNo'
    Dt = getData(path,filename,mark)
    # print(Dt)
    DtFinal = DBVresign(Dt)
    # print(DtFinal)



