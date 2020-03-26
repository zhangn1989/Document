---
layout: post
title: Qt槽函数的重入问题
date: 发布于2019-11-29 18:14:36 +0800
categories: Qt
tag: 4
---

* content
{:toc}

在Qt的信号槽机制中，如果一个槽函数的执行时间很长，在槽函数还没有执行结束的时候，有新的信号产生，默认情况下，该次信号不会被丢弃，而是会等槽函数执行结束后再次调用槽函数  
<!-- more -->

但是在某些情况下，如果想将槽函数执行过程中所产生的新信号丢弃掉，有以下两种方法：blockSignals和disconnect  
假设有如下信号槽

    
    
    connect(m_play, &QShortcut::activated, this, &Editor::play);
    

具体方法如下

# blockSignals

    
    
    void Editor::play()
    {
    	m_play->blockSignals(true); // 屏蔽信号
    	// 槽函数实现
    	m_play->blockSignals(false); // 启用信号
    }
    

优点：轻量级实现，占用资源少  
缺点：会屏蔽掉对象的所有信号，无法对单一信号进行控制

# disconnect

    
    
    void Editor::play()
    {
    	disconnect(m_play, &QShortcut::activated, this, &Editor::play);
    	// 槽函数实现
    	connect(m_play, &QShortcut::activated, this, &Editor::play);
    }
    

优点：可以对单一信号进行控制  
缺点：每次都要对信号进行重连，执行效率相对较低

