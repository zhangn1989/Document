---
layout: post
title: Qt遍历目录下的文件
date: 发布于2019-07-10 10:27:28 +0800
categories: Qt
tag: 4
---

* content
{:toc}


    QDir dir("dir");

<!-- more -->
    if (!dir.exists())
    	return a.exec();
    
    QStringList filters("*.abd");
    dir.setFilter(QDir::Files | QDir::NoSymLinks);
    dir.setNameFilters(filters);
    int dir_count = dir.count();
    if (dir_count <= 0)
    	return a.exec();
    
    QFileInfoList list = dir.entryInfoList();
    for (int i = 0; i < list.size(); ++i) {
    	QFileInfo fileInfo = list.at(i);
    	QString fileName = fileInfo.fileName();
    
    	QString m = fileInfo.absoluteFilePath();
    	QString q = fileInfo.absolutePath();
    	QString o = fileInfo.baseName();
    	QString v = fileInfo.bundleName();
    	QString u = fileInfo.canonicalFilePath();
    	QString y = fileInfo.canonicalPath();
    	QString t = fileInfo.completeBaseName();
    	QString r = fileInfo.completeSuffix();
    	QString e = fileInfo.filePath();
    	QString w = fileInfo.path();
    	//对每个文件进行相应的操作
    }
    

