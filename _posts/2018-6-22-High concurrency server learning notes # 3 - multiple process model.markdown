---
layout: post
title: 高并发服务器学习笔记之三：多进程模型
date: 发布于2018-06-22 14:37:56 +0800
categories: 一步步打造高并发服务器
tag: 4
---

* content
{:toc}

该模型是在单一迭代模型的基础上的改进，父进程只在一个死循环里进行accept，当一个客户端接入时，父进程会fork一个子进程，然后父进程关闭该连接的socket，并继续accept，等待下一个客户端接入，子进程可以关闭监听socket，然后去处理客户端请求，处理结束后关闭连接socket，结束自身进程，完整代码[戳这里](https://github.com/zhangn1989/MyRPC)​​​​​​​
<!-- more -->


    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    #include <signal.h>
    #include <semaphore.h>
    #include <unistd.h>
    #include <sys/types.h>          /* See NOTES */
    #include <sys/wait.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h> /* superset of previous */
    #include <arpa/inet.h>
    
    #include "public_head.h"
    #include "fileio.h"
    
    #define LISTEN_BACKLOG 50
    
    static void grim_reaper(int sig)
    {
    	int saved_error = errno;
    	while (waitpid(-1, NULL, WNOHANG) >= 0)
    		continue;
    
    	errno = saved_error;
    }
    
    static void handle_request(int acceptfd)
    {
        int i = 0;
        ssize_t readret = 0;
        char read_buff[256] = { 0 };
        char write_buff[256] = { 0 };
       
    	while (1)
    	{
    		memset(read_buff, 0, sizeof(read_buff));
    		readret = read(acceptfd, read_buff, sizeof(read_buff));
    		if (readret == 0)
    			break;
    
    		printf("progress id:%d, recv message:%s\n", getpid(), read_buff);
    
    		memset(write_buff, 0, sizeof(write_buff));
    		sprintf(write_buff, "This is server send message:%d", i++);
    		write(acceptfd, write_buff, sizeof(write_buff));
    	}
        
        printf("\n");
        close(acceptfd);
        return;
    }
    
    int main(int argc, char ** argv)
    {
    	pid_t pid;
        int sockfd = 0;
        int acceptfd = 0;
        socklen_t client_addr_len = 0;
    	struct sigaction sa;
        struct sockaddr_in server_addr, client_addr;
    
        char client_ip[16] = { 0 };
    
        memset(&server_addr, 0, sizeof(server_addr));
        memset(&client_addr, 0, sizeof(client_addr));
    
    	sigemptyset(&sa.sa_mask); 
    	sa.sa_flags = SA_RESTART;
    	sa.sa_handler = grim_reaper;
    	if(sigaction(SIGCHLD, &sa, NULL) < 0)
    		handle_error("sigaction");
    
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
    	
        while(1)
        {
            client_addr_len = sizeof(client_addr);
            if((acceptfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_addr_len)) < 0)
            {
    			handle_warning("accept");
    			continue;
            }
           
            memset(client_ip, 0, sizeof(client_ip));
            inet_ntop(AF_INET,&client_addr.sin_addr,client_ip,sizeof(client_ip)); 
            printf("client:%s:%d\n",client_ip,ntohs(client_addr.sin_port));
    
    		pid = fork();
    		if (pid > 0)	//parent
    		{
    			close(acceptfd);
    			continue;
    		} 
    		else if (pid == 0)	//child
    		{
    			close(sockfd);
    			handle_request(acceptfd);
    			exit(EXIT_SUCCESS);
    		} 
    		else
    		{
    			handle_warning("fork");
    			continue;
    		}
        }
        
        close(sockfd);
    
    	exit(EXIT_SUCCESS);
    }
    

