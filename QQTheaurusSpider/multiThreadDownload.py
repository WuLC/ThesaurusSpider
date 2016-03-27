# encoding:utf-8
# 功能：多线程下载QQ输入法词库文件,使用时把主函数中的baseDir改成自己的下载目录即可，注意baseDir末尾不能有/

import threading
import Queue
import re
import urllib2
import os
import time

import downloadSingleFile
import getQQCategory

# 全局变量
queue = Queue.Queue()   # 存储待访问的url
visited = set()     # 存储已经访问的url
downloaded = set()  # 存储已经下载过的文件
logFile = ''      # 日志文件
downloadDir = ''  # 下载的路径
smallCateURL = ''      # 类别url
threadingLock = threading.Lock()  # 保护除Queue以外的共享区域的线程锁

pagePattern = re.compile('&page=(\d+)"')  # 找到其他page的正则匹配模式
filePattern = re.compile('<a href="/dict_detail\?dict_id=(\d+)">(.*?)</a>')  # 找到下载文件的正则匹配模式

# 构建自己的线程类
class downloadThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print self.name+ 'is created!'

    def run(self):
        global visited, downloaded
        while True:
            if queue.empty(): # 防止一开始队列内容太少导致后创建的线程退出
                continue
            currentURL = queue.get()

            # 查看url是否被访问过
            threadingLock.acquire()
            try:
                if currentURL in visited:
                    queue.task_done()
                    continue
                else:
                    visited.add(currentURL)
            finally:
                threadingLock.release()

            # 解析当前页面
            try:
                response = urllib2.urlopen(currentURL)
            except urllib2.HTTPError, e:
                with open(logFile.decode('utf8'), 'a') as f:
                    f.write(str(e.code)+' while parsing url '+currentURL+'\n')
                continue
            except:
                with open(logFile.decode('utf8'), 'a') as f:
                    f.write('unexcepted error while parsing url '+currentURL+'\n')
                continue

            # 找到链接到其他页面的连接
            data = response.read()
            pageList = re.findall(pagePattern,data)
            for i in pageList:
                pageURL = smallCateURL+'&page='+i
                queue.put(pageURL)

            # 下载当前页面存在的文件
            fileList = re.findall(filePattern,data)
            for id, name in fileList:
                fileURL = 'http://dict.qq.pinyin.cn/download?dict_id='+id
                filePath = downloadDir.decode('utf8')+'/'+name.decode('gbk')+'.qpyd'

                # 检查文件是否被下载
                threadingLock.acquire()
                try:
                    if fileURL in downloaded:
                        continue
                    else:
                        downloaded.add(fileURL)
                finally:
                    threadingLock.release()

                print self.name+' is downloading '+fileURL,name.decode('gbk')+'.qpyd  ...........'
                downloadSingleFile.downloadSingleFile(fileURL, filePath, logFile)
                print filePath+' is downloaded!!'

            queue.task_done()  #告诉queue当前任务已完成，否则因为queue调用了join，会一直block下去


# 下载某一类的词库
def downloadSingleType(bigCate,smallCate,baseDir):
    """
    下载某一分类的词库，实际作用是修改全局变量让多线程可以获取到正确的下载路径和存储目录
    :param bigCate:   一级分类
    :param smallCate: 二级分类
    :param baseDir:   下载目录
    :return: None
    """
    global smallCateURL, downloadDir, queue, logFile
    smallCateURL = 'http://dict.qq.pinyin.cn/dict_list?sort1=%s&sort2=%s' %(urllib2.quote(bigCate), urllib2.quote(smallCate))  # url编码
    if baseDir[-1] == '/':
        print '路径 '+baseDir+' 末尾不能有/'
        return
    downloadDir = baseDir+'/'+bigCate+'/'+smallCate
    logFile = baseDir+'/download.log'
    if not os.path.exists(downloadDir.decode('utf8')):  # 目录不存在的时候创建目录
        os.makedirs(downloadDir.decode('utf8'))
    queue.put(smallCateURL)

if __name__ == '__main__':
    start = time.time()
    baseDir = 'G:/各大输入法词库/QQ/多线程下载'  # 下载的目录，最后不能带有/
    category = getQQCategory.getCategory()

    threadNum = 5    # 下载的线程数目
    for i in range(threadNum):
        th = downloadThread()
        th.setDaemon(True)
        th.start()

    for bigCate in category:
        for smallCate in category[bigCate]:
            downloadSingleType(bigCate.encode('utf8'), smallCate.encode('utf8'), baseDir)
            queue.join()

    print 'process time: %s seconds' % (time.time()-start)
