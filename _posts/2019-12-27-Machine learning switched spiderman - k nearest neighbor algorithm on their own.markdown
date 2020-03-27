---
layout: post
title: 机器学习调包侠：自己动手实现k最近邻算法
date: 发布于2019-12-27 17:56:04 +0800
categories: 机器学习调包侠
tag: 4
---

* content
{:toc}

# 本篇对应教程

[油管原版](https://www.youtube.com/watch?v=AoeEHqVSNOw)，[B站搬运](https://www.bilibili.com/video/av7325584)

<!-- more -->

# k最近邻算法

虽说本系列以调包为主，不过也不妨碍找个最简单的算法实现一下找找感觉  
最近邻指的是，测试数据进来后，找到和其最近的一个训练数据，并将其判定为是该训练数据的同类。如果遇到测试数据与两个训练数据的距离都相等，且这两个训练数据分属于两个类的情况，怎么判定测试数据的种类呢？一种方法就是给该测试数据随机指定一个类型，另一种做法则是按距离由近至远多选几个训练数据，看哪个种类的训练数据个数更多就判定训练数据为哪种类型，而选取的训练数据的个数就是所谓的k值。这里需要说明的是，本例中做的是点分类，而一个点只包含x和y两个特征，所以使用平面两点间距离公式来计算距离。由于两点间距离公式可以向高维无限扩展，所以该算法针对更多特征的数据分类也是适用的。  
视频中为了简化，只给了k值为1的算法，我们来扩展一下，做一个可以指定k值的分类算法。

# 代码

    
    
    from scipy.spatial import distance
    
    def euc(a, b):
          return distance.euclidean(a, b)
    
    class ScrappyKNN():
          def fit(self, k, X_train, y_train):
                self.k = k
                self.X_train = X_train
                self.y_train = y_train
    
          def predict(self, X_test):
                predictions = []
                for row in X_test:
                      label = self.closest(row)
                      predictions.append(label)
                return predictions
    
          def closest(self, row):
                best_dists = []
                best_indexs = []
                for i in range(0, self.k):
                      best_indexs.append(i)
                      best_dists.append(euc(row, self.X_train[i]))
               
                for i in range(self.k, len(self.X_train)):
                      dist = euc(row, self.X_train[i])
                      if dist < max(best_dists):
                            index = best_dists.index(max(best_dists))
                            del best_indexs[index]
                            del best_dists[index]
                            best_indexs.append(i)
                            best_dists.append(dist)
    
                lst = []
                for i in range(0, self.k):
                      lst.append(self.y_train[best_indexs[i]])
    
                return max(lst, key=lst.count)
    
    # 导入测试数据
    from sklearn import datasets
    iris = datasets.load_iris()
    
    X = iris.data
    y = iris.target
    
    # 将测试数据切分成训练集和测试集，这个切分是随机的
    from sklearn.model_selection import  train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .5)
    
    my_classifier = ScrappyKNN()
    
    # 使用训练数据进行训练，然后对测试数据进行分类
    my_classifier.fit(3, X_train, y_train)
    predictions = my_classifier.predict(X_test)
    
    # 将预测的分类结果和测试集中真实的分类结果进行对比，计算准确率
    from sklearn.metrics import accuracy_score
    print(accuracy_score(y_test, predictions))
    

