---
layout: post
title: 解决SecureCRT登录服务器Connection closed错误
date: 发布于2018-06-14 10:20:29 +0800
categories: 测试结果杂记
tag: 4
---

症状：使用SecureCRT登录远程服务器失败，返回Connection closed，直接使用ssh命令可以正常登录。

<!-- more -->

解决：打开Session Options界面，选中Connection——SSH2，在右面的Key
exchange分组中，将ecdh开头的几个复选框取消选中，单击OK，如下图所示

![](/styles/images/blog/Solve the SecureCRT login server Connection closed error_1.png)

* content
{:toc}


