# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-03-26 22:42:39
# @Last modified by:   LC
# @Last Modified time: 2016-04-11 15:22:41
# @Email: liangchaowu5@gmail.com

# 功能：单线程下载搜狗输入法的词库，使用时把主函数中的baseDir改成自己的下载目录即可，注意baseDir末尾不能有/

import urllib2
import Queue
import re
import os
import time
import downloadSingleFile
import getCategory


def downloadSingleCate(cateID,dir,logFile):
    pageBaseUrl = 'http://pinyin.sogou.com/dict/cate/index/%s' % cateID
    fileBaseUrl = 'http://download.pinyin.sogou.com'

    pagePattern = re.compile(r'href="/dict/cate/index/%s/default(.*?)"' % cateID)  # 非贪婪匹配,查找跳转到其他页面的url
    filePattern = re.compile(r'href="http://download.pinyin.sogou.com(.*?)"')   # 非贪婪匹配,查找可下载的文件

    visited = []       # 记录某个url是否已经被访问了
    downloaded = []    # 记录某个文件是否被下载了
    queue = Queue.Queue() # 创建一个FIFO队列，用于存放待遍历的url（bfs）

    #  bfs 查找所有的url,队列不为空时可以一直遍历
    queue.put(pageBaseUrl)  # 将当前页面也就是访问的第一个页面放到队列中

    while not queue.empty():
        currentURL = queue.get()
        if currentURL in visited:
            continue
        else:
            visited.append(currentURL)

        try:
            response = urllib2.urlopen(currentURL)
            data = response.read()
        except urllib2.HTTPError, e:
            with open(logFile.decode('utf8'), 'a') as f:
                f.write(str(e.code)+' error while parsing page of '+currentURL+'\n')
        except:
            with open(logFile.decode('utf8'), 'a') as f:
                f.write('unexcepted error while parsing page of '+currentURL+'\n')

        pageResult = re.findall(pagePattern, data)
        for i in range(len(pageResult)):
            queue.put(pageBaseUrl + '/default' + pageResult[i])

        # 查找并下载文件
        # 指定下载目录，目录不存在时自动创建,需要在前面加上u，指定编码为utf-8

        if not os.path.exists(dir.decode('utf8')):   # dir 为str类型，但是创建目录# 必须要用
            os.makedirs(dir.decode('utf8'))          # 创建多层目录

        fileResult = re.findall(filePattern, data)
        for later in fileResult:
            fileURL = fileBaseUrl+later
            if fileURL in downloaded:
                continue
            else:
                downloaded.append(fileURL)
            print fileURL+' downloading.......'
            downloadSingleFile.downLoadSingleFile(fileURL, dir, logFile)


    for visit in visited:
        print visit

if __name__ == '__main__':
    start = time.time()
    bigCateDict, smallCateDict = getCategory.getSogouDictCate()
    baseDir = './sogou_dicts_single_thread2'
    logFile = baseDir+'/download.log'
    for i in bigCateDict:
        for j in smallCateDict[i]:
            downloadDir = baseDir+'/%s/%s/' %(bigCateDict[i],smallCateDict[i][j])
            downloadSingleCate(int(j), downloadDir, logFile)
    print 'process time:%s' % (time.time() - start)
