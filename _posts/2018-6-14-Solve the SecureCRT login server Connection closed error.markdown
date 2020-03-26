---
layout: post
title: 解决SecureCRT登录服务器Connection closed错误
date: 发布于2018-06-14 10:20:29 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}

症状：使用SecureCRT登录远程服务器失败，返回Connection closed，直接使用ssh命令可以正常登录。
<!-- more -->


解决：打开Session Options界面，选中Connection——SSH2，在右面的Key
exchange分组中，将ecdh开头的几个复选框取消选中，单击OK，如下图所示

![](https://img-
blog.csdn.net/20180614101926790?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)

