---
layout: post
title: Qt的TCP通讯
date: 发布于2020-03-23 11:49:30 +0800
categories: Qt
tag: 4
---

* content
{:toc}

# 基本使用

使用Qt的进行TCP通讯，主要用到两个类，QTcpServer和QTcpSocket。前者主要用于服务端的监听，相当于原始socket中由socket函数创建的监听socket；后者主要用于读写数据，相当于原始socket中由accept函数返回的连接socket。
<!-- more -->


## 服务端的大致使用流程如下：

  1. 创建QTcpServer对象，调用listen函数进行IP和端口号的监听，执行过该函数后，客户端就可以进行连接操作了，创建的服务器直接就是多连接多消息服务器，不需要我们去处理并发连接的问题。
  2. 监听QTcpServer对象的newConnection信号，每当有客户端连接后就会发射该信号
  3. 在newConnection的槽函数中使用nextPendingConnection函数获取连接的客户端，返回值是一个QTcpSocket对象，我们就用该对象和客户端进行数据读写
  4. 得到QTcpSocket对象后绑定该对象的readyRead和disconnected信号，当客户端有数据发送过来时会发射readyRead信号，当客户端断开连接时会发射disconnected信号。

需要注意的是，一般需要在disconnected的槽函数中通过deleteLater函数删除该连接的QTcpSocket对象，如果不进行手动删除，Qt会在QTcpServer对象销毁时自动消除所有连接的QTcpSocket对象，在此之前，那些断开的QTcpSocket对象会一直占用内存，造成内存没必要的浪费。

## 客户端的大致使用流程如下：

  1. 创建QTcpSocket对象，绑定该对象的readyRead和disconnected信号，这点同服务端一样
  2. 调用connectToHost函数连接服务端
  3. 调用waitForConnected或其他函数判断是否连接成功
  4. 在readyRead的槽函数中收发数据
  5. 调用close函数断开连接，销毁该QTcpSocket对象

相对于服务端，客户端的disconnected倒是没那么重要，是否需要处理看情况而定。

# 拆包封包问题

首先需要了解的是readyRead信号的行为，该信号只有在有新数据到来时发射一次，与缓冲区中是否还有未读数据无关。比如发送端一次发来了十个字节的数据，但接收端一次只能读取五个字节，需要在一个信号响应过程中读两次，因为该信号只会发射一次。通常情况下要在槽函数中写一个循环来读取数据，如果缓冲区中的所有数据都读完了，再次调用read函数会返回0字节。  
发送端处理起来比较简单，write函数会将指定的数据无脑写入缓冲区，由Qt自行处理封包拆包问题，比较麻烦的是接收端。  
我们每次发送的数据长度是不确定的，而Qt又不管我们调用过几次write，也不管每次发送多少字节，都是无脑写入缓冲区，这样就可能回造成一个问题，如果每次发送的数据很小，接收端会一次接收到多次write的数据，如果发送的数据很大，接收端一次接收的数据又很可能不完整，需要接收几次才行，甚至还很可能在接收端的一次接收时会接收到两次不完整的数据，第一次的后半段和第二次的前半段。因此在接收端需要进行拆包封包的操作，自行拼凑我们想要的数据。

# 具体例子

我们首先定义一个接收端和发送端共用的数据协议

    
    
    enum ProtocolType
    {
    	TEXT = 0,
    	PICTURE,
    	END,
    	MAX
    };
    
    struct MYBSProtocol
    {
    	int length;
    	ProtocolType type;
    	char data[0];
    };
    

然后是服务端

    
    
    class Server : public QObject
    {
    	Q_OBJECT
    
    public:
    	explicit Server(QObject *parent = nullptr);
    	~Server();
    
    	void startListen(int nPort);
    private:
    	QTcpServer *m_server;
    
    public slots :
    	void onNewConnection();
    	void onReadyRead();
    	void onDisconnected();
    };
    
    Server::Server(QObject *parent)
    	: QObject(parent)
    {
    	m_server = new QTcpServer;
    }
    
    Server::~Server()
    {
    	delete m_server;
    }
    
    void Server::startListen(int nPort)
    {
    	if (m_server->listen(QHostAddress::Any, nPort))
    		qDebug() << "listen port "<< nPort << " ok";
    	else
    		qDebug() << "listen err";
    	connect(m_server, SIGNAL(newConnection()), this, SLOT(onNewConnection()));
    }
    
    void Server::onNewConnection()
    {
    	QTcpSocket *socket = m_server->nextPendingConnection();
    	QString ip = socket->peerAddress().toString();
    	quint16 port = socket->peerPort();
    	qDebug() << "new client connect:" << ip << ":" << port;
    	connect(socket, SIGNAL(readyRead()), this, SLOT(onReadyRead()));
    	connect(socket, SIGNAL(disconnected()), this, SLOT(onDisconnected()));
    }
    
    void Server::onReadyRead()
    {
    	qDebug() << "read client message";
    	QTcpSocket *socket = dynamic_cast<QTcpSocket *>(sender());
    	if (socket)
    	{
    		QByteArray buff;
    		buff = socket->readAll();
    		qDebug() << buff;
    
    		QFile file(buff);
    		if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
    			return;
    
    		while (!file.atEnd())
    		{
    			MYBSProtocol *mp = nullptr;
    			// 处理中文乱码
    			QString line = QString::fromLocal8Bit(file.readLine());
    			QString key = line.left(line.indexOf(':'));
    			QString value = line.mid(line.indexOf(':') + 1);
    
    			if (key == "text")
    			{
    				QByteArray ba = value.toLocal8Bit();
    				mp = (MYBSProtocol *)malloc(sizeof(mp) + ba.size());
    				if (!mp)
    					continue;
    				memset(mp, 0, sizeof(mp) + value.size());
    				mp->type = TEXT;
    				mp->length = ba.size();
    				memcpy(mp->data, ba.data(), mp->length);
    			}
    			else if (key == "picture")
    			{
    				QFile picture(value);
    				if (!picture.open(QIODevice::ReadOnly))
    					continue;
    
    				QByteArray ba = picture.readAll();
    				picture.close();
    
    				mp = (MYBSProtocol *)malloc(sizeof(mp) + ba.size());
    				if (!mp)
    					continue;
    				memset(mp, 0, sizeof(mp) + ba.size());
    
    				mp->type = PICTURE;
    				mp->length = ba.count();
    				memcpy(mp->data, ba.data(), mp->length);
    			}
    			else
    			{
    				continue;
    			}
    
    			socket->write((char *)mp, sizeof(mp) + mp->length);
    			free(mp);
    			mp = nullptr;
    		}
    
    		file.close();
    		MYBSProtocol mp;
    		mp.type = END;
    		mp.length = 0;
    		socket->write(QByteArray(reinterpret_cast<const char *>(&mp), sizeof(mp)));
    	}
    }
    
    void Server::onDisconnected()
    {
    	QTcpSocket *socket = dynamic_cast<QTcpSocket *>(sender());
    	if (socket)
    	{
    		QString ip = socket->peerAddress().toString();
    		quint16 port = socket->peerPort();
    		qDebug() << "client disconnect:" << ip << ":" << port;
    		socket->deleteLater();
    	}
    }
    

最后是客户端，客户端的重点是拆包组包的操作

    
    
    void MainWindow::onPushButtonClicked(bool checked)
    {
    	QString url = ui->lineEdit->text();
    	QString ip = url.left(url.indexOf(':'));
    	QString port = url.mid(url.indexOf(':') + 1, url.indexOf('/') - url.indexOf(':') - 1);
    	QString file = url.mid(url.indexOf('/') + 1);
    
    	QTcpSocket *socket = new QTcpSocket;
    	connect(socket, &QTcpSocket::readyRead, this, &MainWindow::onReadyRead);
    	connect(socket, &QTcpSocket::disconnected, this, &MainWindow::onDisconnected);
    	socket->connectToHost(ip, port.toUInt());
    	if (socket->waitForConnected(-1))
    	{
    		socket->write(file.toUtf8());
    		socket->waitForBytesWritten(-1);
    	}
    	else
    	{
    		QAbstractSocket::SocketError error = socket->error();
    		QString str = socket->errorString();
    		delete socket;
    		socket = nullptr;
    	}
    }
    
    void MainWindow::onReadyRead()
    {
    	QTcpSocket *socket = dynamic_cast<QTcpSocket *>(sender());
    	if (socket)
    	{
    		while (true)
    		{
    			QByteArray buff;
    			int buffLen = 0;
    			MYBSProtocol *mp = nullptr;
    
    			// 如果临时缓冲区为空指针，说明是每条指令的第一次读
    			if (!m_tempBuff)
    			{
    				buff = socket->read(sizeof(MYBSProtocol));
    				buffLen = buff.size();
    				if(buffLen == 0)
    					break;
    				mp = (MYBSProtocol *)buff.data();
    
    				// 防止上次内存申请失败读到抛弃的数据
    				if (mp->type >= MAX)
    					return;
    
    				// 如果内存分配失败，直接关闭socket，这一次的数据全不要了
    				m_tempBuff = (char *)malloc(sizeof(mp) + mp->length);
    				if (!m_tempBuff)
    				{
    					socket->close();
    					socket->waitForDisconnected(-1);
    					m_surplus = 0;
    					return;
    				}
    				memset(m_tempBuff, 0, sizeof(mp) + mp->length);
    
    				memcpy(m_tempBuff, buff.data(), buffLen);
    				m_cursor += buffLen;
    				m_surplus = mp->length;
    			}
    			else
    			{
    				buff = socket->read(m_surplus > m_maxRead ? m_maxRead : m_surplus);
    				buffLen = buff.size();
    
    				// buffLen和m_surplus等于0是数据段长度为0的情况
    				// 防止数据段长度等于零时造成内存泄露
    				if (buffLen == 0 && m_surplus != 0)
    					break;
    				memcpy(m_tempBuff + m_cursor, buff.data(), buffLen);
    				m_cursor += buffLen;
    				m_surplus -= buffLen;
    
    				if (m_surplus == 0)
    				{
    					mp = (MYBSProtocol *)m_tempBuff;
    
    					switch (mp->type)
    					{
    					case TEXT:
    					{
    						QByteArray ba(mp->data, mp->length);
    						QString text = QString::fromLocal8Bit(ba);
    						ui->browseArea->setText(text);
    					}break;
    					case PICTURE:
    					{
    						QPixmap imageresult;
    						QByteArray ba(mp->data, mp->length);
    						imageresult.loadFromData(ba);
    						ui->browseArea->setPixmap(imageresult);
    					}break;
    					case END:
    					{
    						socket->close();
    						socket->waitForDisconnected(-1);
    					}break;
    					default:
    						break;
    					}
    
    					// 函数的最后判断一下是否完整处理过一个组包过程
    					// 如果处理过，释放内存
    					if (m_tempBuff)
    					{
    						free(m_tempBuff);
    						m_tempBuff = nullptr;
    						m_cursor = 0;
    					}
    				}
    			}
    		}
    	}
    }
    
    void MainWindow::onDisconnected()
    {
    	QTcpSocket *socket = dynamic_cast<QTcpSocket *>(sender());
    	if (socket)
    	{
    		QString ip = socket->peerAddress().toString();
    		quint16 port = socket->peerPort();
    		qDebug() << "client disconnect:" << ip << ":" << port;
    		socket->deleteLater();
    	}
    }
    
    

