---
layout: post
title: 深扒Qt信号槽（Windows平台）
date: 发布于2019-08-08 12:39:10 +0800
categories: Qt
tag: 4
---

在上一篇[简单实现Qt的信号槽](https://blog.csdn.net/mumufan05/article/details/98499694)中，我们简单模拟了Qt的信号槽，从信号发出到槽函数调用我们已经基本了解了，但一些Qt自带的信号是怎么发射出来的呢？今天我们就来深扒一下。  

<!-- more -->
为了方便起见，我们先找一张Qt继承关系图  
![常用Qt类图](/styles/images/blog/Dig deep Qt signal channel (Windows)_1.png)  
上图为网上找的，原图连接[在这里](https://www.processon.com/view/5758f23de4b080e40c7feaca)，侵删  
然后，我们随便建个Qt工程，添加一个pushButton，并绑定clicked信号，将断点下在我们的槽函数上，调试程序，点击pushButton，程序会断在我们的槽函数，并得到从main函数开始的调用堆栈，我们逐层的观察  
![堆栈调用图](/styles/images/blog/Dig deep Qt signal channel (Windows)_2.png)  
在堆栈的最底层是WinMain函数，没做过windows开发的小伙伴可能会对这个函数感到陌生，这个是windows应用程序的入口函数，我们来看一下这个函数

    
    
    extern "C" int APIENTRY WinMain(HINSTANCE, HINSTANCE, LPSTR /*cmdParamarg*/, int /* cmdShow */)
    {
        int argc;
        wchar_t **argvW = CommandLineToArgvW(GetCommandLineW(), &argc);
        if (!argvW)
            return -1;
        char **argv = new char *[argc + 1];
        for (int i = 0; i < argc; ++i)
            argv[i] = wideToMulti(CP_ACP, argvW[i]);
        argv[argc] = Q_NULLPTR;
        LocalFree(argvW);
        const int exitCode = main(argc, argv);
        for (int i = 0; i < argc && argv[i]; ++i)
            delete [] argv[i];
        delete [] argv;
        return exitCode;
    }
    

这个函数主要是处理的命令行参数，然后调用Qt工程自动创建的main函数，该函数没做什么特别的事情，主要是处理跨平台问题，可以不用多研究，我们继续往上层走  
这一层来到了我们最熟悉的main函数，通常这个函数做的事情也不多，而且主要都是我们自己要做的事，也就不贴代码了，值得深扒也就有是return
a.exec();这么一句，正好堆栈也停留在这一句上，我们继续往上走，看a.exec()函数干了什么  
我们跳了几层看到，a.exec()只是不断的调用父类的方法，直到QCoreApplication::exec才是真正的函数实现，我们来看一下这个函数

    
    
    int QCoreApplication::exec()
    {
        if (!QCoreApplicationPrivate::checkInstance("exec"))
            return -1;
    
        QThreadData *threadData = self->d_func()->threadData;
        if (threadData != QThreadData::current()) {
            qWarning("%s::exec: Must be called from the main thread", self->metaObject()->className());
            return -1;
        }
        if (!threadData->eventLoops.isEmpty()) {
            qWarning("QCoreApplication::exec: The event loop is already running");
            return -1;
        }
    
        threadData->quitNow = false;
        QEventLoop eventLoop;
        self->d_func()->in_exec = true;
        self->d_func()->aboutToQuitEmitted = false;
        int returnCode = eventLoop.exec();
        threadData->quitNow = false;
        if (self) {
            self->d_func()->in_exec = false;
            if (!self->d_func()->aboutToQuitEmitted)
                emit self->aboutToQuit(QPrivateSignal());
            self->d_func()->aboutToQuitEmitted = true;
            sendPostedEvents(0, QEvent::DeferredDelete);
        }
    
        return returnCode;
    }
    

上面的代码就是处理程序的消息循环，我想大家对消息循环应该不陌生，这里不做多说，通过查看堆栈信息，我们可以看到，堆栈停留在int returnCode =
eventLoop.exec();这一句上，Qt程序也是阻塞在这一句上，这里一定会有一个while循环，我们继续往上走，找到这个while循环  
我们运气不错，往上走了一层，在eventLoop.exe()就找到了这个while循环

    
    
        while (!d->exit.loadAcquire())
            processEvents(flags | WaitForMoreEvents | EventLoopExec);
    

写过windows程序的朋友，一定对下面的代码不会陌生

    
    
    while (GetMessage(&msg, NULL, 0, 0))
    {
    	TranslateMessage(&msg);
    	DispatchMessage(&msg);
    }
    

没错，这就是windows程序必备的消息循环，Qt中也一定会存在这个消息循环，while我们已经找到了，那么GetMessage，TranslateMessage和DispatchMessage在什么地方呢？不用想都知道，GetMessage一定在!d->exit.loadAcquire()中，而TranslateMessage和DispatchMessage一定在processEvents中，我们来找到它们  
首先在while
(!d->exit.loadAcquire())一行下个断点，重新启动调试程序，将程序断在这里，然后跟进去，可当我们根据去后发现，最深层的是这么一个函数

    
    
        template <typename T> static void orderedMemoryFence(const T &) Q_DECL_NOTHROW
        {
        }
    

what the fuсk???are you fucking kidding
me???啪啪打脸有木有？？？GetMessage应该（我已经不敢说一定了）有啊，在哪里？启用搜索大法，以GetMessage为关键字，在Qt源码中找找看有什么结果  
经过查找后，排除大量不太可能的结果，最终定位到下面这个函数

    
    
    void QEventDispatcherWin32::installMessageHook()
    {
        Q_D(QEventDispatcherWin32);
    
        if (d->getMessageHook)
            return;
    
    #ifndef Q_OS_WINCE
        // setup GetMessage hook needed to drive our posted events
        d->getMessageHook = SetWindowsHookEx(WH_GETMESSAGE, (HOOKPROC) qt_GetMessageHook, NULL, GetCurrentThreadId());
        if (!d->getMessageHook) {
            int errorCode = GetLastError();
            qFatal("Qt: INTERNAL ERROR: failed to install GetMessage hook: %d, %s",
                   errorCode, qPrintable(qt_error_string(errorCode)));
        }
    #endif
    }
    

原来是设置了消息钩子，难怪找不到，通过堆栈信息，是在QApplication初始化的时候调用的。GetMessage已经找到了，我们继续找找看TranslateMessage和DispatchMessage  
回到eventLoop.exe()的while循环，找到processEvents函数跟进去，同样的跳过意义不大的子类重载，我们来到了QEventDispatcherWin32::processEvents函数，在这个函数中我们发现了熟悉的MSG
msg和PeekMessage，以及qt_GetMessageHook等钩子函数，并且找到了TranslateMessage和DispatchMessage

    
    
    if (!filterNativeEvent(QByteArrayLiteral("windows_generic_MSG"), &msg, 0)) {
          TranslateMessage(&msg);
          DispatchMessage(&msg);
    }
    

看来这里就是处理windows消息循环的核心位置了，并且将windows消息循环转换为Qt的事件响应  
windows消息循环的问题我们到此为止，接下来我们继续分析pushButton的信号是怎么发出的  
跟着最开始的槽函数的堆栈继续往上走，跳过我们不感兴趣去的函数调用，来到了QGuiApplicationPrivate::processWindowSystemEvent，函数实现如下

    
    
    void QGuiApplicationPrivate::processWindowSystemEvent(QWindowSystemInterfacePrivate::WindowSystemEvent *e)
    {
        switch(e->type) {
        case QWindowSystemInterfacePrivate::FrameStrutMouse:
        case QWindowSystemInterfacePrivate::Mouse:
            QGuiApplicationPrivate::processMouseEvent(static_cast<QWindowSystemInterfacePrivate::MouseEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::Wheel:
            QGuiApplicationPrivate::processWheelEvent(static_cast<QWindowSystemInterfacePrivate::WheelEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::Key:
            QGuiApplicationPrivate::processKeyEvent(static_cast<QWindowSystemInterfacePrivate::KeyEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::Touch:
            QGuiApplicationPrivate::processTouchEvent(static_cast<QWindowSystemInterfacePrivate::TouchEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::GeometryChange:
            QGuiApplicationPrivate::processGeometryChangeEvent(static_cast<QWindowSystemInterfacePrivate::GeometryChangeEvent*>(e));
            break;
        case QWindowSystemInterfacePrivate::Enter:
            QGuiApplicationPrivate::processEnterEvent(static_cast<QWindowSystemInterfacePrivate::EnterEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::Leave:
            QGuiApplicationPrivate::processLeaveEvent(static_cast<QWindowSystemInterfacePrivate::LeaveEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::ActivatedWindow:
            QGuiApplicationPrivate::processActivatedEvent(static_cast<QWindowSystemInterfacePrivate::ActivatedWindowEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::WindowStateChanged:
            QGuiApplicationPrivate::processWindowStateChangedEvent(static_cast<QWindowSystemInterfacePrivate::WindowStateChangedEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::WindowScreenChanged:
            QGuiApplicationPrivate::processWindowScreenChangedEvent(static_cast<QWindowSystemInterfacePrivate::WindowScreenChangedEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::ApplicationStateChanged: {
            QWindowSystemInterfacePrivate::ApplicationStateChangedEvent * changeEvent = static_cast<QWindowSystemInterfacePrivate::ApplicationStateChangedEvent *>(e);
            QGuiApplicationPrivate::setApplicationState(changeEvent->newState, changeEvent->forcePropagate); }
            break;
        case QWindowSystemInterfacePrivate::FlushEvents: {
            QWindowSystemInterfacePrivate::FlushEventsEvent *flushEventsEvent = static_cast<QWindowSystemInterfacePrivate::FlushEventsEvent *>(e);
            QWindowSystemInterface::deferredFlushWindowSystemEvents(flushEventsEvent->flags); }
            break;
        case QWindowSystemInterfacePrivate::Close:
            QGuiApplicationPrivate::processCloseEvent(
                    static_cast<QWindowSystemInterfacePrivate::CloseEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::ScreenOrientation:
            QGuiApplicationPrivate::reportScreenOrientationChange(
                    static_cast<QWindowSystemInterfacePrivate::ScreenOrientationEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::ScreenGeometry:
            QGuiApplicationPrivate::reportGeometryChange(
                    static_cast<QWindowSystemInterfacePrivate::ScreenGeometryEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::ScreenLogicalDotsPerInch:
            QGuiApplicationPrivate::reportLogicalDotsPerInchChange(
                    static_cast<QWindowSystemInterfacePrivate::ScreenLogicalDotsPerInchEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::ScreenRefreshRate:
            QGuiApplicationPrivate::reportRefreshRateChange(
                    static_cast<QWindowSystemInterfacePrivate::ScreenRefreshRateEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::ThemeChange:
            QGuiApplicationPrivate::processThemeChanged(
                        static_cast<QWindowSystemInterfacePrivate::ThemeChangeEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::Expose:
            QGuiApplicationPrivate::processExposeEvent(static_cast<QWindowSystemInterfacePrivate::ExposeEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::Tablet:
            QGuiApplicationPrivate::processTabletEvent(
                        static_cast<QWindowSystemInterfacePrivate::TabletEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::TabletEnterProximity:
            QGuiApplicationPrivate::processTabletEnterProximityEvent(
                        static_cast<QWindowSystemInterfacePrivate::TabletEnterProximityEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::TabletLeaveProximity:
            QGuiApplicationPrivate::processTabletLeaveProximityEvent(
                        static_cast<QWindowSystemInterfacePrivate::TabletLeaveProximityEvent *>(e));
            break;
    #ifndef QT_NO_GESTURES
        case QWindowSystemInterfacePrivate::Gesture:
            QGuiApplicationPrivate::processGestureEvent(
                        static_cast<QWindowSystemInterfacePrivate::GestureEvent *>(e));
            break;
    #endif
        case QWindowSystemInterfacePrivate::PlatformPanel:
            QGuiApplicationPrivate::processPlatformPanelEvent(
                        static_cast<QWindowSystemInterfacePrivate::PlatformPanelEvent *>(e));
            break;
        case QWindowSystemInterfacePrivate::FileOpen:
            QGuiApplicationPrivate::processFileOpenEvent(
                        static_cast<QWindowSystemInterfacePrivate::FileOpenEvent *>(e));
            break;
    #ifndef QT_NO_CONTEXTMENU
            case QWindowSystemInterfacePrivate::ContextMenu:
            QGuiApplicationPrivate::processContextMenuEvent(
                        static_cast<QWindowSystemInterfacePrivate::ContextMenuEvent *>(e));
            break;
    #endif
        case QWindowSystemInterfacePrivate::EnterWhatsThisMode:
            QGuiApplication::postEvent(QGuiApplication::instance(), new QEvent(QEvent::EnterWhatsThisMode));
            break;
        default:
            qWarning() << "Unknown user input event type:" << e->type;
            break;
        }
    }
    

我们可以看到，这里就是Qt事件分发的核心位置了，由于我们是鼠标点击事件，所以会走QGuiApplicationPrivate::processMouseEvent函数的分支，这也是我们此行的主要目标，我们先跟进去看看  
由于该函数太长，我们就不贴代码了，说道那句再贴那句吧，在该函数中，我们看到了这么一句

    
    
    QMouseEvent ev(type, localPoint, localPoint, globalPoint, button, buttons, e->modifiers, e->source);
    

看到这个QMouseEvent大家应该都熟悉了，我们重写的一些时间方法传进去的event就是在这里构造的  
我们继续往上走，跳过我们不关心的堆栈层，来到了QPushButton::event这一层，现在函数调用到了QPushButton类了，那么Qt是怎么调到这个类的呢？我们向下回退一层堆栈，回到了QApplicationPrivate::notify_helper函数，在该函数中有这么一句

    
    
    bool consumed = receiver->event(e);
    

可见，这个receiver就是QPushButton的实例，那么这个实例是怎么来的呢？我们继续回退，来到QWidgetWindow::handleMouseEvent，在这个函数中我们找到了receiver构造的位置

    
    
        // which child should have it?
        QWidget *widget = m_widget->childAt(event->pos());
        QPoint mapped = event->pos();
    
        if (!widget)
            widget = m_widget;
    
        if (event->type() == QEvent::MouseButtonPress)
            qt_button_down = widget;
    
        QWidget *receiver = QApplicationPrivate::pickMouseReceiver(m_widget, event->windowPos().toPoint(), &mapped, event->type(), event->buttons(), qt_button_down, widget);
    

看来，在这里就能找到我们点击的是哪个widget了，并将指针层层上传  
接下来我们回到QPushButton::event，到了这里，应该就离我们的目标不远了，我们继续往上走，来到的父类的QWidget::event，在这里，我们看到了下面的代码

    
    
    case QEvent::MouseButtonRelease:
            mouseReleaseEvent((QMouseEvent*)event);
            break;
    

猜测QPushButton应该就是重写的QWidget的mouseReleaseEvent方法，并在这里调用的，是不是这样呢？我们再往上走一层，来到QAbstractButton::mouseReleaseEvent，可以看出，并不是QPushButton重写了QWidget的mouseReleaseEvent方法，而是QAbstractButton重写了QWidget的mouseReleaseEvent方法  
我们继续往上走，来到了QAbstractButtonPrivate::emitClicked()，我们看一下该函数的实现

    
    
    void QAbstractButtonPrivate::emitClicked()
    {
        Q_Q(QAbstractButton);
        QPointer<QAbstractButton> guard(q);
        emit q->clicked(checked);
    #ifndef QT_NO_BUTTONGROUP
        if (guard && group) {
            emit group->buttonClicked(group->id(q));
            if (guard && group)
                emit group->buttonClicked(q);
        }
    #endif
    }
    

这里有一句emit
q->clicked(checked);，就是我们此行的目标了，在这里就调用了QPushButton的clicked信号。再往下走看clicked的实现，发现没有源码，该函数实现在moc_qabstractbutton.cpp中，这就来到了moc生成的代码中了，再继续往下走就和之前我们分析Qt信号槽的路径一样了，详见[简单实现Qt的信号槽](https://blog.csdn.net/mumufan05/article/details/98499694)  
至此，我们的旅程圆满结束，由于本人目前的工作主要是在windows平台上，因此本次只分析了windows平台的实现，等以后有时间再来分析linux平台的实现。

* content
{:toc}


