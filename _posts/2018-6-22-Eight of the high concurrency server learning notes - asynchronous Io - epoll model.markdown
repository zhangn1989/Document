---
layout: post
title: 高并发服务器学习笔记之八：异步IO——epoll模型
date: 发布于2018-06-22 16:28:57 +0800
categories: 一步步打造高并发服务器
tag: 4
---

* content
{:toc}

epoll是Linux下多路复用IO接口select/poll的增强版本，它能显著提高程序在大量并发连接中只有少量活跃的情况下的系统CPU利用率，因为它会复用文件描述符集合来传递结果而不用迫使开发者每次等待事件之前都必须重新准备要被侦听的文件描述符集合，另一点原因就是获取事件的时候，它无须遍历整个被侦听的描述符集，只要遍历那些被内核IO事件异步唤醒而加入Ready队列的描述符集合就行了。

<!-- more -->

目前epell是linux大规模并发网络程序中的热门首选模型。epoll除了提供select/poll那种IO事件的电平触发（Level
Triggered）外，还提供了边沿触发（Edge
Triggered），这就使得用户空间程序有可能缓存IO状态，减少epoll_wait/epoll_pwait的调用，提高应用程序效率，完整代码[戳这里](https://github.com/zhangn1989/MyRPC)​​​​​​​

epoll API

1.创建一个epoll句柄，参数size用来告诉内核监听的文件描述符个数，跟内存大小有关

    
    
    int epoll_create(int size)
    size：告诉内核监听的数目（该参数已经废弃，随便给个参数就行）

2.控制某个epoll监控的文件描述符上的事件：注册、修改、删除。

    
    
    #include <sys/epoll.h>
    int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event)
    epfd：为epoll_creat的句柄
    op：表示动作，用3个宏来表示：
    EPOLL_CTL_ADD(注册新的fd到epfd)，
    EPOLL_CTL_MOD(修改已经注册的fd的监听事件)，
    EPOLL_CTL_DEL(从epfd删除一个fd)；
    event：告诉内核需要监听的事件
    struct epoll_event {
    __uint32_t events; /* Epoll events */
    epoll_data_t data; /* User data variable */
    };
    EPOLLIN ：表示对应的文件描述符可以读（包括对端SOCKET正常关闭）
    EPOLLOUT：表示对应的文件描述符可以写
    EPOLLPRI：表示对应的文件描述符有紧急的数据可读（这里应该表示有带外数据到来）
    EPOLLERR：表示对应的文件描述符发生错误
    EPOLLHUP：表示对应的文件描述符被挂断；
    EPOLLET： 将EPOLL设为边缘触发(Edge Triggered)模式，这是相对于水平触发(Level Triggered)来说的
    EPOLLONESHOT：只监听一次事件，当监听完这次事件之后，如果还需要继续监听这个socket的话，需要再次把这个socket加入到EPOLL队列里

3.等待所监控文件描述符上有事件的产生，类似于select()调用。

    
    
    #include <sys/epoll.h>
    int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout)
    events：用来从内核得到事件的集合，
    maxevents：告之内核这个events有多大，这个maxevents的值不能大于创建epoll_create()时的size，
    timeout：是超时时间
    -1：阻塞
    0：立即返回，非阻塞
    >0：指定微秒
    返回值：成功返回有多少文件描述符就绪，时间到时返回0，出错返回-1

下面的epoll模型的服务端代码，代码中实际使用的是int epoll_create1(int
flags)，flags只有一个参数EPOLL_CLOEXEC

epoll_create1(0)等价于epoll_create(0)

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    #include <unistd.h>
    #include <sys/time.h>
    #include <sys/types.h>  
    #include <sys/epoll.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h> /* superset of previous */
    #include <arpa/inet.h>
    
    #include "public_head.h"
    #include "fileio.h"
    
    #define LISTEN_BACKLOG 50
    #define MAX_EVENTS	5
    
    static ssize_t handle_request(int acceptfd)
    {
    	ssize_t readret = 0;
    	char read_buff[256] = { 0 };
    	char write_buff[256] = { 0 };
    
    
    	memset(read_buff, 0, sizeof(read_buff));
    	readret = read(acceptfd, read_buff, sizeof(read_buff));
    	if (readret == 0)
    		return readret;
    
    	printf("acceptfd:%d, recv message:%s\n", acceptfd, read_buff);
    
    	memset(write_buff, 0, sizeof(write_buff));
    	sprintf(write_buff, "This is server send message");
    	write(acceptfd, write_buff, sizeof(write_buff));
    
    	printf("\n");
    	return readret;
    }
    
    int main(int argc, char ** argv)
    {
    	int i = 0;
        int sockfd = 0;
        int acceptfd = 0;
        socklen_t client_addr_len = 0;
        struct sockaddr_in server_addr, client_addr;
    
        char client_ip[16] = { 0 };
    
    	int epfd = -1, ready = -1;
    	struct epoll_event ev;
    	struct epoll_event evlist[MAX_EVENTS];
    
        memset(&server_addr, 0, sizeof(server_addr));
        memset(&client_addr, 0, sizeof(client_addr));
    
        if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
            handle_error("socket");
    
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(9527);
        server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
        if(bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
        {
            close(sockfd);
            handle_error("bind");
        }
    
        if(listen(sockfd, LISTEN_BACKLOG) < 0)
        {
            close(sockfd);
            handle_error("listen");
        }
    	
    	epfd = epoll_create1(0);
    	if (epfd < 0)
    	{
    		close(sockfd);
    		handle_error("epoll_create1");
    	}
    
    	ev.data.fd = sockfd;
    	ev.events = EPOLLIN;
    	if (epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev) < 0)
    	{
    		close(sockfd);
    		close(epfd);
    		handle_error("epoll_ctl");
    	}
    
        while(1)
        {
    		ready = epoll_wait(epfd, evlist, MAX_EVENTS, -1);
    		if (ready < 0)
    		{
    			if (errno == EINTR)
    				continue;
    
    			close(sockfd);
    			close(epfd);
    			handle_error("epoll_wait");
    		}
    		else if (ready == 0)
    		{
    			continue;
    		}
    
    		for (i = 0; i < ready; ++i)
    		{
    			if (evlist[i].events != EPOLLIN)
    				continue;
    
    			if (evlist[i].data.fd == sockfd)
    			{
    				client_addr_len = sizeof(client_addr);
    				if ((acceptfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_addr_len)) < 0)
    				{
    					handle_warning("accept");
    					continue;
    				}
    
    				memset(client_ip, 0, sizeof(client_ip));
    				inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
    				printf("client:%s:%d\n", client_ip, ntohs(client_addr.sin_port));
    
    				ev.data.fd = acceptfd;
    				ev.events = EPOLLIN;
    				if (epoll_ctl(epfd, EPOLL_CTL_ADD, acceptfd, &ev) < 0)
    				{
    					close(acceptfd);
    					handle_warning("epoll_ctl");
    					continue;
    				}
    			}
    			else
    			{
    				if (handle_request(evlist[i].data.fd) <= 0)
    				{
    					ev.data.fd = evlist[i].data.fd;
    					ev.events = EPOLLIN;
    					if (epoll_ctl(epfd, EPOLL_CTL_DEL, evlist[i].data.fd, &ev) < 0)
    						handle_warning("epoll_ctl");
    					close(evlist[i].data.fd);
    				}
    			}
    		}
        }
    
    	close(epfd);
        close(sockfd);
    
    	exit(EXIT_SUCCESS);
    }
    

