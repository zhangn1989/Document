---
layout: post
title: 高并发服务器学习笔记之七：异步IO——poll模型
date: 发布于2018-06-22 16:10:28 +0800
categories: 一步步打造高并发服务器
tag: 4
---

* content
{:toc}

poll模型和select模型很相似。两者间的主要区别在于我们要如何指定待检查的文件描述符。在select中，我们提供三个集合，在每个集合中标明我们感兴趣的文件描述符。而在poll中我们提供一列文件描述符，并在每个文件描述符上标明我们感兴趣的事件，完整代码[戳这里](https://github.com/zhangn1989/MyRPC)​​​​​​​，用到的系统调用如下
<!-- more -->


    
    
    #include <poll.h>
    int poll(struct pollfd *fds, nfds_t nfds, int timeout);
    struct pollfd {
    int fd; /* 文件描述符 */
    short events; /* 监控的事件 */
    short revents; /* 监控事件中满足条件返回的事件 */
    };
    POLLIN普通或带外优先数据可读,即POLLRDNORM | POLLRDBAND
    POLLRDNORM-数据可读
    POLLRDBAND-优先级带数据可读
    POLLPRI 高优先级可读数据
    POLLOUT普通或带外数据可写
    POLLWRNORM-数据可写
    POLLWRBAND-优先级带数据可写
    POLLERR 发生错误
    POLLHUP 发生挂起
    POLLNVAL 描述字不是一个打开的文件
    nfds 监控数组中有多少文件描述符需要被监控
    timeout 毫秒级等待
    -1：阻塞等，#define INFTIM -1 Linux中没有定义此宏
    0：立即返回，不阻塞进程
    >0：等待指定毫秒数，如当前系统时间精度不够毫秒，向上取值

如果不再监控某个文件描述符时，可以把pollfd中，fd设置为-1，poll不再监控此

pollfd，下次返回时，把revents设置为0。

下面是poll模型的服务端代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    #include <unistd.h>
    #include <sys/time.h>
    #include <sys/types.h>          /* See NOTES */
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h> /* superset of previous */
    #include <arpa/inet.h>
    #include <poll.h>
    
    #include "public_head.h"
    #include "fileio.h"
    
    #define LISTEN_BACKLOG 50
    #define MAX_CLIENT	1024
    
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
    
    	int ready;
    	int clientlen = 0;
    	struct pollfd clientfd[MAX_CLIENT];
    
    	for (i = 0; i < MAX_CLIENT; ++i)
    		clientfd[i].fd = -1;
    
        memset(&server_addr, 0, sizeof(server_addr));
        memset(&client_addr, 0, sizeof(client_addr));
    
        if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
            handle_error("socket");
    
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(9527);
        server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
        if(bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
        {
    		char buff[256] = { 0 };
            close(sockfd);
    		strerror_r(errno, buff, sizeof(buff));
            handle_error("bind");
        }
    
        if(listen(sockfd, LISTEN_BACKLOG) < 0)
        {
            close(sockfd);
            handle_error("listen");
        }
    
    	clientfd[0].fd = sockfd;
    	clientfd[0].events = POLLRDNORM;
    	clientlen++;
    	
        while(1)
        {
    		ready = poll(clientfd, clientlen, -1);
    		if (ready < 0)
    		{
    			if(errno == EINTR)
    				continue;
    
    			close(sockfd);
    			handle_error("poll");
    		}
    		else if (ready == 0)
    		{
    			continue;
    		}
    
    		if (clientfd[0].revents & POLLRDNORM)
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
    
    			clientfd[clientlen].fd = acceptfd;
    			clientfd[clientlen].events = POLLRDNORM;
    			clientlen++;
    
    			if (ready == 1)
    				continue;
    		}
            
    		for (i = 1; i < clientlen; ++i)
    		{
    			if (clientfd[i].fd < 0)
    				continue;
    
    			if (clientfd[i].revents & POLLRDNORM)
    			{
    				if (handle_request(clientfd[i].fd) <= 0)
    				{
    					close(clientfd[i].fd);
    					clientfd[i].fd = -1;
    				}
    			}
    		}
        }
        
        close(sockfd);
    
    	exit(EXIT_SUCCESS);
    }
    

