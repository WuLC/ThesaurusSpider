# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-03-26 22:42:39
# @Last modified by:   LC
# @Last Modified time: 2016-04-11 15:21:27
# @Email: liangchaowu5@gmail.com

# 功能：单线程下载百度词库，将主函数中的baseDir改为自己的下载路径即可运行，baseDir末尾没有/

import urllib2
import Queue
import re
import os
import time
import downloadSingleFile
import getCategory


def downloadSingleCate(cateID, dir, downloadLog):
    """
    下载某一类别的词库

    :param cateID: 类别ID
    :param dir: 下载的目录
    :parm downloadLog:下载日志，记录下载不成功的文件
    :return: None
    """
    pageBaseUrl = r'http://shurufa.baidu.com/dict-list.html?cid=%s' %cateID
    fileBaseUrl = r'http://shurufa.baidu.com/?act=dict-download&id='

    pagePattern = re.compile(r'from=dict-list&page=(\d+)"')  # 非贪婪匹配,查找跳转到其他页面的url
    filePattern = re.compile(r'dict-info.html\?id=(\d+).*?title="(.*?)" ')   # 非贪婪匹配,查找可下载的文件的id和

    visited = set()       # 记录某个url是否已经被访问了
    downloaded = set()    # 记录某个文件是否被下载了
    queue = Queue.Queue() # 创建一个FIFO队列，用于存放待遍历的url（bfs）

    #  bfs 查找所有的url,队列不为空时可以一直遍历
    queue.put(pageBaseUrl)  # 将当前页面也就是访问的第一个页面放到队列中

    while not queue.empty():
        currentURL = queue.get()
        if currentURL in visited:
            continue
        else:
            visited.add(currentURL)

        try:
            response = urllib2.urlopen(currentURL)
            data = response.read()
        except urllib2.HTTPError, e:
            with open(downloadLog, 'a') as f:
                f.write(str(e.code)+' error while parsing url '+currentURL+'\n')
        except:
            print 'unexcepted error'
            with open(downloadLog, 'a') as f:
                f.write('unexpected error while parsing url '+currentURL+'\n')

        pageResult = re.findall(pagePattern, data)
        for i in range(len(pageResult)):
            queue.put(pageBaseUrl +'&from=dict-list&page='+pageResult[i])

        # 查找并下载文件
        # 指定下载目录，目录不存在时自动创建,需要在前面加上u，指定编码为utf-8
        if not os.path.exists(dir.decode('utf8')):   # dir 为str类型
            os.makedirs(dir.decode('utf8'))          # 创建多层目录

        fileResult = re.findall(filePattern, data)
        for fileID, fileName in fileResult:
            fileURL = fileBaseUrl+fileID
            if fileURL in downloaded:
                continue
            else:
                downloaded.add(fileURL)
                print fileName+' downloading.......'
                try:
                    downloadSingleFile.downLoadSingleFile(fileURL, fileName, dir, downloadLog)
                except:
                    with open(downloadLog, 'a') as f:
                        f.write(fileURL+' is not DOWNLOADED successfully\n')


    # 打印出下载某一类别所访问过的页面
    for visit in visited:
        print visit

if __name__ == '__main__':
    start = time.time()
    '''
    # test data
    downloadDir = 'G:/各大输入法词库/百度/'
    downloadLog = 'G:/各大输入法词库/百度/download.log'
    downloadSingleCate(211, downloadDir, downloadLog)
    '''
    baseDir = 'G:/百度输入法/单线程下载'
    downloadLog = baseDir+'/download.log'
    bigCateDict, smallCateDict = getCategory.getBaiduDictCate()
    for i in bigCateDict:
        for j in smallCateDict[i]:
            downloadDir = baseDir+'/%s/%s/' %(bigCateDict[i],smallCateDict[i][j])
            downloadSingleCate(j, downloadDir, downloadLog)
    print 'process time:%s' % (time.time() - start)