---
layout: post
title: 正确且优雅的使用QThread
date: 发布于2019-07-10 10:23:31 +0800
categories: Qt
tag: 4
---

我们在写Qt多线程的时候，都会直接重写QThread类的run方法，其实这种方式是Qt的设计者所反对的，它违背了QThread类的设计初衷，QThread的设计者曾发帖说过这个问题，原文找不到了，我们今天来看一下如何在不重写run方法的情况下使用QThread

<!-- more -->

首先是控制类实现

    
    
    //Controller.h
    #ifndef CONTROLLER_H
    #define CONTROLLER_H
    
    #include <QObject>
    
    class QThread;
    class Controller : public QObject
    {
    	Q_OBJECT
    
    public:
    	Controller(QObject *parent = nullptr);
    	~Controller();
    
    	void start();
    
    signals:
    	void operate();
    
    private:
    	QThread *m_pThread;
    };
    
    #endif // CONTROLLER_H
    
    //Controller.cpp
    #include "Controller.h"
    #include "Worker.h"
    #include <QThread>
    
    Controller::Controller(QObject *parent)
    	: QObject(parent)
    {
    	m_pThread = new QThread;
    
    	// 要调用moveToThread的QObject子类实例，不能有父类指针
    	// 因此只能绑定QObject::deleteLater释放内存
    	Worker *pWorker = new Worker;
    	pWorker->moveToThread(m_pThread);
    
    	connect(m_pThread, &QThread::finished, pWorker, &QObject::deleteLater);
    	connect(this, &Controller::operate, pWorker, &Worker::doWork);
    }
    
    Controller::~Controller()
    {
    	if (m_pThread)
    	{
    		m_pThread->requestInterruption();
    		m_pThread->quit();
    		m_pThread->wait();
    
    		delete m_pThread;
    		m_pThread = nullptr;
    	}
    }
    
    void Controller::start()
    {
    	// 启动线程
    	m_pThread->start();
    
    	// 必须用信号曹的方式执行工作
    	// 如果直接调用则不会在线程中工作
    //	m_pWorker->doWork();
    //	emit operate();
    }
    

然后是工作类实现

    
    
    //Worker.h
    #ifndef WORKER_H
    #define WORKER_H
    
    #include <QObject>
    
    class Worker : public QObject
    {
    	Q_OBJECT
    
    public:
    	Worker(QObject *parent = nullptr);
    	~Worker();
    
    	void doWork();
    
    private:
    	
    };
    
    #endif // WORKER_H
    
    //Worker.cpp
    #include "Worker.h"
    #include <stdio.h>
    #include <QThread>
    
    Worker::Worker(QObject *parent)
    	: QObject(parent)
    {
    
    }
    
    Worker::~Worker()
    {
    
    }
    
    void Worker::doWork()
    {
    	while (!QThread::currentThread()->isInterruptionRequested())
    	{
    		QString threadText = QStringLiteral("@0x%1").arg(quintptr(QThread::currentThreadId()), 16, 16, QLatin1Char('0'));
    	//	QString threadText = QString::number(quintptr(QThread::currentThreadId()));
    		printf("worker = %d\n", threadText.toUInt());
    		QThread::sleep(1);
    	}
    }
    

最后是main函数

    
    
    #include <QtCore/QCoreApplication>
    #include "Controller.h"
    #include <QThread>
    
    int main(int argc, char *argv[])
    {
    	QCoreApplication a(argc, argv);
    
    	// 工作信号在哪发射的无所谓，但必须有人发射；
    	// 信号和线程开始谁先调用也无所谓，中间有时间间隔也没影响，
    	// 只有两个都被调用了才会在线程中工作；
    	// 如果先调用线程开始，则线程会启动，但工作代码不执行；
    	// 如果先发射信号，线程不启动，工作代码也不执行，
    	// 只有在线程启动后工作代码才会在线程中执行；
    	// 如果不使用信号而是直接调用工作代码，线程启动与否已经不重要，
    	// 即使线程已经启动，也不会在线程中执行，而是在当前线程中运行
    	Controller *controller = new Controller;
    
    //	emit controller->operate();
    //	QThread::sleep(5);
    	controller->start();
    //	emit controller->operate();
    
    	QThread::sleep(5);
    
    	emit controller->operate();
    	QThread::sleep(5);
    	delete controller;
    
    // 	while (true)
    // 	{
    // 		QString threadText = QString::number(quintptr(QThread::currentThreadId()));
    // 		QByteArray ba = threadText.toLocal8Bit();
    // 		printf("main = %d\n", ba.data());
    // 		QThread::sleep(1);
    // 	}
    
    	return a.exec();
    }
    
    

* content
{:toc}


