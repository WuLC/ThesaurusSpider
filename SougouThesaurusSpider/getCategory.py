# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-03-26 22:42:39
# @Last modified by:   LC
# @Last Modified time: 2016-04-11 15:22:46
# @Email: liangchaowu5@gmail.com

# 功能：提取分类ID的和对应的具体类别，以字典形式返回
# bigCateDict 是所有大类ID及其代表内容，smallCateDict是每一类大类下的若干小类

import urllib2
import re

def getSogouDictCate():
    bigCatePattern = re.compile(r"href='/dict/cate/index/(\d+).*?>(.*?)<")  #
    smallCatePattern = re.compile(r'href="/dict/cate/index/(\d+)">(.*?)<')

    bigCateURL = 'http://pinyin.sogou.com/dict/'
    smallCateBaseURL = 'http://pinyin.sogou.com/dict/cate/index/'
    bigCateDict = {}
    smallCateDict = {}

    # 得到大分类
    try:
        response = urllib2.urlopen(bigCateURL)
    except urllib2.HTTPError, e:
        print 'Error while finding bigCate,error code'+e.code
    bigCateData = response.read()
    result = re.findall(bigCatePattern,bigCateData) # 返回一个元组列表，元组的长度由正则表达决定
    for i in result:
        bigCateDict[i[0]] = i[1]

    # 从大分类中得到小分类
    for i in bigCateDict:
        bigCate = i
        smallCateDict[bigCate] = {}  # 小分类的字典
        smallCateURL = smallCateBaseURL+str(i)
        try:
            response = urllib2.urlopen(smallCateURL)
        except urllib2.HTTPError, e:
            print 'Error while finding smallCate,error code'+e.code
        smallCateData = response.read()
        result = re.findall(smallCatePattern,smallCateData)
        for j in result:
            if len(j[1]) == 0:   # 这个分类属于大分类
                continue
            else:
                smallCateDict[bigCate][j[0]] = j[1]
    return bigCateDict, smallCateDict

# 分类列出所有词库
if __name__ == '__main__':
    bigCateDict, smallCateDict = getSogouDictCate()
    for i in bigCateDict:
        for j in smallCateDict[i]:
            print i, bigCateDict[i], j, smallCateDict[i][j]
            




