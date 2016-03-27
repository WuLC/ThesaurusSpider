#encoding: utf-8
# 功能：下载百度词库的当个文件

import urllib2

def downLoadSingleFile(url, fileName, downloadDir, downloadLog):
    """
    功能：下载单个词库文件
    :param url: 词库文件的url地址
    :param fileName: 词库文件的文件名
    :param downloadDir: 词库文件的下载目录
    :param downloadLog: 下载日志，记录下载不成功的记录
    :return:None
    """
    userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
    referrer = 'http://shurufa.baidu.com/dict.html'  # 百度词库貌似没有防盗链,但这里为了保险还是在请求时带上referer
    headers = {}
    headers['User-Agent'] = userAgent
    headers['Referer'] = referrer

    request = urllib2.Request(url=url, headers=headers)
    try:
        response = urllib2.urlopen(request)
        data = response.read()
        filePath = downloadDir+fileName.replace('/', '-')+'.bdict'   # 需要将文件名中的/替换，否则或造成目录误判
        print filePath
        with open(filePath.decode('utf8'), 'wb') as f:  # 保存中文文件名所必须的
            f.write(data)
    except urllib2.HTTPError, e:
        with open(downloadLog.decode('utf8'), 'a') as f:
            f.write(str(e.code)+'error while downloading file ' + fileName + 'of URL '+url+'\n')
    except:
        with open(downloadLog.decode('utf8'), 'a') as f:
            f.write('unexpected error while downloading file ' + fileName + 'of URL '+url+'\n')

if __name__ == '__main__':
    url = 'http://shurufa.baidu.com/?act=dict-download&id=33'
    url1 = 'http://act=dict-download'
    name = 'test'
    dir = 'G:/各大输入法词库/百度/'
    log = 'G:/各大输入法词库/百度/download.log'
    downLoadSingleFile(url, name, dir, log)
