#-*- coding: utf-8 -*-
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

if __name__ == '__main__':
    i = 1
    while 1:
        # 每个用户都有这么一个url做为文章列表，后面的数字就是列表分页后的页号
        url = 'https://blog.csdn.net/mumufan05/article/list/' + str(i)
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
