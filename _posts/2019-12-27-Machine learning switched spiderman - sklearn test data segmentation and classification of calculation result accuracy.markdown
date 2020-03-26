---
layout: post
title: 机器学习调包侠：sklearn测试数据切分和计算分类结果准确率
date: 发布于2019-12-27 15:16:23 +0800
categories: 机器学习调包侠
tag: 4
---

* content
{:toc}

# 本篇对应教程

[油管原版](https://www.youtube.com/watch?v=84gqSbLcBFE)，[B站搬运](https://www.bilibili.com/video/av7283864)。这期视频简单介绍了一些分类器学习算法的原理，如果我们需要对坐标系上的点进行分类，那么首先需要创建一条随机的直线，该直线的两侧就是分类的结果。如果训练数据中某个点的落在了直线的另一侧，那么就调整直线的参数从而使直线能够正确划分所有点的，最后的这条直线就是分类器了，测试数据进来后直接根据点在直线的哪一侧来确定点的所属分类，大致就是这么个意思。视频中介绍的神经网络的演示网站挺好玩的，想玩玩的朋友可以[戳这里](http://playground.tensorflow.org)。  
<!-- more -->

由于本系列的目的是当一个调包侠，所以不会着重于原理方面的东西，重点在各种框架的接口怎么用，本节课中出现的两个新接口就是sklearn测试数据切分和计算分类结果准确率，具体看下面的代码

# 代码

    
    
    # 导入测试数据
    from sklearn import datasets
    iris = datasets.load_iris()
    
    X = iris.data
    y = iris.target
    
    # 将测试数据切分成训练集和测试集，这个切分是随机的
    from sklearn.model_selection import  train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .5)
    
    # 导入不同的分类器看效果
    #from sklearn import tree
    #my_classifier = tree.DecisionTreeClassifier()
    from sklearn.neighbors import KNeighborsClassifier
    my_classifier = KNeighborsClassifier()
    
    # 使用训练数据进行训练，然后对测试数据进行分类
    my_classifier.fit(X_train, y_train)
    predictions = my_classifier.predict(X_test)
    
    # 将预测的分类结果和测试集中真实的分类结果进行对比，计算准确率
    from sklearn.metrics import accuracy_score
    print(accuracy_score(y_test, predictions))
    

