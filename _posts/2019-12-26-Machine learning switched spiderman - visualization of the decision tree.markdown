---
layout: post
title: 机器学习调包侠：可视化决策树
date: 发布于2019-12-26 18:41:02 +0800
categories: 机器学习调包侠
tag: 4
---

# 本篇对应教程

* content
{:toc}


[油管原版](https://www.youtube.com/watch?v=tNa99PG8hR8)，[B站搬运](https://www.bilibili.com/video/av7214214)
<!-- more -->


# 测试数据

本节课要生成一个可视化的决策树，不能再用上一节那个简单的例子了，本节课我们使用机器学习领域中一个很经典的数据——鸢尾属植物数据集（Iris flower
data set），该数据集的相关介绍[戳这里](https://en.wikipedia.org/wiki/Iris_flower_data_set)。

# scikit-learn的数据集

Iris flower data set作为一个经典数据集，scikit-learn中已经集成了，不需要我们自己去创建，使用scikit-
learn的数据集模块直接引用即可。关于scikit-learn的数据集模块这里不多说，读者可自行查阅相关文档。

# 决策树的可视化

这里需要说明的是，可视化这部分功能已经更新，视频中的方法已经不再适用，对细节没兴趣的读者可以直接拷贝本篇的代码，想了解细节的朋友可以自行查阅[官方文档](https://scikit-
learn.org/stable/modules/tree.html)。另外还有一点要注意，新版本的可视化需要安装graphviz相关的二进制文件以及相应的python模块，graphviz的二进制文件可以去[官网下载](http://www.graphviz.org)，相应的python模块可以用下面的命令进行安装

    
    
    pip install graphviz
    

# 代码

    
    
    import numpy as np
    # 引入决策树算法
    from sklearn import tree
    # 引入数据集
    from sklearn.datasets import load_iris
    # 引入可视化模块
    import graphviz
    
    # 导入测试数据
    iris = load_iris()
    
    # 先从测试数据集中删除第0、50、100条这3条数据
    # 并将删除后的数据集作为训练数据集
    # 训练结束后用删除掉的数据当做测试数据验证学习的准确性
    test_idx = [0, 50, 100]
    train_target = np.delete(iris.target, test_idx)
    train_data = np.delete(iris.data, test_idx, axis = 0)
    
    # 将删除的数据当做测试数据
    test_target = iris.target[test_idx]
    test_data = iris.data[test_idx]
    
    # 像上一节一样训练数据
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(train_data, train_target)
    
    # 对比原数据的结果和训练后的结果
    print(test_target)
    print(clf.predict(test_data))
    
    # 训练结束后，生成pdf格式的可视化决策树
    dot_data = tree.export_graphviz(clf, out_file=None, 
          feature_names=iris.feature_names,  
          class_names=iris.target_names,  
          filled=True, rounded=True,  
          special_characters=True)
    graph = graphviz.Source(dot_data)
    graph.render("iris")
    
    

# 查看决策树

![决策树](https://img-blog.csdnimg.cn/20191226183902305.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
决策树的策略简单说就是判断输入数据的某个特征是否满足某些条件，满足的走一个分支，不满足的走另一个分支，直到将路径走完，这里不做太详细的说明。

