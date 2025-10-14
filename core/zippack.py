import zipfile
import os
# 解压（后面夹的utf_8和cp437是为了避免解压乱码，实际是用rename的方式，去改那个解压出来的乱码名字）
def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            try:
                newfile = file.encode('cp437').decode('gbk')
                fz.extract(file, dst_dir)
                oldfilename = dst_dir +'\\'+ file
                newfilename = dst_dir +'\\'+ newfile
                try:
                    os.rename(oldfilename,newfilename)
                except:
                    raise Exception('Rename failed')
            except:
                newfile = file.encode('utf-8').decode('utf-8')
                fz.extract(file,dst_dir)
    else:
        # print('This is not zip')
        raise Exception(f'{zip_src} is not zipfile')
        # return f'{zip_src} is not zipfile'
#压缩
def zip_file(src_dir):
    zip_name = src_dir +'.zip'
    z = zipfile.ZipFile(zip_name,'w',zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        fpath = dirpath.replace(src_dir,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
            # print ('==压缩成功==')
    z.close()
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
        # print('This is not zip')
        raise Exception(f'{zip_src} is not zipfile')
        # return f'{zip_src} is not zipfile'
