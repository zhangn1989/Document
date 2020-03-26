---
layout: post
title: 高并发服务器学习笔记之十二：分布式架构
date: 发布于2019-04-29 11:17:19 +0800
categories: 一步步打造高并发服务器
tag: 4
---

* content
{:toc}

###

  * 简介
<!-- more -->

    * 流量分流
    * 业务分流
    * 集群和分布式的区别与联系
  * 示例程序
    * RPC协议
    * 客户端
    * 加法服务器
    * 乘法服务器
  * 小结

# 简介

在使用多台设备处理海量数据的时候，主要有两种方案：流量分流和业务分流。

## 流量分流

流量分流也就是我们常说的集群架构，这里不细说，可以看一下我之前的文档：[高并发服务器学习笔记之十一：集群架构](https://blog.csdn.net/mumufan05/article/details/80817513)

## 业务分流

业务分流也就是我们常说的分布式架构，是今天的主要内容。  
一个完成的系统，是由多个业务组成，业务之间相互协调来完成工作。而分布式架构区别于传统的集中式架构，就是将不同的业务分别架设在不同的机器上，彼此之间使用RPC协议进行协调工作。

## 集群和分布式的区别与联系

两种架构都是使用多台机器来处理海量数据的解决方案，而且两者经常混在一起使用，并统称为“分布式集群”，因此经常有人将两种概念搞混。集群是流量分流，当大量数据到来，会根据每个节点的闲置情况进行分流处理；分布式是先将业务进行拆分，分别放在不同的节点上，根据处理业务的不同去分配相应业务的节点。  
举个栗子，现在想做这么个事，设计一个集视频播放与直播一体的系统。  
如果采用集群架构，那么就将所有代码都写在一个程序中，分别部署在多台机器上，并用一个发现服务器进行最优节点分配。  
如果采用分布式架构，那么就将直播的代码和视频分别写在两个程序中，然后分别部署，客户端在需要时去连接相应的节点。  
而所谓的“分布式集群”，就是先将业务拆分，采用分布式架构，然后每个业务节点后面又跟着一个集群，是一种综合应用。

# 示例程序

这次我们来做一个简单的数学运算系统，只支持加法和乘法，采用分布式架构，将加法和乘法分别部署在两个节点上，并用RPC协议进行通信。实际开发中，有时候为了一些安全问题，不会将业务分发直接写在客户端，而是用一个业务分发服务器去处理，由于我们只是练习的示例代码，业务分发服务器就不加了，直接将业务分发写在客户端。关于业务节点列表，应给写在一个配置文件里，程序在运行的时候实时读取，我们这里为了简单，直接写死在代码里。  
完整代码[戳这里](https://github.com/zhangn1989/MyRPC)

## RPC协议

简单说就是各个业务节点之间的通信协议，这个协议可以自己定一个私有协议，也可以用一些公开协议，比如JsonRPC，我们这里简单一点，定义一个简单的私有协议，一个结构体，包含两个运算数和一个结果

    
    
    typedef struct __Messages
    {
    	int arg1;
    	int arg2;
    	int result;
    }Message;
    

## 客户端

客户端比较简单，首先向加法服务器发送一个加法运算申请，并等待结果返回，然后再向乘法服务器发送一个乘法运算申请，等待结果返回

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    #include <unistd.h>
    #include <sys/types.h>          /* See NOTES */
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h> /* superset of previous */
    #include <arpa/inet.h>
    
    #include "public_head.h"
    #include "fileio.h"
    
    #define LISTEN_BACKLOG	50
    #define ADD_IP		"127.0.0.1"
    #define ADD_PORT	10086
    #define MUL_IP		ADD_IP
    #define MUL_PORT	10010
    
    int main(int argc, char ** argv)
    {
    	int sockfd = 0;
    	Message addMessage, mulMessage;
    	struct sockaddr_in addServer_addr;
    	struct sockaddr_in mulServer_addr;
    
    	memset(&addServer_addr, 0, sizeof(addServer_addr));
    	memset(&mulServer_addr, 0, sizeof(mulServer_addr));
    	memset(&addMessage, 0, sizeof(Message));
    	memset(&mulMessage, 0, sizeof(Message));
    
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    		handle_error("socket");
    
    	addServer_addr.sin_family = AF_INET;
    	addServer_addr.sin_port = htons(ADD_PORT);
    	inet_pton(sockfd, ADD_IP, &addServer_addr.sin_addr.s_addr);
    
    	addMessage.arg1 = 3;
    	addMessage.arg2 = 5;
    	if (connect(sockfd, (struct sockaddr*) & addServer_addr, sizeof(addServer_addr)) < 0)
    	{
    		close(sockfd);
    		handle_error("connect");
    	}
    
    	write(sockfd, &addMessage, sizeof(Message));
    	read(sockfd, &addMessage, sizeof(Message));
    	printf("%d + %d = %d\n", addMessage.arg1, addMessage.arg2, addMessage.result);
    	sleep(1);
    	close(sockfd);
    
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    		handle_error("socket");
    
    	mulServer_addr.sin_family = AF_INET;
    	mulServer_addr.sin_port = htons(MUL_PORT);
    	inet_pton(sockfd, MUL_IP, &mulServer_addr.sin_addr.s_addr);
    
    	mulMessage.arg1 = 3;
    	mulMessage.arg2 = 5;
    	if (connect(sockfd, (struct sockaddr*) & mulServer_addr, sizeof(mulServer_addr)) < 0)
    	{
    		close(sockfd);
    		handle_error("connect");
    	}
    
    	write(sockfd, &mulMessage, sizeof(Message));
    	read(sockfd, &mulMessage, sizeof(Message));
    	printf("%d x %d = %d\n", mulMessage.arg1, mulMessage.arg2, mulMessage.result);
    	sleep(1);
    	close(sockfd);
    
    	return 0;
    }
    
    

## 加法服务器

加法服务器也比较简单，接收到客户端的加法运算请求后，用客户端给的参数进行加法运算，再将结果返回

    
    
    static void handle_request(int acceptfd)
    {
        ssize_t readret = 0;
    
    	Message message;
       
    	while (1)
    	{
    		memset(&message, 0, sizeof(message));
    		readret = read(acceptfd, &message, sizeof(message));
    		if (readret == 0)
    			break;
    
    		printf("thread id:%lu, recv operation:%d + %d\n", 
    			pthread_self(), message.arg1, message.arg2);
    		message.result = message.arg1 + message.arg2;
    		write(acceptfd, &message, sizeof(message));
    	}
    
        close(acceptfd);
        return;
    }
    

## 乘法服务器

乘法服务器可以如同加法服务器一样简单实现，但我们这里为了演示业务服务器之间的协调工作，乘法采用调用加法服务器进行结果累加去实现

    
    
    static void handle_request(int acceptfd)
    {
    	ssize_t readret = 0;
    	Message message;
    
    	int i = 0;
    	int sockfd = 0;
    	Message addMessage;
    	struct sockaddr_in addServer_addr;
    
    	while (1)
    	{
    		memset(&message, 0, sizeof(message));
    		readret = read(acceptfd, &message, sizeof(message));
    		if (readret == 0)
    			break;
    
    		printf("thread id:%lu, recv operation:%d x %d\n",
    			pthread_self(), message.arg1, message.arg2);
    
    		memset(&addServer_addr, 0, sizeof(addServer_addr));
    		memset(&addMessage, 0, sizeof(Message));
    
    		if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    			handle_error("socket");
    
    		addServer_addr.sin_family = AF_INET;
    		addServer_addr.sin_port = htons(ADD_PORT);
    		inet_pton(sockfd, ADD_IP, &addServer_addr.sin_addr.s_addr);
    
    		if (connect(sockfd, (struct sockaddr*) & addServer_addr, sizeof(addServer_addr)) < 0)
    		{
    			close(sockfd);
    			handle_error("connect");
    		}
    
    		for(i = 0; i < message.arg2; ++i)
    		{
    			addMessage.arg1 = message.arg1;
    			addMessage.arg2 = addMessage.result;
    			write(sockfd, &addMessage, sizeof(Message));
    			readret = read(sockfd, &addMessage, sizeof(Message));
    			sleep(1);
    		}
    		close(sockfd);
    		message.result = addMessage.result;
    
    		write(acceptfd, &message, sizeof(message));
    	}
    
    	printf("\n");
    	close(acceptfd);
    	return;
    }
    
    

# 小结

通过以上代码我们可以看出，采用分布式架构，不但可以进行业务分流，提高数据处理量，更是简化的服务端的代码。分布式架构的难点不在于代码，而在于业务的拆分和RPC协议的制定。业务怎么拆分才合理，能够让各个业务节点的流量达到最佳平衡点，如果一个业务节点经常闲置，另一个业务节点经常爆满，这显然是不合适的，不过这个问题倒是可以通过集群架构进行缓解。

