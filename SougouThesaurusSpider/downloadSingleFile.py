# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-03-26 22:42:39
# @Last modified by:   LC
# @Last Modified time: 2017-07-17 22:52:49
# @Email: liangchaowu5@gmail.com

# 功能：下载搜狗输入法单个词库文件

import urllib
import urllib2
import re

def downLoadSingleFile(url,dir,logFile):
    """
    下载单个词库文件
    :param url: 词库文件的URL
    :param dir: 本地的存放目录
    :return: None
    """

    userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
    referrer = 'http://pinyin.sogou.com/dict/cate/index/'
    headers = {}
    headers['User-Agent'] = userAgent
    headers['Referer'] = referrer  # 解决防盗链带来的403问题

    '''
    url 示例
    url = r'http://download.pinyin.sogou.com/dict/download_cell.php?id=15197&name=%E8%B1%A1%E6%A3%8B%E3%80%90%E5%AE%98%E6%96%B9%E6%8E%A8%E8%8D%90%E3%80%91'
    url = 'http://download.pinyin.sogou.com/dict/download_cell.php?id=15197&name=象棋【官方推荐】'
    '''

    request = urllib2.Request(url=url, headers=headers)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        with open(logFile.decode('utf8'), 'a') as f:
            f.write(str(e.code)+' error while downloading file of '+url+'\n')
        return
    except:
        with open(logFile.decode('utf8'), 'a') as f:
            f.write('unexcepted error while downloading file of '+url+'\n')
        return

    data = response.read()
    fileStr = re.findall('name=(.*)$', url)[0]
    filename = urllib.unquote(fileStr)
    filename = filename.replace('/', '-')
    filePath = dir + filename + '.scel'   # 需要将文件名中的/替换，否则报错
    try:
        with open(filePath.decode('utf8'), 'wb') as f:  # 保存中文文件名所必须的
            f.write(data)
        print filePath+' has downloaded!'
    except:
        with open(logFile.decode('utf8'), 'a') as f:
            f.write('unexcepted error while downloading file of '+url+'\n')
        return 


if __name__ ==  '__main__':
    url = 'http://download.pinyin.sogou.com/dict/download_cell.php?id=13793&name=经济 财政 金融 证券 货币 商品 市场 外汇_/'
    downLoadSingleFile(url)
