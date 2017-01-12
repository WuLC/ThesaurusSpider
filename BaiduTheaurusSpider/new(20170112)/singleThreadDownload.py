# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2017-01-11 22:42:39
# @Last modified by:   LC
# @Last Modified time: 2017-01-12 22:21:27
# @Email: liangchaowu5@gmail.com

# 功能：单线程下载百度词库，将主函数中的baseDir改为自己的下载路径即可运行，baseDir末尾没有/

import urllib2
import io
import re
import os
import time
import downloadSingleFile
import getCategory

from user_agent import generate_user_agent

def downloadSingleCate(cateID, dirName, downloadLog):
    """下载某一类别的词库

    :param cateID: 类别ID
    :param dirName: 下载的目录
    :parm downloadLog:下载日志，记录下载不成功的文件
    :return: None
    """
    pageBaseUrl = r'https://shurufa.baidu.com/dict_list?cid=%s' %cateID
    fileBaseUrl = r'https://shurufa.baidu.com/dict_innerid_download?innerid='

    pagePattern = re.compile(r'page=(\d+)#page')  # 非贪婪匹配,查找跳转到其他页面的url
    filePattern = re.compile(r'dict-name="(.*?)" dict-innerid="(\d+)"')   # 非贪婪匹配,查找可下载的文件的id和

    visited = set()       # 记录某个url是否已经被访问了
    downloaded = set()    # 记录某个文件是否被下载了


    # 防止502错误
    userAgent = generate_user_agent()
    referrer = 'http://shurufa.baidu.com/dict.html'  
    headers = {}
    headers['User-Agent'] = userAgent
    headers['Referer'] = referrer

    # 找到最大页的页码，然后从1开始遍历
    request = urllib2.Request(url=pageBaseUrl, headers=headers)
    response = urllib2.urlopen(request)
    data = response.read()
    pageResult = re.findall(pagePattern, data)
    maxPage = 1 if len(pageResult) == 0 else max(map(lambda x:int(x), pageResult))

    for page in xrange(1, maxPage+1):
        currentURL = pageBaseUrl + '&page=%s#page'%page
        if currentURL in visited:
            continue
        else:
            visited.add(currentURL)

        try:
            request = urllib2.Request(url=currentURL, headers=headers)
            response = urllib2.urlopen(request)
            data = response.read()
        except urllib2.HTTPError, e:
            with io.open(downloadLog.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                f.write((str(e.code)+' error while parsing url '+currentURL+'\n').decode('utf8'))
        except:
            print 'unexcepted error'
            with io.open(downloadLog.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                f.write(('unexpected error while parsing url '+currentURL+'\n').decode('utf8'))
            continue


        # 查找并下载文件
        # 指定下载目录，目录不存在时自动创建,需要在前面加上u，指定编码为utf-8
        if not os.path.exists(dirName.decode('utf8')):   # dirName 为str类型
            os.makedirs(dirName.decode('utf8'))          # 创建多层目录

        fileResult = re.findall(filePattern, data)
        for fileName, fileID in fileResult:
            fileURL = fileBaseUrl+fileID
            if fileURL in downloaded:
                continue
            else:
                downloaded.add(fileURL)
                print fileName+' downloading...................................................'
                # 在 downloadSingleFile 函数中处理异常
                downloadSingleFile.downLoadSingleFile(fileURL, fileName, dirName, downloadLog)
                

    # 打印出下载某一类别所访问过的页面
    for visit in visited:
        print visit

if __name__ == '__main__':
    start = time.time()
    '''
    # test data
    downloadDir = 'D:/各大输入法词库/百度/财经'
    downloadLog = 'D:/各大输入法词库/百度/download.log'
    downloadSingleCate(218, downloadDir, downloadLog)
    '''
    baseDir = 'D:/百度输入法/单线程下载'
    downloadLog = baseDir+'/download.log'
    bigCateDict, smallCateDict = getCategory.getBaiduDictCate()
    for i in bigCateDict:
        for j in smallCateDict[i]:
            downloadDir = baseDir+'/%s/%s/' %(bigCateDict[i],smallCateDict[i][j])
            downloadSingleCate(j, downloadDir, downloadLog)
    print 'process time:%s' % (time.time() - start)
    