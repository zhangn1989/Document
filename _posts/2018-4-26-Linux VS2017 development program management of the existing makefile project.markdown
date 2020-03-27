---
layout: post
title: VS2017开发Linux程序之管理已有的makefile工程
date: 发布于2018-04-26 16:11:20 +0800
categories: VS2017开发Linux程序
tag: 4
---

上一篇简单介绍了vs2017新建一个linux的工程，本编将介绍一下如何管理已有的makefile工程，如果你想了解新建工程该如何操作，请点击下面的连接：

<!-- more -->

https://blog.csdn.net/mumufan05/article/details/80093732

本篇以unzip的源码工程为例进行介绍，将unzip的源码解压后我们没有在源码的根目录下找到makefile，需要手动将unix目录下的Makefile拷贝到根目录下，并在终端执行“make
unzip”进行编译。

如果您的工程还没有makefile，请根据您的工程结构，搞出一个makefile，现在我假设您已经准备好了makefile了，好，我们开始。

首先，我们要做的第一件事就是想办法让你的linux和Windows进行文件共享，用什么方式不重要，只要能让你的Windows能够想访问本地文件一样去访问linux上的文件就可以，关于这一点，请您自行百度。

然后，请去https://github.com/robotdad/vclinux这个页面下载vclinux，这是微软官方提供的shell脚本，可以根据makefile生成vs的工程文件。

下载完成后放到linux上进行解压，找到bash目录中的两个脚本文件，并执行这两个脚本，命令格式如下

    
    
    $ ./genvcxproj.sh 工程目录 xxx.vcxproj
    
    
    $ ./genfilters.sh 工程目录 xxx.vcxproj.filters

具体内容相见压缩包中的README.md

执行完上面两条命令，就会在工程目录下生成vs的工程文件，用vs打开这个工程，然后在打开工程是属性页面，点击常规，在右边找到远程生成根目录，修改为linux工程目录所在的目录，注意是工程目录所在的目录，而不是工程文件所在的目录，比如我将unzip.tar.gz放在了/home/user/work目录，解压后会在该目录下多出来一个unzip目录用来存放unzip的工程文件，我们这里要修改的目录是/home/user/work，而不是/home/user/work/unzip，这里一定要注意，如下图

![](https://img-
blog.csdn.net/20180426155744422?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

然后单击远程生成选项，在右面配置程序的生成命令，清理命令，重新生成命令，如下图

![](https://img-
blog.csdn.net/20180426160106184?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

最后，我们再配置一下调试选项，点击调试，在右边配置可执行程序的路径，运行参数，工作目录等，如下图所示

![](https://img-
blog.csdn.net/20180426160347420?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

至此，所有的配置都完成了，以上所有配置内容都可以根据自己的习惯进行相应的修改，调试的时候如果涉及到终端的输入输出，可以在调试菜单中找到linux控制台，使用微软提供的那个简陋的模拟终端。

用了两天，感觉这次vs2017提供的linux程序开发，完全符合微软东西的特点：好用吗？好用，真TM好用，功能很强大，用的爽吗？不爽，非常的不爽，因为超级卡。每次启动编译和启动调试的时候都非常的慢，不过这个慢也是可以理解的，毕竟编译和调试都是在远程linux上进行的。不过这次的2017可以模块安装，完全可以根据自己的需要进行定制，倒是没有以前版本那么臃肿了。

更多内容详见微软的官方博客文章https://blogs.msdn.microsoft.com/vcblog/2016/03/30/visual-c-
for-linux-development/

=====================================================================

用了一段时间，发现启动编译和启动调试都非常慢是Visual Assist X的锅，把插件禁掉就很快了。但对于用习惯Visual Assist
X插件的用户来说，把它禁掉也是一件十分蛋疼的事，所以就看个人的取舍了。

* content
{:toc}


