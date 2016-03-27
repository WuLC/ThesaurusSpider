# encoding:utf-8
# 功能：下载单个QQ词库文件

import urllib2


def downloadSingleFile(URL,downloadPath,logFile):
    """
    功能：下载单个QQ词库文件
    :param URL: 词库文件的URL
    :param downloadPath: 本地的存放目录
    :param logFile: 记录可能出现的错误的日志文件
    :return: None
    """
    try:
        response = urllib2.urlopen(URL)  # 没有防盗链，不需要构造headers
    except urllib2.HTTPError, e:
        with open(logFile.decode('utf8'), 'a') as log:
            log.write(str(e.code)+' while downloading file '+URL+'\n')
        return
    except:
         with open(logFile.decode('utf8'), 'a') as log:
            log.write('unexpected error while downloading file '+URL+'\n')
         return

    data = response.read()
    try:
        with open(downloadPath, 'wb') as f:
            f.write(data)
    except:
        with open(logFile.decode('utf8'),'a') as log:
            f.write('unexpected error while wrting data to local file from url '+URL+'\n')

if __name__ == "__main__":
    url = ' '
    downloadPath = ' '
    logFile = ' '
    downloadSingleFile()