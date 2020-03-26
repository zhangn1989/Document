---
layout: post
title: VS2017开发Linux程序之新建工程
date: 发布于2018-04-26 15:22:23 +0800
categories: VS2017开发Linux程序
tag: 4
---

* content
{:toc}

使用vs2017开发linux程序，首先要安装linux开发组件，可以在安装时就选中，也可以在安装完成后使用在线安装工具进行安装，如下图所示，选中那只企鹅。
<!-- more -->


![](https://img-
blog.csdn.net/20180426144328162?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

新建程序比较简单，在文件>新建>项目中找到Visual C++>跨平台>Linux，在右侧选择相应的项目即可

![](https://img-
blog.csdn.net/20180426144744787?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

其中空项目就是一个空白的，一个文件都没有的工程，创建好以后自行添加文件

控制台项目比空项目多一个main.cpp，是一个可以直接编译通过的简单代码

闪烁是某个开发板的嵌入式工程，好像是Inetl的一个开发板，示例程序可以点亮一个LED

生成文件项目是一个依赖linux工具集的项目，主要是使用linux工具链来编译程序

新建好工程后，第一次编译会让你登录远程linux服务器，输入IP、用户名、密码后就可以像编译调试Windows程序一样去编译调试linux程序了。

工程默认会在远程linux服务器的~/projects路径下创建一个工程目录，用来拷贝源代码，存放中间文件和目标文件，可以在工程属性界面进行修改，如下图

![](https://img-
blog.csdn.net/20180426150229772?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

以上是默认选项，可以根据自己的需要进行修改。如果不想在linux上复制源码，可以点击左侧的复制源，在复制源界面的复制源选项中把是改成否。

如果linux的版本比较老，编译器不支持最新的语言标准，可以在左侧的c++>语言页面进行修改。

在安装VS2017时，会安装一些linux的头文件，但是并不全，有些头文件没有，需要将linux机器上/usr/include目录下的文件，拷贝到Windows机器上，并将拷贝的目录添加到工程的引用目录。我比较懒，直接拷贝到了VS2017默认的linux头文件目录下，即

C:\Program Files (x86)\Microsoft Visual
Studio\2017\Enterprise\Common7\IDE\VC\Linux\include\usr\include

如果程序运行需要终端，可以在vs的系统菜单中找到 调试>linux控制台
来打开一个模拟终端，这是一个非常简陋的终端，只能显示程序的输入和输出，如果要给调试程序输入运行时参数，请在属性页面的调试，程序参数选项中进行指定，此外，还可以在工作目录选项中指定linux程序的工作目录。

本篇先简单介绍这么多，下一篇将一unzip的源码为例，介绍如何编译一个已有的makefile工程。

更多内容详见微软的官方博客文章https://blogs.msdn.microsoft.com/vcblog/2016/03/30/visual-c-
for-linux-development/

