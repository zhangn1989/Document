---
layout: post
title: 深扒QProcess
date: 发布于2020-01-20 12:24:50 +0800
categories: Qt
tag: 4
---

临近年关，春节前的一周时间都没什么事，每天上班光明正大的摸鱼。但一周都没事做也不免有些无聊。为了打发无聊的时间，翻出我珍藏多年的移动硬盘，在硬盘的某个快被遗忘的角落，翻出了一个我多年以前刚开始学C语言时在网上淘到的一个双管道后门程序。这个后门程序当时我是看不懂的，随手丢在了角落吃灰，这么多年过去了，我觉得我应该能看得懂了，就翻出来研究一下。  

<!-- more -->
其大致原理是这样的：先在本地起一个监听socket，然后开启两个管道，运行cmd程序，并将管道1的读端绑定到cmd的标准输入，管道2的写端绑定到cmd的标准输出和错误输出。然后远程想要用后门了，需要连接这个socket，连接成功后，发送一条命令，比如是dir。后门程序通过socket读到了这条命令，然后把socket读到的命令写入到管道1的写端。还记得管道1的读端在哪不？就是绑定在cmd的标准输入。cmd进程发现管道有数据了，就会读取这条数据，然后执行相应的命令，并将结果写入到管道2的写端。然后后门程序发现管道2的写端有数据了，就读出来。最后通过socket将cmd的返回结果发送给远程。  
看到这里，突然联想到，QProcess读取进程的输出是不是也用管道实现的呢？写段代码跟踪一下

    
    
    QProcess proc;
    proc.start("C:/WINDOWS/system32/cmd.exe", QStringList("/c") << "dir\r\n");
    
    if (proc.state() == QProcess::NotRunning)
    {
    	LOG_ERROR("failed to start %s: %s", exe.toLocal8Bit().data(), QMetaEnum::fromType<QProcess::ProcessError>().valueToKey(proc.error()));
    	return false;
    }
    
    proc.waitForFinished(-1);
    
    QByteArray message = proc.readAllStandardOutput().trimmed();
    
    

这段代码很简单，是QProcess的一个常见用法，先执行某个进程，然后等待进程结束，最后读取该进程的输出内容。  
接下来要做的是跟进去每个函数，看这些函数都做了什么。

# 启动进程

首先是构造函数，构造函数没什么可说的，就是一些变量的初始化。  
start函数进去后，跳过那些不重要的代码，直接来到QProcessPrivate::startProcess函数内，这才是启动进程的关键位置。QProcessPrivate是不对用户开放的类，但却是QProcess的真正核心，QProcess的很多功能都在QProcessPrivate中实现的。先来看一下QProcessPrivate::startProcess的实现，下面代码删除了该函数内不太重要的内容，只保留真正核心功能，后面的所有Qt的代码段都是这么处理的，完整实现请自行参阅Qt源码

    
    
    void QProcessPrivate::startProcess()
    {
        pid = new PROCESS_INFORMATION;
        memset(pid, 0, sizeof(PROCESS_INFORMATION));
    
        if (!openChannel(stdinChannel) ||
            !openChannel(stdoutChannel) ||
            !openChannel(stderrChannel))
            return;
            
        DWORD dwCreationFlags = (GetConsoleWindow() ? 0 : CREATE_NO_WINDOW);
        dwCreationFlags |= CREATE_UNICODE_ENVIRONMENT;
        STARTUPINFOW startupInfo = { sizeof( STARTUPINFO ), 0, 0, 0,
                                     (ulong)CW_USEDEFAULT, (ulong)CW_USEDEFAULT,
                                     (ulong)CW_USEDEFAULT, (ulong)CW_USEDEFAULT,
                                     0, 0, 0,
                                     STARTF_USESTDHANDLES,
                                     0, 0, 0,
                                     stdinChannel.pipe[0], stdoutChannel.pipe[1], stderrChannel.pipe[1]
        };
        success = CreateProcess(0, (wchar_t*)args.utf16(),
                                0, 0, TRUE, dwCreationFlags,
                                environment.isEmpty() ? 0 : envlist.data(),
                                workingDirectory.isEmpty() ? 0 : (wchar_t*)QDir::toNativeSeparators(workingDirectory).utf16(),
                                &startupInfo, pid);
    
        if (stdinChannel.pipe[0] != INVALID_Q_PIPE) {
            CloseHandle(stdinChannel.pipe[0]);
            stdinChannel.pipe[0] = INVALID_Q_PIPE;
        }
        if (stdoutChannel.pipe[1] != INVALID_Q_PIPE) {
            CloseHandle(stdoutChannel.pipe[1]);
            stdoutChannel.pipe[1] = INVALID_Q_PIPE;
        }
        if (stderrChannel.pipe[1] != INVALID_Q_PIPE) {
            CloseHandle(stderrChannel.pipe[1]);
            stderrChannel.pipe[1] = INVALID_Q_PIPE;
        }
    }
    

## 创建管道

该函数中，我们首先看这个if判断

    
    
    if (!openChannel(stdinChannel) ||
        !openChannel(stdoutChannel) ||
        !openChannel(stderrChannel))
            return;
    

从名字上可以看出来，openChannel的功能是初始化标准输入，标准输出和标准错误。当我们跟进去这个函数后，跳过一些不太关心的内容，发现函数中又调用了一个叫做qt_create_pipe的函数，从名字上就能看出，这个函数就是在创建管道。具体是怎么做的呢？我们跟进去看看

    
    
    static void qt_create_pipe(Q_PIPE *pipe, bool isInputPipe)
    {
        SECURITY_ATTRIBUTES secAtt = { sizeof(SECURITY_ATTRIBUTES), 0, false };
    
        HANDLE hServer;
        wchar_t pipeName[256];
        unsigned int attempts = 1000;
        forever {
            _snwprintf(pipeName, sizeof(pipeName) / sizeof(pipeName[0]),
                    L"\\\\.\\pipe\\qt-%X", qrand());
    
            DWORD dwOpenMode = FILE_FLAG_OVERLAPPED;
            DWORD dwOutputBufferSize = 0;
            DWORD dwInputBufferSize = 0;
            const DWORD dwPipeBufferSize = 1024 * 1024;
            if (isInputPipe) {
                dwOpenMode |= PIPE_ACCESS_OUTBOUND;
                dwOutputBufferSize = dwPipeBufferSize;
            } else {
                dwOpenMode |= PIPE_ACCESS_INBOUND;
                dwInputBufferSize = dwPipeBufferSize;
            }
            DWORD dwPipeFlags = PIPE_TYPE_BYTE | PIPE_WAIT;
            if (QSysInfo::windowsVersion() >= QSysInfo::WV_VISTA)
                dwPipeFlags |= PIPE_REJECT_REMOTE_CLIENTS;
            hServer = CreateNamedPipe(pipeName,
                                      dwOpenMode,
                                      dwPipeFlags,
                                      1,                      // only one pipe instance
                                      dwOutputBufferSize,
                                      dwInputBufferSize,
                                      0,
                                      &secAtt);
        }
    
        secAtt.bInheritHandle = TRUE;
        const HANDLE hClient = CreateFile(pipeName,
                                          (isInputPipe ? (GENERIC_READ | FILE_WRITE_ATTRIBUTES)
                                                       : GENERIC_WRITE),
                                          0,
                                          &secAtt,
                                          OPEN_EXISTING,
                                          FILE_FLAG_OVERLAPPED,
                                          NULL);
        ConnectNamedPipe(hServer, NULL);
    
        if (isInputPipe) {
            pipe[0] = hClient;
            pipe[1] = hServer;
        } else {
            pipe[0] = hServer;
            pipe[1] = hClient;
        }
    }
    

先来说该函数的两个参数，该函数在上一层openChannel函数中的调用方式是qt_create_pipe(channel.pipe,
true);，channel的pipe成员是一个有两个元素的int数组，熟悉管道的朋友应该都知道，这个数组就是存放管道两端的文件描述符。第一个参数就是该数组的指针，第二个参数是标记读端和写端的顺序，这个不理解先不着急，我们来看qt_create_pipe的实现就理解了，这里我们先记住，标准输入是true，标准输出和标准错误是false。  
纵观整个函数，都是在创建管道。首先看`DWORD dwOpenMode =
FILE_FLAG_OVERLAPPED;`这一句，变量dwOpenMode是用来指定管道的样式，这里首先给了一个FILE_FLAG_OVERLAPPED标记，该标记表示这条管道是异步的。然后我们需要关心下面这个if判断

    
    
    if (isInputPipe) {
    	 dwOpenMode |= PIPE_ACCESS_OUTBOUND;
    	    dwOutputBufferSize = dwPipeBufferSize;
    	} else {
    	    dwOpenMode |= PIPE_ACCESS_INBOUND;
    	    dwInputBufferSize = dwPipeBufferSize;
    	}
    

变量isInputPipe就是该函数的第二个形参，还记得吗？标准输入是true，标准输出和标准错误是false。PIPE_ACCESS_OUTBOUND和PIPE_ACCESS_INBOUND都是标记管道读写方向的，PIPE_ACCESS_OUTBOUND是数据只能从服务端流向客户端，PIPE_ACCESS_INBOUND是数据只能从客户端流向服务端。  
接下来是通过CreateNamedPipe函数来创建管道，这个是windows系统的原生API，函数的返回值就是管道句柄，如果你是纯粹linux码驴，不了解windows系统编程，你可以理解为这是管道的其中一端的文件描述符。  
然后是通过CreateFile函数打开这个管道，这个也是windows系统的原生API，该函数返回管道的另一端文件句柄，linux码驴也可以理解为这是管道的另一端的文件描述符。  
这时候纯粹的linux码驴可能已经蒙逼了，彻底搞不清管道的哪端是读端，哪端是写端了。确定读端还是写端关键看dwOpenMode变量是标记了PIPE_ACCESS_OUTBOUND还是标记了PIPE_ACCESS_INBOUND，看前面的介绍，这两个标记定义管道数据的流向，不了解windows开发的朋友可以理解为CreateNamedPipe返回的文件句柄就是服务端，CreateFile返回的文件句柄就是客户端。看上面的代码，hServer就是服务端句柄，hClient就是客户端句柄。  
这里多说一句，在linux下叫文件描述符，在windows下叫文件句柄或资源句柄，其实都是差不多的东西，下面我会混用两种叫法，大家知道是一个东西就行。  
对于标准输入，函数的第二个形参为true，标记为PIPE_ACCESS_OUTBOUND，就是hServer是写端，hClient是读端，标准输出和错误输出同理相反。  
管道创建完毕后调用ConnectNamedPipe函数等待管道连接，由于这里标记了FILE_FLAG_OVERLAPPED，所以管道是异步的，不会堵塞。  
这里和windows的常规管道用法还是略有不同的，这里不做深究，有兴趣的朋友可以自行查阅MSDN的相关章节。  
以上是windows平台的实现，linux平台的实现代码我也看了，基本流程差不多，只是具体体统原生API不同。  
最后的那个if判断就是确定管道数组的读端和写端，不管创建时的读端和写端是怎么定义的，通过这个if以后，第一个文件描述符就是读端，第二个就是写端。  
至此管道创建完成，我们回到QProcessPrivate::startProcess()函数，由于有三个标准输入输出，所以一共创建了三条管道，分别对应创建进程和当前进程的三个标准输入输出。之前的后门程序只用了两条管道是将标准输出和标准出错共用一条管道，Qt程序为了更严谨所以用了三条管道，各自一条。

## 创建进程

管道创建完成该是创建进程了，windows系统的原生API是CreateProcess函数，windows的API经常搞一大堆参数，CreateProcess也同样有很多参数，幸运的是这里我们只要关心其中的两个就可以了。首先是第5个参数，该参数标记创建的子进程是否要复制父进程的文件句柄，true就是复制，行为和linux的fork函数一样，这里给的就是true，也就是继承。然后看倒数第二个参数，也就是结构体startupInfo的参数位置，这里需要一个STARTUPINFOW结构体，同样有好多成员，同样的我们只关心其中最后的三个，后三个分别对应标准输入，标准输出和标准出错。子进程会从标准输入的文件句柄读取数据，然后将程序的正确输出写入标准输出句柄，错误输出写如到标准错误句柄。这里就是使用之前创建的管道的相应端的文件句柄，还记得吗？不管是哪个标准输入输出的管道，都是0为读端，1为写端，所以程序中是这样赋值的`stdinChannel.pipe[0],
stdoutChannel.pipe[1], stderrChannel.pipe[1]`  
最后的三个if就将绑定到子进程的管道句柄关闭，这样父进程与子进程就使用了三条管道进行连接，各自保留三条管道中的一端，进程启动并运行。

# 等待进程结束

回到最开始的QProcess的使用代码，通过QProcess的start函数启动线程后，需要调用QProcess的
waitForFinished函数来等待进程结束，那么这个函数又做了什么呢？我们继续跟进去看一下。  
跟进去后我们发现，该函数的真正核心功能还是在QProcessPrivate中实现的，具体代码如下，同样删除掉错误判断等待超时的代码，只保留我们所关心的

    
    
    bool QProcessPrivate::waitForFinished(int msecs)
    {
        forever {
            if (!stdinChannel.buffer.isEmpty() && !_q_canWrite())
                return false;
            if (stdinChannel.writer && stdinChannel.writer->waitForWrite(0))
                timer.resetIncrements();
            if (stdoutChannel.reader && stdoutChannel.reader->waitForReadyRead(0))
                timer.resetIncrements();
            if (stderrChannel.reader && stderrChannel.reader->waitForReadyRead(0))
                timer.resetIncrements();
            if (WaitForSingleObject(pid->hProcess, timer.nextSleepTime()) == WAIT_OBJECT_0) {
                drainOutputPipes();
                if (pid)
                    _q_processDied();
                return true;
            }
        }
        return false;
    }
    
    

该函数主要做两件事，第一是检查三条管道是否有数据可读写，然后调用WaitForSingleObject一段时间看进程是否结束，如果结束，则调用drainOutputPipes函数处理管道数据，然后退出。如果没有结束则进行下一次循环，检查管道数据。WaitForSingleObject也是windows的原生API，这里不多研究，有兴趣的朋友请自行查阅MSDN。  
那么Qt是怎么检查管道数据的呢？我们继续深入扒一扒  
本次跟踪遇到了点麻烦，当调用堆栈跟踪到QWindowsPipeReader::waitForNotification一层时，由于该函数调用了一个windows原生API——SleepEx，SleepEx函数的功能是阻塞当前线程，直到超时或者指定条件发生，这里是等待有I/O系统回调产生，这回导致程序走到了外部代码，无法继续深入。最后使用搜索大法，最终定位到QWindowsPipeReader::checkPipeState()函数，大家在自己调试的时候记得在这个函数下个断点，其具体内容如下

    
    
    DWORD QWindowsPipeReader::checkPipeState()
    {
        DWORD bytes;
        if (PeekNamedPipe(handle, NULL, 0, NULL, &bytes, NULL)) {
            return bytes;
        } else {
            if (!pipeBroken) {
                pipeBroken = true;
                emit pipeClosed();
            }
        }
        return 0;
    }
    

这里我们只需要关心一个函数——PeekNamedPipe，该函数也是windows原生API，作用是检查管道是否有数据可以读写，如果有，QWindowsPipeReader::checkPipeState返回可读写的字符长度，如果没有就返回0。  
函数断下后，我们继续单步走完该函数，然后回到上一层的QWindowsPipeReader::startAsyncRead()，这里有些东西是我们感兴趣的，该函数的关键代码如下

    
    
    void QWindowsPipeReader::startAsyncRead()
    {
        const DWORD minReadBufferSize = 4096;
        DWORD bytesTo
        Read = qMax(checkPipeState(), minReadBufferSize);
        if (pipeBroken)
            return;
    
        if (readBufferMaxSize && bytesToRead > (readBufferMaxSize - readBuffer.size())) {
            bytesToRead = readBufferMaxSize - readBuffer.size();
            if (bytesToRead == 0) {
                // Buffer is full. User must read data from the buffer
                // before we can read more from the pipe.
                return;
            }
        }
    
        char *ptr = readBuffer.reserve(bytesToRead);
    
        stopped = false;
        readSequenceStarted = true;
        overlapped.clear();
        if (!ReadFileEx(handle, ptr, bytesToRead, &overlapped, &readFileCompleted)) {
            readSequenceStarted = false;
    
            const DWORD dwError = GetLastError();
            switch (dwError) {
            case ERROR_BROKEN_PIPE:
            case ERROR_PIPE_NOT_CONNECTED:
                // It may happen, that the other side closes the connection directly
                // after writing data. Then we must set the appropriate socket state.
                pipeBroken = true;
                emit pipeClosed();
                break;
            default:
                emit winError(dwError, QLatin1String("QWindowsPipeReader::startAsyncRead"));
                break;
            }
        }
    }
    

该函数的主要功能是，先检查管道中可读写数据的大小，然后判断是否大于4096，从而确定本次需要读取多大的内容。然后调用windows的原生API——ReadFileEx来读取管道内容。  
这里有一个关键的问题，就是管道中读取的内容存放在哪了？通过函数接口可以确定写入到ptr指向的内存，但ptr指向哪呢？我们找到ptr的定义`char *ptr
=
readBuffer.reserve(bytesToRead);`，可以看出关键的存储位置是在readBuffer内的，而readBuffer又是什么鬼？原来是QWindowsPipeReader的成员变量，而QWindowsPipeReader又是怎么和管道关联起来的呢？我们找到QWindowsPipeReader的构造函数，并在该构造函数上下断点，重启启动程序，程序断在QWindowsPipeReader的构造函数后，通过条用堆栈，找到该类的构造位置是在openChannel函数中，在该函数中有一句`stdoutChannel.reader
= new QWindowsPipeReader(q);`，这样，就将前后整个流程都串上了。

# 读取缓存

最后在用户层接口中，我们只需要调用QProcess的readAllStandardOutput函数就能将管道输出的内容读出来了，至于readAllStandardOutput和QWindowsPipeReader又是怎么关联的这是Qt框架设计的问题了，这里就不深扒了。

# 总结

QProcess读取子进程的输出就是用管道实现了，原理和管道后门程序一样，只不过Qt做的更严谨，需要考虑的问题更多，所以代码更复杂。

* content
{:toc}


