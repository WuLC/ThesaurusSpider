# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2017-01-11 22:42:39
# @Last modified by:   WuLC
# @Last Modified time: 2017-01-12 09:56:23
# @Email: liangchaowu5@gmail.com

# 功能：获取百度词库的分类

import sys
import random
import urllib2
import re
from user_agent import generate_user_agent

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
    userAgent = generate_user_agent()
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
        #print i[0], i[2]

    # 抓取大类下对应的小类, 遇到 502 重复进行请求
    bigCateSet = set(bigCateDict.keys())
    while bigCateSet:
        bigCateID = random.sample(bigCateSet,1)[0]
        smallCateDict[bigCateID] = {}
        smallCateURL = cateBaseURL+bigCateID
        try:
            request = urllib2.Request(url=smallCateURL, headers=headers)
            smallResponse = urllib2.urlopen(request)
            smallData = smallResponse.read()
            bigCateSet.remove(bigCateID)
        except urllib2.HTTPError, e:
            print 'Error code:',e.code
            continue
        
        # \s 表示不可见字符(包括空格，tab，换行符等)
        if bigCateID == "157": # 城市区划的页面很特殊，需要特殊处理
            smallCatePattern = re.compile(r'<a\s*href="/dict_list\?cid.*?cid=(\d+)\s*data-stats="webDictListPage.category1">(.*?)\s*</a>')
        else:
            #smallCatePattern = re.compile(r'<a.*?href="/dict_list\?cid=(\d+)(.|\n)*?category2">((.|\n)*?)</a>')
            smallCatePattern = re.compile(r'<a\s*href="/dict_list\?cid.*?cid=(\d+)\s*data-stats="webDictListPage.category2">(.*?)\s*</a>')
        smallResult = re.findall(smallCatePattern, smallData)
        for j in smallResult:
            if bigCateID == "157" and j[0] in bigCateDict: # 防止找城市区划下面的子分类的时候将其他的一级分类都找出来
                continue
            smallCateDict[bigCateID][j[0]] = j[1].strip()
            #print '\t', j[0], j[2].strip()
    return bigCateDict, smallCateDict
    

if __name__ == '__main__':
    bigCateDict, smallCateDict = getBaiduDictCate()
    for bigCateID, bigCate  in bigCateDict.items():
        print bigCateID, bigCate
        for smallCateID, smallCate in smallCateDict[bigCateID].items():
            print '\t', smallCateID, smallCate


