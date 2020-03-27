---
layout: post
title: Jekyll + Github Pages + CSDN迁移脚本 = 自己的云笔记
date: 发布于2020-03-27 11:49:30 +0800
categories: 测试结果杂记
tag: Python, 爬虫
---


* content
{:toc}

折腾了几天，将sbdn上的文章转移到gayhub pages上，做个简要笔记，以后sbdn上不再更新，转移到gayhub pages，新地址[戳这里](https://zhangn1989.github.io)，废话不多说，直接开始

<!-- more -->

# gayhub部分

 1. 创建gayhub帐号，然后新建一个名为```用户名.github.io```的存储库，**注意，存储库的名称一定要是这个形式的，否则后期访问处理路径问题是很麻烦的**
 2. 向存储出中添加一个index.html或者README.md
 3. 进入settings，往下拉，找到设置GitHub Pages的位置，将Source中的None改成主分支
 4. 如果有自己的域名可以在设置GitHub Pages的位置进行域名绑定，然后就可以通过该域名进行访问了，如果没有自己的域名，则使用```用户名.github.io```进行访问
 5. 在浏览器中输入自己绑定的域名或```用户名.github.io```就会返回之前添加的index.html或者README.md的主页
 
 至此，一个静态网站已经建成，大家可以自己去丰富自己的网站
# Jekyll部分
我们要做一个云笔记，如果每更新一篇文章都写一个html未免有些太蛋疼，Jekyll的作用就是创建一个静态网站的框架，并将Markdown文档直接转换为html，当Jekyll架设好之后，之后我们只要写自己的Markdown笔记就行了，写完笔记后上传到指定目录等待Jekyll编译完成就可以在网页上访问了
使用下面的命令就可以在本地搭建一个测试环境了

```bash
~ $ gem install jekyll
~ $ jekyll new myblog
~ $ cd myblog
~/myblog $ jekyll serve
# => Now browse to http://localhost:4000
```

该命令会自动生成一个Jekyll的demo，并会搭建一个简单的测试环境，可以在本地预览效果。
熟悉前端的同学可以自己配置一个自己喜欢的网站，对网站颜值没要求的也可以直接用这个demo，既关心颜值，也不想自己动手的也可以去找别人做好分享的，自己拿过来简单改点信息就能用了。这里推荐一个专门分享模版的网站[Jekyll Themes](http://jekyllthemes.org)，除此之外，也可以去逼呼、gayhub上找。如果想自己做模版，可以去Jekyll的官网上看官方文档，中英文的都有，中文文档[在这里](http://jekyllcn.com)。
模版配置完成后就将所有文件上传到```用户名.github.io```存储库，**注意：_site和.jekyll-cache不要上传。**之后更新笔记的时候只要将笔记上传到_posts目录下即可

# 从sbdn转移到Jekyll
直接上脚本，注意修改成自己的url

```python
#-*- coding: utf-8 -*-

# 脚本功能：批量爬取sbdn某一用户下所有文章并转为包含jekyll文件头的Markdown文档，支持获取文中图片并修改为本地url
# 整体思路：简单分析sbdn的页面，在前台的html上包含所有想要的信息，只要分析html上的信息进行检索即可
#         每个用户都有一个查询所有文章列表的url，其组成就是固定路径加分页索引，简单循环枚举即可获取所有文章列表信息
#         在文章列表页面上，每篇文章的列表信息中又包含有文章的URL，可以直接读取，然后爬取文章的页面
#         从文章的页面中，可以读取包括文章内容在内的所有想要的信息
#         取出标题、时间、分类、文章内容等所需信息，其中文章内容要保留html的文件格式，其他信息可以直接读取内容
#         通过html2text库将html格式的文章内容转换为Markdown格式
#         找到文章中的图片URL，下载图到本地，然后将sbdn的图片URL转换为本地图片的URL
#         再用所有信息组拼成包含包含jekyll文件头的Markdown文档，并以标题名为文件名保存到本地
#         由于jekyll对中文路径支持的不好，需要将中文文件名翻译成英文，并转换所有非法文件名字符，本例调用的是有道翻译的网络接口
# 不足之处：没找到标签信息，转换后标签信息丢失
#         文档转换过程中，代码部分丢失语言信息，任何语言的代码都是统一格式
# 意外收获：删除本地保存部分，可以用来刷sbdn的阅读量
# 原始连接：https://github.com/zhangn1989/zhangn1989.github.io.git
# 联系作者：zhangnan6419@163.com
#          https://github.com/zhangn1989
#          https://zhangn1989.github.io

import re
import time
import requests
import html2text
import urllib.request
import urllib.parse
import json
from translate import Translator
from bs4 import BeautifulSoup

def translateChinese2English(chinese):
    # 网上找到的代码，使用有道翻译的接口来翻译文件名
    url='http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&sessionFrom=http://fanyi.youdao.com/'
    data = {        #表单数据
                'i': chinese,
                'from': 'AUTO',
                'to': 'AUTO',
                'smartresult': 'dict',
                'client': 'fanyideskweb',
                'doctype': 'json',
                'version': '2.1',
                'keyfrom': 'fanyi.web',
                'action': 'FY_BY_CLICKBUTTION',
                'typoResult': 'false'
            }
    data=urllib.parse.urlencode(data).encode('utf-8')
    response=urllib.request.urlopen(url,data)
    html=response.read().decode('utf-8')
    target=json.loads(html)
    english = target['translateResult'][0][0]['tgt']
    return english

def getHtmlElement(html):
    title = "1"
    date = "2"
    categories = "3"
    tag = "4"
    text = "5"

    soup=BeautifulSoup(html,'lxml')
    title = soup.select('#mainBox > main > div.blog-content-box > div > div > div.article-title-box > h1')[0].get_text().strip()
    date = soup.select('#mainBox > main > div.blog-content-box > div > div > div.article-info-box > div.up-time')[0].get_text().strip()
    categories = soup.select('#mainBox > main > div.blog-content-box > div > div > div.article-info-box > div.slide-content-box > div.tags-box.artic-tag-box > a')[0].get_text().strip()
#    tag = soup.select('')[0].get_text().strip()
    text = str(soup.select('#content_views')[0])

    return title, date, categories, tag, text

def html2Markdown(html):
    #从html中分析出标题分类等信息
    title, date, categories, tag, text = getHtmlElement(html)

    timeArray = time.strptime(date, "发布于%Y-%m-%d %H:%M:%S")

    # 添加jekyll的文件头
    mdText = "---\n"
    mdText += "layout: post\n"
    mdText += "title: " + title + "\n"
    mdText += "date: " + date + " +0800\n"
    mdText += "categories: " + categories + "\n"
    mdText += "tag: " + tag + "\n"
    mdText += "---\n\n"

    # 将html转换为Markdown格式的文本
    body = html2text.html2text(text)
    # 找出正文的第一段
    lst = body.split('\n')
    i = 0
    for item in lst:
        if(len(item) == 0 or item[0] == '#'):
            i = i + 1
            continue
        break
    while 1:
        if(len(lst[i]) != 0):
            break
        i = i + 1
    content = lst[i]

    # 找到正文的第一段的开始和结束的位置
    index = body.index(content)
    pos = index + len(content) + 1
    body = list(body)

    # 取正文的第一段做摘要
    body.insert(index - 1, '\n* content\n{:toc}\n\n')
    # 在正文的第一段后面添加摘要分割信息
    body.insert(pos, '\n<!-- more -->\n')

    # 将list转换回文本
    mdText += "".join(body)

    # 本脚本使用文章标题作为文件名
    # 由于jekyll对中文路径支持不好
    # 需要使用在线翻译将中文文件名翻译成英文
    # 在翻译的过程中会遇到一些非法的文件名字符
    # 需要将这些非法字符转换成合法的    
    title = title.replace('：', '-')
    fileName = translateChinese2English(title)
    if(title == 'C++11的一个格式化字符串的黑科技'):
        fileName = 'Tech of a formatted string in C++11'
    fileName = fileName.replace('/', '')

    # 转换完的图片url会多一个\n字符，需要将其删除从而得到正确的图片url
    # 每找到一个图片的url就要下载一副图片并用文档同名文件名进行保存
    # 同时还要将原文章中的url替换为本地图片的地址
    results=re.findall(r'\!\[([^\]]*)\]\(([^)]+)\)', mdText)
    i = 1
    for item in results:
        url = item[1];
        r = requests.get(url.replace('\n', ''))
        image = fileName + '_' + str(i) + '.png'
        with open(image, 'wb') as f:
            f.write(r.content) 
        f.close()
        text = text.replace(url, '/styles/images/blog/' + image)
        i = i + 1

    # 文档转换成，写入本地文件
    fp = open(str(timeArray.tm_year) + "-" + str(timeArray.tm_mon) + "-" + str(timeArray.tm_mday) + "-" + fileName + ".markdown", "w", encoding='UTF-8')
    fp.write(mdText)
    fp.close()

def getSbdnPosts():
    i = 1
    while 1:
        # 每个用户都有这么一个url做为文章列表，后面的数字就是列表分页后的页号
        url = 'https://blog.sbdn.net/mumufan05/article/list/' + str(i)
        strhtml = requests.get(url)
        soup=BeautifulSoup(strhtml.text,'lxml')
        # 如果页号超出范围（比如只有3页但访问到第4页）返回的页面回包含下面这个信息，如果返回的页面有这个信息说明所有页面遍历完成，可以退出了
        if(len(soup.select('#mainBox > main > div.no-data.d-flex.flex-column.justify-content-center.align-items-center')) != 0):
            break
        # 循环遍历所有的文章列表分页，找出没一个分页的文章列表
        postsList = soup.select('#mainBox > main > div.article-list')[0].contents
        for posts in postsList:
            # 通过分析列表页面中每篇文章的信息，获取文章的url
            if(posts == '\n' or posts.a == None):
                continue
            postsURL = posts.a.get('href')
            postsName = posts.a.get_text()
            print("正在爬取文章：" + str(postsName))
            strhtml = requests.get(postsURL)
            # 获取到每篇文章的页面信息后将其转换为Markdown文档
            html2Markdown(strhtml.text)
        i = i + 1  

if __name__ == '__main__':
    getSbdnPosts()

```
