# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2017-01-14 11:42:39
# @Last modified by:   LC
# @Last Modified time: 2016-01-14 18:21:15
# @Email: liangchaowu5@gmail.com

# 功能：多线程下载百度词库,将主函数中的baseDir改为自己的下载路径即可运行，baseDir末尾没有/

import urllib2
import Queue
import re
import os
import io
import threading
import time

from user_agent import generate_user_agent

import downloadSingleFile
import getCategory

# global variables
VISITED = set()           # 记录某个url是否已经被访问了
DOWNLOADED = set()        # 记录某个文件是否被下载了
DOWNLOAD_DIR = ''         # 下载目录
DOWNLOAD_LOG = ''         # 记录下载中出错的日志
CATEID = ''               # 下载的词库的分类ID
PAGE_BASE_URL = ''        # 某一分类的页面前缀
PAGE_QUEUE = Queue.Queue()     # 记录某一分类的所有下载页数
THREAD_LOCK = threading.Lock() # 用于保护公共变量的锁


class downloadThread(threading.Thread):
    """
    用于下载文件的线程类
    利用广度优先搜索，每次从队列里面取出一个URL访问，从这个URL中可能得到两种URL
    1. 其他页面URL
    2. 文件URL
    对于第一种URL放入队列，第二种URL则直接通过当前线程下载
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self.fileBaseURL = 'https://shurufa.baidu.com/dict_innerid_download?innerid=' # 文件实际下载URL的共同前缀
        self.filePattern = re.compile(r'dict-name="(.*?)" dict-innerid="(\d+)"')   #在网页源码找到当前页面可下载文件的url的正则表达匹配模式
        print '%s is created' % self.name

    def run(self):
        global VISITED, DOWNLOADED, DOWNLOAD_LOG, DOWNLOAD_DIR, PAGE_QUEUE
        while True:
            print PAGE_QUEUE.qsize()
            try:
                currentPage = PAGE_QUEUE.get()
                currentURL = PAGE_BASE_URL+'&page=%s#page'%currentPage
            except PAGE_QUEUE.Empty:
                continue

            THREAD_LOCK.acquire()  # 获取锁来修改VISITED内容
            try:
                if currentURL in VISITED:
                    PAGE_QUEUE.task_done()
                    continue
                else:
                    VISITED.add(currentURL)
            finally:
                THREAD_LOCK.release()

            
            # 获取当前页面, 为了防止502,500错误, 最多尝试三次
            maxTry = 3
            data = None
            for i in xrange(maxTry):
                try:
                    response = urllib2.urlopen(currentURL)
                    data = response.read()
                    break
                except urllib2.HTTPError, e:
                    if i == maxTry-1:
                        with io.open(DOWNLOAD_LOG.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                            f.write((str(e.code)+' error while parsing url '+currentURL+'\n').decode('utf8'))
                except:
                    if i == maxTry-1:
                        with io.open(DOWNLOAD_LOG.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                            f.write(('unexpected error while parsing url '+currentURL+'\n').decode('utf8'))
            
            # 获取当前页面不成功, 将页面放回队列中并取下一个页面
            if data == None: 
                PAGE_QUEUE.task_done() # 虽然没完成，但是也要task_done 否则队列会一直block下去
                PAGE_QUEUE.put(currentPage)  
                continue

            # 创建不存在的下载目录
            THREAD_LOCK.acquire()
            try:
                if not os.path.exists(DOWNLOAD_DIR.decode('utf8')):   # DOWNLOAD_DIR 为str类型，而创建文件夹需要的是Unicode编码，所以需要decode
                    os.makedirs(DOWNLOAD_DIR.decode('utf8'))          # 创建多层目录
            finally:
                THREAD_LOCK.release()

            fileResult = re.findall(self.filePattern, data)
            for fileName, fileID in fileResult:
                fileURL = self.fileBaseURL + fileID
                THREAD_LOCK.acquire()  # 获取锁来修改DOWNLOADED内容
                try:
                    if fileURL in DOWNLOADED:
                        continue
                    else:
                        DOWNLOADED.add(fileURL)
                finally:
                    THREAD_LOCK.release()
                print self.name + ' is downloading' + fileName + '.......'

                # 防止500,502错误，最大尝试三次
                maxTry = 3
                for m in xrange(maxTry):
                    tryBest = False if m < maxTry - 1 else True
                    if downloadSingleFile.downLoadSingleFile(fileURL, fileName, DOWNLOAD_DIR, DOWNLOAD_LOG, tryBest):
                        break
                    print '==========retrying to download file %s of url %s'%(fileName, fileURL) 

            PAGE_QUEUE.task_done()   # PAGE_QUEUE.join()阻塞直到所有任务完成，也就是说要收到从 PAGE_QUEUE 中取出的每个item的task_done消息


def getCategoryPages(caterotyID,downloadDIR):
    """通过类别的初始页面得到该类别的总页数，并将所有的页数放到 PAGE_QUEUE 中供所有线程下载

    :param caterotyID: 下载的词库类型的 ID，用于找到正确 url
    :param downloadDIR: 下载词库的存放目录
    :return:
    """
    global CATEID, DOWNLOAD_DIR, PAGE_BASE_URL, THREAD_LOCK
    CATEID = caterotyID
    DOWNLOAD_DIR = downloadDIR
    PAGE_BASE_URL = 'https://shurufa.baidu.com/dict_list?cid=%s' % CATEID
    pagePattern = re.compile(r'page=(\d+)#page')    # 在网页源码找到其他页面的URL的正则表达匹配模式
    
    # 防止502错误
    userAgent = generate_user_agent()
    referrer = 'http://shurufa.baidu.com/dict.html'  
    headers = {}
    headers['User-Agent'] = userAgent
    headers['Referer'] = referrer

    # 找到最大页的页码，然后所有页面就是1到最大页面
    # 可能会返回502,500错误，最多尝试5次
    maxTry = 8
    data = None
    for i in xrange(maxTry):
        try:
            request = urllib2.Request(url=PAGE_BASE_URL, headers=headers)
            response = urllib2.urlopen(request)
            data = response.read()
            break
        except urllib2.HTTPError, e:
            if i == maxTry-1:
                with io.open(DOWNLOAD_LOG.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                    f.write((str(e.code)+' error while parsing url '+PAGE_BASE_URL+'\n').decode('utf8'))
        except:
            if i == maxTry-1:
                with io.open(DOWNLOAD_LOG.decode('utf8'), mode = 'a', encoding = 'utf8') as f:
                    f.write(('unexpected error while parsing url '+PAGE_BASE_URL+'\n').decode('utf8'))

    # 成功获得当前类别的页面后，将该类别所有页面放到 PAGE_QUEUE 中，否则就要放弃该类别下载下一类别
    if data:
        pageResult = re.findall(pagePattern, data)
        maxPage = 1 if len(pageResult) == 0 else max(map(lambda x:int(x), pageResult))
        for page in xrange(1, maxPage+1):
            PAGE_QUEUE.put(page)
        



if __name__ == '__main__':
    baseDir = 'D:/百度输入法/多线程下载' # 设置你的下载目录
    DOWNLOAD_LOG = baseDir+'/baiduDownload.log'
    start = time.time()
    bigCateDict, smallCateDict = getCategory.getBaiduDictCate()
    print '===========get categories successfully================'
    threadNum = 5    # 下载的线程数目
    # 创建线程
    for i in range(threadNum):
        th = downloadThread()
        th.setDaemon(True)
        th.start()

    for i in bigCateDict:
        for j in smallCateDict[i]:
            downloadDir = baseDir+'/%s/%s/'  %(bigCateDict[i], smallCateDict[i][j])
            getCategoryPages(j, downloadDir)
            PAGE_QUEUE.join()  # Blocks until all items in the QUEUE have been gotten and processed（necessary)
    print 'process time:%s' % (time.time()-start)
