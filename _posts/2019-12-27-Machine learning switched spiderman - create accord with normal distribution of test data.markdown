---
layout: post
title: 机器学习调包侠：创建符合正态分布的测试数据
date: 发布于2019-12-27 14:18:03 +0800
categories: 机器学习调包侠
tag: 4
---

# 本篇对应教程

* content
{:toc}


[油管原版](https://www.youtube.com/watch?v=N9fDIAflCMY)，[B站搬运](https://www.bilibili.com/video/av7253344)。原版教程其实是介绍特征的好坏的，但是我觉得这个看一遍就懂了，没什么值得做笔记的，倒是视频中创建正态分布测试数据的例子值得记录一下
<!-- more -->


# 代码

    
    
    import numpy as np
    import matplotlib.pyplot as plt
    
    # 定义样本数量，两种各500，共1000
    greyhounds = 500
    labs = 500
    
    # np.random.randn()功能是返回一组满足标准正态分布的随机值
    # 也就是说这组数据的平均值是0，标准差是1，且满足正态分布
    # 一个参数时表示的是这一组随机值一共有指定参数个
    # 本例中的4表示的是将标准差从1放大到4，28表示的是将平均值从0调整为28
    # 最后的结果就是生成一组平均值为28，标准差为4，且满足正态分布的随机数，这组数共有500个数据
    grey_height = 28 + 4 * np.random.randn(greyhounds)
    lab_height = 24  + 4 * np.random.randn(labs)
    
    plt.hist([grey_height, lab_height], stacked = True, color = ['r', 'b'])
    plt.show()
    

