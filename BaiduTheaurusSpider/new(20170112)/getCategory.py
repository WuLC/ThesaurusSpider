# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2017-01-11 22:42:39
# @Last modified by:   WuLC
# @Last Modified time: 2017-01-12 09:56:23
# @Email: liangchaowu5@gmail.com

# 功能：获取百度词库的分类

import sys
import urllib2
import re

def getBaiduDictCate():
    """
    功能：得到百度词库的分类，有三级分类，因为三级分类太细而且较少，所以将三级分类纳入其二级分类
    :return:两个词典，第一个词典记录大类的ID和内容的对应关系，第二个词典记录了第一个词典中每一类大类下的所有分类
    """
    bigCateDict = {}
    smallCateDict ={}
    initPageURL = r'https://shurufa.baidu.com/dict'
    cateBaseURL = r'https://shurufa.baidu.com/dict_list?cid='

    # 防止502错误
    userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2526.111 Safari/537.36'
    referrer = 'http://shurufa.baidu.com/dict.html'  
    headers = {}
    headers['User-Agent'] = userAgent
    headers['Referer'] = referrer

    # 抓取大类
    try:
        request = urllib2.Request(url=initPageURL, headers=headers)
        response = urllib2.urlopen(request)
        data = response.read()
    except urllib2.HTTPError, e:
        print 'Error while getting the big category,error code:',e.code
        sys.exit()

    bigCatePattern = re.compile(r'cid=(\d+).*?category1(.|\n)*?<span>(.*?)</span>')
    result = re.findall(bigCatePattern, data)
    for i in result:
        bigCateDict[i[0]] = i[2]  # 一个大类
        #print bigCateID, i[2]

    # 抓取大类下对应的小类
    for bigCateID in bigCateDict.keys():   
        smallCateDict[bigCateID] = {}
        smallCateURL = cateBaseURL+bigCateID
        try:
            request = urllib2.Request(url=smallCateURL, headers=headers)
            smallResponse = urllib2.urlopen(request)
            smallData = smallResponse.read()
        except urllib2.HTTPError, e:
            print 'Error code:',e.code
            continue
        
        if bigCateID == "157": # 城市区划的页面很特殊，需要特殊处理
            smallCatePattern = re.compile(r'cid=(\d+)(.|\n)*?category1">((.|\n)*?)</a>')
        else:
            smallCatePattern = re.compile(r'cid=(\d+)(.|\n)*?category2">((.|\n)*?)</a>')

        smallResult = re.findall(smallCatePattern, smallData)
        for j in smallResult:
            if bigCateID == "157" and j[0] in bigCateDict: # 防止找城市区划下面的子分类的时候将其他的一级分类都找出来
                continue
            smallCateDict[bigCateID][j[0]] = j[2].strip()
            #print '\t', j[0], j[2].strip()
    return bigCateDict, smallCateDict
    

if __name__ == '__main__':
    bigCateDict, smallCateDict = getBaiduDictCate()
    for bigCateID, bigCate  in bigCateDict.items():
        print bigCateID, bigCate
        for smallCateID, smallCate in smallCateDict[bigCateID].items():
            print '\t', smallCateID, smallCate


