# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-03-26 22:42:39
# @Last modified by:   LC
# @Last Modified time: 2017-07-17 22:53:03
# @Email: liangchaowu5@gmail.com

# 功能：利用多线程和队列进行下载搜狗词库，使用时把主函数中的baseDir改成自己的下载目录即可，注意baseDir末尾不能有/

import urllib2
import Queue
import re
import os
import threading
import time

import downloadSingleFile
import getCategory

# 全局变量
VISITED = []         # 记录某个url是否已经被访问了,不用list，因为判断元素是否在list的时间复杂度是O(n)
DOWNLOADED = []     # 记录某个文件是否被下载了
DIR = ' '               # 下载目录
CATEID = 0              # 下载的词库的分类ID
PageBaseURL = ''        # 列出下载文件的页面的URL的共同前缀
FileBaseURL = ''        # 文件实际下载URL的共同前缀
PagePattern = None      # 在网页源码找到其他页面的URL的正则表达匹配模式
FilePattern = None      # 在网页源码找到当前页面可下载文件的url的正则表达匹配模式
QUEUE = Queue.Queue()   # 队列，用于存放待访问的页面URL


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
        print '%s is created' % self.name

    def run(self):
        global VISITED, DOWNLOADED, QUEUE
        while True:
            try:
                currentURL = QUEUE.get()
            except Queue.Empty:
                continue

            lock.acquire()  # 获取锁来修改VISITED内容
            try:
                if currentURL in VISITED:
                    QUEUE.task_done()
                    continue
                else:
                    VISITED.append(currentURL)
            finally:
                lock.release()

            try:
                response = urllib2.urlopen(currentURL)
                data = response.read()
            except urllib2.HTTPError, e:    #将可能发生的错误记录到日志文件中
                with open(DOWNLOADLOG, 'a') as f:
                    f.write(str(e.code)+' error while parsing the URL:'+currentURL+'\n')
            except:
                with open(DOWNLOADLOG, 'a') as f:
                    f.write(' unexpected error while parsing the URL:'+currentURL+'\n')

            pageResult = re.findall(PagePattern, data)
            for i in range(len(pageResult)):
                pageURL = PageBaseURL + '/default' + pageResult[i]
                QUEUE.put(pageURL)

            # 创建不存在的下载目录
            lock.acquire()
            try:
                if not os.path.exists(DIR.decode('utf8')):   # DIR 为str类型，而创建文件夹需要的是Unicode编码，所以需要decode
                    os.makedirs(DIR.decode('utf8'))          # 创建多层目录
            finally:
                lock.release()

            fileResult = re.findall(FilePattern, data)
            for later in fileResult:
                fileURL = FileBaseURL+later

                lock.acquire()  # 获取锁来修改DOWNLOADED内容
                try:
                    if fileURL in DOWNLOADED:
                        continue
                    else:
                        DOWNLOADED.append(fileURL)
                finally:
                    lock.release()

                print self.name + ' is downloading ' + fileURL+' .......'
                downloadSingleFile.downLoadSingleFile(fileURL, DIR, DOWNLOADLOG)
            QUEUE.task_done()   # Queue.join()阻塞直到所有任务完成，也就是说要收到从QUEUE中取出的每个item的task_done消息


def downloadSingleCate(caterotyID,downloadDIR):
    """
    通过类别ID构建某一类词典的下载链接，设置下载目录等参数，初始化这一类别的队列；
    通过修改全局变量，线程读取全局变量来获取修改后的内容

    :param caterotyID: 下载的词库类型的ID，用于找到正确url
    :param downloadDIR: 下载词库的存放目录
    :return: None
    """
    global CATEID, DIR, PageBaseURL, FileBaseURL, PagePattern, FilePattern, QUEUE
    CATEID = caterotyID
    DIR = downloadDIR
    PageBaseURL = 'http://pinyin.sogou.com/dict/cate/index/%s' % CATEID
    FileBaseURL = 'http://download.pinyin.sogou.com'
    PagePattern = re.compile(r'href="/dict/cate/index/%s/default(.*?)"' % CATEID)  # 非贪婪匹配,查找跳转到其他页面的url
    FilePattern = re.compile(r'href="http://download.pinyin.sogou.com(.*?)"')   # 非贪婪匹配,查找可下载的文件
    QUEUE.put(PageBaseURL)  # 将当前页面也就是访问的第一个页面放到队列中


if __name__ == '__main__':
    start = time.time()
    bigCateDict, smallCateDict = getCategory.getSogouDictCate()
    # baseDir = 'G:/搜狗词库/多线程下载'
    baseDir = './sogou_dicts_chinese'
    DOWNLOADLOG = baseDir+'/sougouDownload.log'
    threadNum = 10    # 下载的线程数目
    lock = threading.Lock()
    for i in range(threadNum):
        th = downloadThread()
        th.setDaemon(True)
        th.start()

    for i in bigCateDict:
        for j in smallCateDict[i]:
            downloadDir = baseDir+'/%s/%s/'  %(bigCateDict[i], smallCateDict[i][j])
            downloadSingleCate(j, downloadDir)
            QUEUE.join()  # Blocks until all items in the QUEUE have been gotten and processed（necessary），
    print 'process time:%s' % (time.time()-start)


