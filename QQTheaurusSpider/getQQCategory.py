# -*- coding: utf-8 -*-
# @Author: LC
# @Date:   2016-03-26 22:42:39
# @Last modified by:   LC
# @Last Modified time: 2016-04-11 15:22:13
# @Email: liangchaowu5@gmail.com

# 得到QQ输入法的词库分类

import urllib2
import re

def getCategory():
    baseURL = 'http://dict.qq.pinyin.cn'
    try:
        response = urllib2.urlopen(baseURL)
    except urllib2.HTTPError,e:
        print str(e.code)+' while parsing page '+baseURL
    except:
        print 'unexpected error while parsing page '+baseURL

    cateData = response.read()
    bigCatePattern = re.compile('"/dict_list\?sort1=(.*?)" class="title"')
    bigCateList = re.findall(bigCatePattern,cateData)
    cateDict = {}  # 存储一级分类和二级分类的字典，key为一级分类，value为一级分类下的二级分类,value为List类型
    for bigCate in bigCateList:
        cateDict[bigCate.decode('gbk')] = []  # 网页采用了gbk编码
        # 找到大分类下的小分类
        smallCatePattern = re.compile('"/dict_list\?sort1=%s&sort2=(.*?)"'%bigCate)
        smallCateList = re.findall(smallCatePattern, cateData)
        for smallCate in smallCateList:
            cateDict[bigCate.decode('gbk')].append(smallCate.decode('gbk'))
    return cateDict



if __name__ == '__main__':
    category = getCategory()
    for bigCate in category:
        for smallCate in category[bigCate]:
            print bigCate,smallCate,isinstance(bigCate,unicode),isinstance(smallCate,unicode)
