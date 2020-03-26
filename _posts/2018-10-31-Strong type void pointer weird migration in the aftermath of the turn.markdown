---
layout: post
title: void类型指针强转后发生诡异偏移
date: 发布于2018-10-31 17:29:27 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}

先上代码，操作系统centos6.5，gcc版本4.4.7 20120313，纯C代码
<!-- more -->


    
    
    int EvoSdtpImsiMIExt(void *arg, void *user)
    {
        (void)user;
        EvoCallInfo *evi = (EvoCallInfo *)arg;
        uint32_t imsi_len   = EvoSdtpFieldsGetBCD(evi, 0, imsi);
    }
    

EvoCallInfo是一个自定义的结构体，在外部malloc了一块内存，通过void
_指针进行函数传递，在EvoSdtpImsiMIExt再强转回EvoCallInfo_
，然后再用该指针调用EvoSdtpFieldsGetBCD函数，然后在EvoSdtpFieldsGetBCD中使用该结构。  
那么问题来啦  
在EvoSdtpFieldsGetBCD函数中一调用EvoCallInfo指针程序就挂掉了  
然后定位了问题产生的原因，问题出现在EvoCallInfo _evi = (EvoCallInfo _)arg;这一句上，将void_
类型的arg指针强专成EvoCallInfo_类型的evi时，指针变量值发生诡异的位移，每次都向前位移了0x50个字节  
下图是gdb调试信息，堆栈位于EvoSdtpImsiMIExt函数  
![在这里插入图片描述](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9pbWctYmJzLmNzZG4ubmV0L3VwbG9hZC8yMDE4MTAvMzEvMTU0MDk1MDk1Ml80MDkyOTIucG5n?x-oss-
process=image/format,png)

在EvoSdtpFieldsGetBCD堆栈中，如果使用函数传进来的指针程序就挂掉，强行查看正确地址内存数据并没有问题  
下图是gdb调试信息，堆栈位于EvoSdtpFieldsGetBCD函数  
![在这里插入图片描述](https://imgconvert.csdnimg.cn/aHR0cHM6Ly9pbWctYmJzLmNzZG4ubmV0L3VwbG9hZC8yMDE4MTAvMzEvMTU0MDk1MTI4Nl84NzU1MS5wbmc?x-oss-
process=image/format,png)

变量evi和eci有一个错误输入，大家忽略这个细节

如果不用中间变量中转，直接使用arg调用函数就没问题，下面是可以运行的代码

    
    
    int EvoSdtpImsiMIExt(void *arg, void *user)
    {
        (void)user;
        uint32_t imsi_len   = EvoSdtpFieldsGetBCD((EvoCallInfo *)arg, 0, imsi);
    }
    

一直想不通为什么会产生这个bug，指针在进行强转的时候还会发生偏移？大家有没有遇到过类似的问题？请大家帮忙分析一下问题产生的原因

