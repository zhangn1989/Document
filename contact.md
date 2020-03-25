---
layout: copy
title: 联系我
date: 2020-03-25 13:15:15 +0800
permalink: /contact/
---
<h1><a id="_0"></a>基本使用</h1>
<p>使用Qt的进行TCP通讯，主要用到两个类，QTcpServer和QTcpSocket。前者主要用于服务端的监听，相当于原始socket中由socket函数创建的监听socket；后者主要用于读写数据，相当于原始socket中由accept函数返回的连接socket。</p>
<h2><a id="_2"></a>服务端的大致使用流程如下：</h2>
<ol>
<li>创建QTcpServer对象，调用listen函数进行IP和端口号的监听，执行过该函数后，客户端就可以进行连接操作了，创建的服务器直接就是多连接多消息服务器，不需要我们去处理并发连接的问题。</li>
<li>监听QTcpServer对象的newConnection信号，每当有客户端连接后就会发射该信号</li>
<li>在newConnection的槽函数中使用nextPendingConnection函数获取连接的客户端，返回值是一个QTcpSocket对象，我们就用该对象和客户端进行数据读写</li>
<li>得到QTcpSocket对象后绑定该对象的readyRead和disconnected信号，当客户端有数据发送过来时会发射readyRead信号，当客户端断开连接时会发射disconnected信号。</li>
</ol>
<p>需要注意的是，一般需要在disconnected的槽函数中通过deleteLater函数删除该连接的QTcpSocket对象，如果不进行手动删除，Qt会在QTcpServer对象销毁时自动消除所有连接的QTcpSocket对象，在此之前，那些断开的QTcpSocket对象会一直占用内存，造成内存没必要的浪费。</p>
<h2><a id="_11"></a>客户端的大致使用流程如下：</h2>
<ol>
<li>创建QTcpSocket对象，绑定该对象的readyRead和disconnected信号，这点同服务端一样</li>
<li>调用connectToHost函数连接服务端</li>
<li>调用waitForConnected或其他函数判断是否连接成功</li>
<li>在readyRead的槽函数中收发数据</li>
<li>调用close函数断开连接，销毁该QTcpSocket对象</li>
</ol>
<p>相对于服务端，客户端的disconnected倒是没那么重要，是否需要处理看情况而定。</p>
<h1><a id="_21"></a>拆包封包问题</h1>
<p>首先需要了解的是readyRead信号的行为，该信号只有在有新数据到来时发射一次，与缓冲区中是否还有未读数据无关。比如发送端一次发来了十个字节的数据，但接收端一次只能读取五个字节，需要在一个信号响应过程中读两次，因为该信号只会发射一次。通常情况下要在槽函数中写一个循环来读取数据，如果缓冲区中的所有数据都读完了，再次调用read函数会返回0字节。<br>
发送端处理起来比较简单，write函数会将指定的数据无脑写入缓冲区，由Qt自行处理封包拆包问题，比较麻烦的是接收端。<br>
我们每次发送的数据长度是不确定的，而Qt又不管我们调用过几次write，也不管每次发送多少字节，都是无脑写入缓冲区，这样就可能回造成一个问题，如果每次发送的数据很小，接收端会一次接收到多次write的数据，如果发送的数据很大，接收端一次接收的数据又很可能不完整，需要接收几次才行，甚至还很可能在接收端的一次接收时会接收到两次不完整的数据，第一次的后半段和第二次的前半段。因此在接收端需要进行拆包封包的操作，自行拼凑我们想要的数据。</p>
<h1><a id="_26"></a>具体例子</h1>
<p>我们首先定义一个接收端和发送端共用的数据协议</p>