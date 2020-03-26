---
layout: post
title: 高并发服务器学习笔记之六：异步IO——select模型
date: 发布于2018-06-22 15:50:37 +0800
categories: 一步步打造高并发服务器
tag: 4
---

* content
{:toc}

前面介绍的都是阻塞IO，又称同步IO，系统默认的IO操作都是同步的，即每次都阻塞在文件读写上，如果没有数据到来程序就阻塞在那，完全靠多线程和多进程实现并发。今天我们开学习非阻塞IO，又称异步IO，在单一线程中实现并发。
<!-- more -->


异步IO的大概的思想是，我们先准备一个文件监控集，将我们想要监控的文件描述符添加到监控集中，然后循环监控该监控集中的文件描述符，当某个或某几个文件有数据到来就结束循环去处理，处理完毕后继续循环监控。和同步IO相比，同步IO是阻塞在某一个文件上，即使其他文件有数据来了，但阻塞的文件上还是没有数据到来，那么程序会一直阻塞，直到该文件有数据到来，处理后再去处理另一个文件。而异步IO则是同时监控多个文件，哪个文件先有数据到来，就处理哪个文件，只有大家都没有数据到来时才会阻塞。

异步IO的并发效率要远高于用同步IO依靠多线程和多进程实现的并发，在Linux平台上，主要有select、poll、信号驱动IO和epoll四种模型。其中select和poll是两种非常古老的异步模型，古老就意味着支持的平台比较多，可移植性好，但其效率很低。而信号驱动IO和epoll模型效率要远高于select和poll，但其只在Linux平台上支持，移植性不好。在效率比较上，在数百数千级的并发量上，四种模型的效率基本上差不多，而在超过数百数千的并发量以后，select和poll的效率就远不如信号驱动和epoll了，epoll是目前主流的服务器设计模式，号称是可以支持百万级别并发量的。后面我们会依次学习到select、poll和epoll，信号驱动IO实现起来比较复杂，效率又与epoll差不多，同时epoll又具有信号驱动IO的几乎所有有点，因此信号驱动IO用到的不多，就不介绍了。

今天我们先来介绍以下select模型，完整代码[戳这里](https://github.com/zhangn1989/MyRPC)​​​​​​​

select的特点：

1.select能监听的文件描述符个数受限于FD_SETSIZE,一般为1024，单纯改变进程打开  
的文件描述符个数并不能改变select监听文件个数  
2.解决1024以下客户端时使用select是很合适的，但如果链接客户端过多，select采用  
的是轮询模型，会大大降低服务器响应效率，不应在select上投入更多精力

用到的相关函数如下

    
    
    #include <sys/select.h>
    /* According to earlier standards */
    #include <sys/time.h>
    #include <sys/types.h>
    #include <unistd.h>
    int select(int nfds, fd_set *readfds, fd_set *writefds,
    fd_set *exceptfds, struct timeval *timeout);
    nfds: 监控的文件描述符集里最大文件描述符加1，因为此参数会告诉内核检测前多少个文件描述符的状态
    readfds：监控有读数据到达文件描述符集合，传入传出参数
    writefds：监控写数据到达文件描述符集合，传入传出参数
    exceptfds：监控异常发生达文件描述符集合,如带外数据到达异常，传入传出参数
    timeout：定时阻塞监控时间，3种情况
    1.NULL，永远等下去
    2.设置timeval，等待固定时间
    3.设置timeval里时间均为0，检查描述字后立即返回，轮询
    struct timeval {
    long tv_sec; /* seconds */
    long tv_usec; /* microseconds */
    };
    void FD_CLR(int fd, fd_set *set); 把文件描述符集合里fd清0
    int FD_ISSET(int fd, fd_set *set); 测试文件描述符集合里fd是否置1
    void FD_SET(int fd, fd_set *set); 把文件描述符集合里fd位置1
    void FD_ZERO(fd_set *set); 把文件描述符集合里所有位清0

有些select的实现，在每次select返回后会清空原有的监控集，每次select调用前都要重新设置监控集，下面是服务端代码

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    #include <unistd.h>
    #include <sys/time.h>
    #include <sys/select.h>
    #include <sys/types.h>          /* See NOTES */
    #include <sys/wait.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h> /* superset of previous */
    #include <arpa/inet.h>
    
    #include "public_head.h"
    #include "fileio.h"
    
    #define LISTEN_BACKLOG 50
    
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
        int sockfd = -1;
        int acceptfd = -1;
        socklen_t client_addr_len = 0;
        struct sockaddr_in server_addr, client_addr;
    
        char client_ip[16] = { 0 };
    
    	int clientfd[FD_SETSIZE];
    	int i = 0, client_index = 0;
    	int ready = -1, nfds = -1;
    	fd_set rset;
    	FD_ZERO(&rset);
    
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
    
    	for (i = 0; i < FD_SETSIZE; ++i)
    		clientfd[i] = -1;
    
    	nfds = sockfd;
    	
        while(1)
        {
    		FD_SET(sockfd, &rset);
    		for (i = 0; i < client_index; ++i)
    		{
    			if( clientfd[i] < 0)
    				continue;
    
    			FD_SET(clientfd[i], &rset);
    		}
    
    		ready = select(nfds + 1, &rset, NULL, NULL, NULL);
    		if (ready < 0)
    		{
    			if (errno == EINTR)
    				continue;
    
    			close(sockfd);
    			handle_error("select");
    		}
    		else if (ready == 0)
    		{
    			continue;
    		}
    
    		if (FD_ISSET(sockfd, &rset))
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
    
    			clientfd[client_index++] = acceptfd;
    
    			FD_SET(acceptfd, &rset);
    			if (acceptfd > nfds)
    				nfds = acceptfd;
    			if (ready == 1)
    				continue;
    		}
    
    		for (i = 0; i < client_index; ++i)
    		{
    			if (clientfd[i] < 0)
    				continue;
    
    			if (FD_ISSET(clientfd[i], &rset))
    			{
    				if (handle_request(clientfd[i]) <= 0)
    				{
    					FD_CLR(clientfd[i], &rset);
    					close(clientfd[i]);
    					clientfd[i] = -1;
    				}
    			}
    		}
        }
        
        close(sockfd);
    
    	exit(EXIT_SUCCESS);
    }
    

