---
layout: post
title: Qt的延时函数
date: 发布于2019-11-29 17:57:04 +0800
categories: Qt
tag: 4
---

# 阻塞延时

* content
{:toc}


使用QThread类的msleep、sleep、usleep函数  
<!-- more -->

优点：

  * 使用简单，都是静态函数，引入头文件后可以直接调用
  * 精确度高，可以精确到微秒

缺点

  * 这几个函数的作用是强制当前线程休眠，非ui线程倒是无所谓，如果是ui线程，界面会卡死

# 非阻塞延时

利用Qt的事件循环结合while循环，方法如下

    
    
    QTime timer = QTime::currentTime().addMSecs(frameTime * 1000);
    while (QTime::currentTime() < timer)
    	QCoreApplication::processEvents();
    

优点

  * 非阻塞，可以在ui线程中使用

缺点

  * 实现相对麻烦，需要写好多代码
  * 精度低，只能精确到毫秒

