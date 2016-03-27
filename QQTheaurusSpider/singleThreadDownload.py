# encoding:utf-8
# 功能：单线程下载QQ输入法词库，使用时把主函数中的baseDir改成自己的下载目录即可，注意baseDir末尾不能有/

import os
import urllib2
import Queue
import re

import downloadSingleFile
import getQQCategory

def downloadSingleType(bigCate,smallCate,downloadDir,logFile):
    """
    下载某一类的词库，由一级分类和二级分类共同确定
    :param bigCate:     一级分类
    :param smallCate:   一级分类下的二级分类
    :param downloadDir: 下载的路径
    :param logFile:     记录可能出现的错误的日志文件
    :return: None
    """
    if downloadDir[-1] == '/':
        print '下载目录 '+downloadDir+' 末尾不能添加/'
        exit(0)
    cateDir = downloadDir+'/'+bigCate+'/'+smallCate
    if not os.path.exists(cateDir.decode('utf8')):  # 目录不存在的时候创建目录
        os.makedirs(cateDir.decode('utf8'))

    queue =Queue.Queue()
    visited = set()    # 已经访问过的url
    downloaded = set() # 已经下载过的文件
    smallCateURL = 'http://dict.qq.pinyin.cn/dict_list?sort1=%s&sort2=%s' %(urllib2.quote(bigCate), urllib2.quote(smallCate)) # url编码
    queue.put(smallCateURL)

    while not queue.empty():
        currentURL = queue.get()
        if currentURL in visited:
            continue
        else:
            visited.add(currentURL)

        try:
            response = urllib2.urlopen(currentURL)
        except urllib2.HTTPError,e:
            with open(logFile.decode('utf8'), 'a') as f:
                f.write(str(e.code)+' while parsing url '+currentURL+'\n')
            continue
        except:
            with open(logFile.decode('utf8'), 'a') as f:
                f.write('unexcepted error while parsing url '+currentURL+'\n')
            continue

        # 找到链接到其他页面的连接
        data = response.read()
        pagePattern = re.compile('&page=(\d+)"')
        pageList = re.findall(pagePattern,data)
        for i in pageList:
            pageURL = smallCateURL+'&page='+i
            queue.put(pageURL)

        # 下载当前页面存在的文件
        filePattern = re.compile('<a href="/dict_detail\?dict_id=(\d+)">(.*?)</a>')
        fileList = re.findall(filePattern,data)
        for id, name in fileList:
             # print id, name.decode('gbk')
             fileURL = 'http://dict.qq.pinyin.cn/download?dict_id='+id
             filePath = cateDir.decode('utf8')+'/'+name.decode('gbk')+'.qpyd'

             if fileURL in downloaded:
                 continue
             else:
                 downloaded.add(fileURL)
                 print fileURL,name.decode('gbk')+'.qpyd is downloading..........'
                 downloadSingleFile.downloadSingleFile(fileURL, filePath, logFile)
                 print filePath+' is downloaded!!'

    for i in visited:
        print i


if __name__ == '__main__':
    baseDir = 'G:/QQ/输入法'  # 路径最后不能添加/
    logFile = baseDir+'/'+'download.log'
    category = getQQCategory.getCategory()
    for bigCate in category:
        for smallCate in category[bigCate]:
            downloadSingleType(bigCate.encode('utf8'), smallCate.encode('utf8'), baseDir, logFile)













