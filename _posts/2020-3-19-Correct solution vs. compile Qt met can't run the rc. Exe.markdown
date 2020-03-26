---
layout: post
title: 正确解决VS编译Qt遇到无法运行rc.exe问题
date: 发布于2020-03-19 11:59:23 +0800
categories: Qt
tag: 4
---

* content
{:toc}

今天用vs新建一个qt工程，编译的时候发现无法运行“rc.exe”，习惯性的上网找解决办法，找到的都是把rc.exe复制来复制去的，这是绕开问题，不是解决问题。而且我之前的qt工程不用复制rc.exe也能正常编译，只有新建的不行，所以肯定有其他正确解决问题的方法，最简单的就是比较两个工程的配置，看有什么区别。  
<!-- more -->

打开工程属性，看下面的截图  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200319115538676.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
能正常编译的旧工程中的目标平台版本是8.1，而新建的工程默认选择10。很明显，这是sdk版本找的不对的问题，如果用那种瞎复制的办法，虽然能正常编译，但鬼知道会不会有什么隐患，到时候出问题找都找不到。

