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
import random
from user_agent import generate_user_agent

import downloadSingleFile
import getCategory



def downloadSingleCate(cateID, dirName, downloadLog, tryBest = True):
    """下载某一类别的词库

    :param cateID: 类别ID
    :param dirName: 下载的目录
    :parm downloadLog: 下载日志，记录下载不成功的文件
    :parm downloadLog: 是否达到最大尝试次数
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

    # 找到最大页的页码，然后所有页面就是1到最大页面
    try:
        request = urllib2.Request(url=pageBaseUrl, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read()
    except urllib2.HTTPError, e:
        if tryBest:
            with io.open(downloadLog.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                f.write((str(e.code)+' error while parsing url '+pageBaseUrl+'\n').decode('utf8'))
        return False
    except:
        if tryBest:
            with io.open(downloadLog.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                f.write(('unexpected error while parsing url '+pageBaseUrl+'\n').decode('utf8'))
        return False

    pageResult = re.findall(pagePattern, data)
    maxPage = 1 if len(pageResult) == 0 else max(map(lambda x:int(x), pageResult))

    # 需要爬取的页面
    pageSet = set(range(1, maxPage+1))
    while pageSet:
        print 'not downloaded pages:',pageSet
        page = random.sample(pageSet, 1)[0] # 随机取一个页面进行抓取
        currentURL = pageBaseUrl + '&page=%s#page'%page
        if currentURL in visited:
            pageSet.remove(page)
            continue
        else:
            visited.add(currentURL)

        try:
            request = urllib2.Request(url=currentURL, headers=headers)
            response = urllib2.urlopen(request)
            data = response.read()
            pageSet.remove(page) # 下载成功就把页面丛集合里面删除
        except urllib2.HTTPError, e:
            with io.open(downloadLog.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                f.write((str(e.code)+' error while parsing url '+currentURL+'\n').decode('utf8'))
            continue
        except:
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
                # 假如下载失败会再次尝试，最多三次
                maxTry = 3
                for i in xrange(maxTry):
                    tryBest = False if i < maxTry-1 else True
                    if downloadSingleFile.downLoadSingleFile(fileURL, fileName, dirName, downloadLog, tryBest):
                        break
                    print '==========retrying to download file %s of url %s'%(fileName, fileURL) 
                # 控制爬虫爬取速度，爬完一个文件睡眠一定时间
                #time.sleep(random.randint(1,10)) 

        # 控制爬虫爬取速度，爬完一个页面的文件睡眠一定时间
        #time.sleep(random.randint(10,20)) 
        

    # 打印出下载某一类别所访问过的页面
    """
    for visit in visited:
        print visit
    """
    return True

if __name__ == '__main__':
    start = time.time()
    '''
    # test data
    downloadDir = 'D:/各大输入法词库/百度/财经'
    downloadLog = 'D:/各大输入法词库/百度/download.log'
    downloadSingleCate(218, downloadDir, downloadLog)
    '''
    baseDir = 'D:/百度输入法/单线程下载'
    #baseDir = '/home/ThesaurusSpider/baidu/singleThread'
    downloadLog = baseDir+'/download.log'
    bigCateDict, smallCateDict = getCategory.getBaiduDictCate()
    for i in bigCateDict.keys():
        for j in smallCateDict[i].keys():
            downloadDir = baseDir+'/%s/%s/' %(bigCateDict[i],smallCateDict[i][j])
            # 最大尝试次数
            maxTry = 3
            for m in xrange(maxTry):
                tryBest = False if m < maxTry - 1 else True
                if downloadSingleCate(j, downloadDir, downloadLog, tryBest):
                    break
    print 'process time:%s' % (time.time() - start)
    