﻿# 搜狗、百度、QQ输入法词库爬虫

---

用python实现的爬取搜狗、百度、QQ输入法词库的爬虫。各文件夹对应的内容如下

- BaiduTheaurusSpifer： [百度输入法][1]的词库爬虫
- QQTheaurusSpider: [QQ输入法][2]的词库爬虫
- SougouThesaurusSpider： [搜狗输入法][3]的词库爬虫


每个输入法均采用了单线程和多线程实现了爬取功能。多线程的速度要远快于单线程，线程数目建议设为5~10，或者保留默认的设定数5。

通过urllib2、Queue、re、threading等python自带模块实现，无依赖的第三方模块。使用时将`singleThreadDownload.py`（单线程下载）或 `multiThreadDownload.py`(多线程下载)中的主函数中的baseDir改为自己的下载路径即可运行单线程下载或多线程下载,注意baseDir末尾没有/。

如果有下载不成功的文件或解析不成功的页面，在下载根目录会生成下载日志，记录这些文件和页面的URL信息，方便debug。

关于实现的具体细节可参考[这篇文章][4]。

下载的词库文件并非文本格式，而是各个输入法自己定制的二进制格式，关于词库文件的解码并转为文本格式可参考[这个repository][5]。

PULL Request
[1]: http://shurufa.baidu.com/dict.html
[2]: http://dict.qq.pinyin.cn/
[3]: http://pinyin.sogou.com/dict/
[4]: http://wulc.me/2016/03/27/%E6%90%9C%E7%8B%97%E3%80%81%E7%99%BE%E5%BA%A6%E3%80%81QQ%E8%BE%93%E5%85%A5%E6%B3%95%E7%9A%84%E8%AF%8D%E5%BA%93%E7%88%AC%E8%99%AB/
[5]: https://github.com/WuLC/ThesaurusParser

