---
layout: post
title: 高并发服务器学习笔记之十一：集群架构
date: 发布于2018-06-26 17:06:38 +0800
categories: 一步步打造高并发服务器
tag: 4
---

* content
{:toc}

集群架构是用一台发现服务器加多台业务服务器的模式。业务服务器首先向发现服务器注册自己，将自己的IP和端口号告诉发现服务器。客户端连接的时候，不是直接连接业务服务器，而是先向发现服务器请求一个业务服务器，发现服务器接收到客户端的请求后会在已注册的业务服务器中选择一台最优质的发送给客户端，客户端拿到后再去连接相应的业务服务器处理业务。
<!-- more -->


本例和之前简单发送几个字符串相比，通信格式稍微复杂一些。首先是公共头文件public_head.h，重新定义了一些数据结构和通信协议。其次是增加了两个函数，readn和writen，这两个函数保证每次都能读写指定的数据大小，代码放在了fileio.c和fileio.h中。然后增加了一个发现服务器，用来管理其身后的业务服务器，并屏蔽掉服务器优选的动作，客户端无需知道究竟有多少业务服务器，只知道发现服务器给的一台业务服务器。客户端和服务端也做了相应的调整，服务端主要多了注册自己的过程，客户端主要多了向发现服务器索要业务服务器的过程。发现服务器和业务服务器可以用之前介绍的任意一种服务器模型，本例中使用的是线程池模型。

还没有来得及研究负载均衡算法，本例中只是简单的用权减去连接数，差值最大的视为最优服务器，等以后有时间搞懂负载均衡算法再来改进，完整代码[戳这里](https://github.com/zhangn1989/MyRPC)

首先是public_head.h

    
    
    #ifndef __PUBLIC_HEAD_H
    #define __PUBLIC_HEAD_H
    
    #include <sys/ioctl.h>
    #include <net/if.h>
    
    #include "log.h"
    #include "fileio.h"
    
    #define DIS_PORT	9527
    #define DIS_IP	"127.0.0.1"
    #define QUEUE_MAX	100
    
    #define IF_NAME	"eth0"
    
    typedef enum
    {
    	cmd_connect = 0,
    	cmd_backconnect,
    	cmd_unconnect,
    	cmd_register,
    	cmd_unregister,
    	cmd_heart,
    	cmd_max
    } command;
    
    typedef struct __serverinfo
    {
    	int id;
    	char ip[16];
    	in_port_t port;
    }serverinfo;
    
    typedef struct __messages
    {
    	command cmd;
    	int arglen;
    	unsigned char argv[0];
    }message;
    
    typedef struct __connectback
    {
    	int back;
    	int id;
    }connectback;
    
    #define handle_info(msg) \
            do { write_logfile(SC_LOG_INFO, stderr, \
                "file:%s line:%d errorno:%d message:%s", \
                __FILE__, __LINE__, errno, msg); \
                } while (0)
    
    #define handle_info(msg) \
            do { write_logfile(SC_LOG_INFO, stderr, \
                "file:%s line:%d errorno:%d message:%s", \
                __FILE__, __LINE__, errno, msg); \
                } while (0)
    
    #define handle_warning(msg) \
            do { write_logfile(SC_LOG_WARNING, stderr, \
                "file:%s line:%d errorno:%d message:%s", \
                __FILE__, __LINE__, errno, msg); \
                } while (0)
    
    #define handle_error(msg) \
            do { write_logfile(SC_LOG_ERROR, stderr, \
                "file:%s line:%d errorno:%d message:%s", \
                __FILE__, __LINE__, errno, msg); \
                exit(errno); } while (0)
    
    static inline int get_local_ip(char * ifname, char * ip)
    {
    	char *temp = NULL;
    	int inet_sock;
    	struct ifreq ifr;
    
    	inet_sock = socket(AF_INET, SOCK_DGRAM, 0);
    
    	memset(ifr.ifr_name, 0, sizeof(ifr.ifr_name));
    	memcpy(ifr.ifr_name, ifname, strlen(ifname));
    
    	if (0 != ioctl(inet_sock, SIOCGIFADDR, &ifr))
    	{
    		perror("ioctl error");
    		return -1;
    	}
    
    	temp = inet_ntoa(((struct sockaddr_in*)&(ifr.ifr_addr))->sin_addr);
    	memcpy(ip, temp, strlen(temp));
    
    	close(inet_sock);
    
    	return 0;
    }
    
    #endif  //__PUBLIC_HEAD_H
    

fileio.h中只有两个函数的声明，就不贴了，直接贴fileio.c

    
    
    //fileio.c
    #include <errno.h>
    
    #include "fileio.h"
    
    ssize_t readn(int fd, void *buffer, size_t n)
    {
    	ssize_t num_read;
    	size_t tot_read;
    	char *buf;
    
    	buf = buffer;
    	for (tot_read = 0; tot_read < n; )
    	{
    		num_read = read(fd, buf, n - tot_read);
    
    		if (num_read == 0)
    			return tot_read;
    
    		if (num_read < 0)
    		{
    			if (errno == EINTR)
    				continue;
    			else
    				return -1;
    		}
    
    		tot_read += num_read;
    		buf += num_read;
    	}
    
    	return tot_read;
    }
    
    ssize_t writen(int fd, const void *buffer, size_t n)
    {
    	ssize_t num_written;
    	size_t tot_written;
    	const char *buf;
    
    	buf = buffer;
    	for (tot_written = 0; tot_written < n; )
    	{
    		num_written = write(fd, buf, n - tot_written);
    
    		if (num_written <= 0)
    		{
    			if (num_written < 0 && errno == EINTR)
    				continue;
    			else
    				return -1;
    		}
    
    		tot_written += num_written;
    		buf += num_written;
    	}
    
    	return tot_written;
    }

发现服务器代码在discovery.c中

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    #include <pthread.h>
    #include <unistd.h>
    #include <sys/types.h>
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h> /* superset of previous */
    #include <arpa/inet.h>
    
    #include "public_head.h"
    
    #define LISTEN_BACKLOG	50
    #define THREAD_COUNT	3
    #define WEIGHT_BOTTOM	1
    #define WEIGHT_TOP		1024
    #define WEIGHT_ADD(w)	{if((w) <= (WEIGHT_TOP / 2)) (w) *= 2;}
    #define WEIGHT_SUB(w)	{if((w) > WEIGHT_BOTTOM) (w) /= 2;}
    
    typedef struct __register_server
    {
    	int weight;
    	int client_count;
    	serverinfo info;
    }register_server;
    
    static int clientfd[QUEUE_MAX];
    static int *client_start;
    static int *client_end;
    
    static register_server serverlist[QUEUE_MAX];
    
    static pthread_mutex_t servermutex = PTHREAD_MUTEX_INITIALIZER;
    
    static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    static pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
    
    void cmd_connect_func(int acceptfd, unsigned char *argv, int arglen)
    {
    	int i = 0;
    	int id = 0;
    	int sub = 0;
    	int maxsub = 0;
    	message *sendmsg = NULL;
    
    	sendmsg = malloc(sizeof(message) + sizeof(serverinfo));
    	if (!sendmsg)
    	{
    		handle_warning("malloc");
    		return;
    	}
    
    	memset(sendmsg, 0, sizeof(message) + sizeof(serverinfo));
    
    	//用负载均衡算法找出最优服务器，并发送给请求客户端
    	for (i = 0; i < QUEUE_MAX; ++i)
    	{
    		if(serverlist[i].info.id < 0)
    			continue;
    
    		sub = serverlist[i].weight - serverlist[i].client_count;
    		if (sub > maxsub)
    		{
    			id = i;
    			maxsub = sub;
    		}
    	}
    
    	memcpy(sendmsg->argv, &serverlist[id].info, sizeof(serverinfo));
    	writen(acceptfd, sendmsg, sizeof(message) + sizeof(serverinfo));
    	if (sendmsg) free(sendmsg);
    }
    
    void cmd_backconnect_func(int acceptfd, unsigned char *argv, int arglen)
    {
    	connectback cb;
    
    	memcpy(&cb, argv, sizeof(connectback));
    	if (cb.back)
    	{
    		//给id服务器加权，增加连接数
    		pthread_mutex_lock(&servermutex);
    		WEIGHT_ADD(serverlist[cb.id].weight);
    		serverlist[cb.id].client_count++;
    		pthread_mutex_unlock(&servermutex);
    	}
    	else
    	{
    		//给id服务器减权，并重新发送新的服务器
    		pthread_mutex_lock(&servermutex);
    		WEIGHT_SUB(serverlist[cb.id].weight);
    		pthread_mutex_unlock(&servermutex);
    		cmd_connect_func(acceptfd, argv, arglen);
    	}
    }
    
    void cmd_unconnect_func(int acceptfd, unsigned char *argv, int arglen)
    {
    	int id = 0;
    	memcpy(&id, argv, sizeof(int));
    
    	//找到对应id的服务器，对其进行减连接数操作
    	pthread_mutex_lock(&servermutex);
    	serverlist[id].client_count--;
    	pthread_mutex_unlock(&servermutex);
    }
    
    void cmd_register_func(int acceptfd, unsigned char *argv, int arglen)
    {
    	
    	int i;
    	int id = 0;
    	message *msg = NULL;
    
    	pthread_mutex_lock(&servermutex);
    	for (i = 0; i < QUEUE_MAX; ++i)
    	{
    		if (serverlist[i].info.id == -1)
    		{
    			memcpy(&serverlist[i].info, argv, sizeof(serverinfo));
    			serverlist[i].info.id = i;
    			break;
    		}
    	}
    	pthread_mutex_unlock(&servermutex);
    
    	if (i == QUEUE_MAX)
    		id = -1;
    	else
    		id = i;
    
    	msg = malloc(sizeof(message) + sizeof(int));
    	if (msg)
    	{
    		msg->cmd = cmd_register;
    		msg->arglen = sizeof(int);
    		memcpy(msg->argv, &id, msg->arglen);
    		writen(acceptfd, msg, sizeof(message) + sizeof(int));
    		free(msg);
    	}
    	else
    	{
    		handle_warning("malloc");
    	}
    
    	return;
    }
    
    void cmd_unregister_func(int acceptfd, unsigned char *argv, int arglen)
    {
    	int id = 0;
    	memcpy(&id, argv, arglen);
    
    	//删除该服务器
    	serverlist[id].client_count = 0;
    	serverlist[id].weight = WEIGHT_TOP;
    	memset(&serverlist[id].info, 0, sizeof(serverinfo));
    	serverlist[id].info.id = -1;
    }
    
    void cmd_heart_func(int acceptfd, unsigned char *argv, int arglen)
    {
    
    }
    
    static void handle_request(int acceptfd)
    {
    	message msg;
    	ssize_t readret = 0;
    	unsigned char *argv = NULL;
    	while (1)
    	{
    		memset(&msg, 0, sizeof(message));
    		readret = readn(acceptfd, &msg, sizeof(message));
    		if (readret == 0)
    		{
    			close(acceptfd);
    			return;
    		}
    
    		if (msg.arglen > 0)
    		{
    			argv = malloc(msg.arglen);
    			if (!argv)
    			{
    				handle_warning("malloc");
    				close(acceptfd);
    				return;
    			}
    
    			readret = readn(acceptfd, argv, msg.arglen);
    			if (readret == 0)
    			{
    				handle_warning("readn argv");
    				free(argv);
    				argv = NULL;
    				close(acceptfd);
    				return;
    			}
    		}
    
    		switch (msg.cmd)
    		{
    		case cmd_connect:
    			cmd_connect_func(acceptfd, argv, msg.arglen);
    			break;
    		case cmd_backconnect:
    			cmd_backconnect_func(acceptfd, argv, msg.arglen);
    			break;
    		case cmd_unconnect:
    			cmd_unconnect_func(acceptfd, argv, msg.arglen);
    			break;
    		case cmd_register:
    			cmd_register_func(acceptfd, argv, msg.arglen);
    			break;
    		case cmd_unregister:
    			cmd_unregister_func(acceptfd, argv, msg.arglen);
    			break;
    		case cmd_heart:
    			cmd_heart_func(acceptfd, argv, msg.arglen);
    			break;
    		case cmd_max:
    		default:
    			break;
    		}
    
    		if (argv)
    		{
    			free(argv);
    			argv = NULL;
    		}
    	}
    	close(acceptfd);
    	return ;
    }
    
    void *thread_func(void *arg)
    {
    	int fd;
    	while (1)
    	{
    		pthread_mutex_lock(&mutex);
    		while (client_start >= client_end)
    		{
    			pthread_cond_wait(&cond, &mutex);
    			continue;
    		}
    
    		fd = *client_start;
    		*client_start = -1;
    		client_start++;
    		pthread_mutex_unlock(&mutex);
    		if (fd > 0)
    			handle_request(fd);
    	}
    }
    
    int main(int argc, char ** argv)
    {
    	int i = 0;
    	int sockfd = 0;
    	int acceptfd = 0;
    	socklen_t client_addr_len = 0;
    	struct sockaddr_in server_addr, client_addr;
    
    	char client_ip[16] = { 0 };
    
    	pthread_t tids[THREAD_COUNT];
    
    	client_start = client_end = clientfd;
    
    	memset(&server_addr, 0, sizeof(server_addr));
    	memset(&client_addr, 0, sizeof(client_addr));
    
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
    		handle_error("socket");
    	}
    
    	int val = 1;
    	if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val)) < 0)
    	{
    		handle_error("setsockopt()");
    	}
    
    	server_addr.sin_family = AF_INET;
    	server_addr.sin_port = htons(DIS_PORT);
    	server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    	if (bind(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    	{
    		close(sockfd);
    		handle_error("bind");
    	}
    
    	if (listen(sockfd, LISTEN_BACKLOG) < 0)
    	{
    		close(sockfd);
    		handle_error("listen");
    	}
    
    	for (i = 0; i < QUEUE_MAX; ++i)
    	{
    		clientfd[i] = -1;
    	}
    
    	for (i = 0; i < QUEUE_MAX; ++i)
    	{
    		serverlist[i].client_count = 0;
    		serverlist[i].weight = WEIGHT_TOP;
    		serverlist[i].info.id = -1;
    	}
    
    	for (i = 0; i < THREAD_COUNT; ++i)
    	{
    		if (pthread_create(tids + i, NULL, thread_func, NULL) != 0)
    		{
    			close(sockfd);
    			handle_error("pthread_create");
    		}
    	}
    
    	while (1)
    	{
    		client_addr_len = sizeof(client_addr);
    		if ((acceptfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_addr_len)) < 0)
    		{
    			perror("accept");
    			continue;
    		}
    
    		memset(client_ip, 0, sizeof(client_ip));
    		inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
    		printf("client:%s:%d\n", client_ip, ntohs(client_addr.sin_port));
    
    		//	pthread_mutex_lock(&mutex);
    		*client_end = acceptfd;
    		client_end++;
    		//	pthread_mutex_unlock(&mutex);
    		pthread_cond_signal(&cond);
    	}
    
    	close(sockfd);
    
    	return 0;
    }

服务端server.c

    
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <errno.h>
    
    #include <pthread.h>
    #include <unistd.h>
    #include <sys/types.h>          /* See NOTES */
    #include <sys/socket.h>
    #include <netinet/in.h>
    #include <netinet/ip.h> /* superset of previous */
    #include <arpa/inet.h>
    
    #include "public_head.h"
    
    #define LISTEN_BACKLOG 50
    #define THREAD_COUNT	3
    
    static int clientfd[QUEUE_MAX];
    static int *client_start;
    static int *client_end;
    
    static serverinfo selfinfo;
    
    static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    static pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
    
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
    
    		printf("thread id:%lu, recv message:%s\n", pthread_self(), read_buff);
    
    		memset(write_buff, 0, sizeof(write_buff));
    		sprintf(write_buff, "This is server send message:%d", i++);
    		write(acceptfd, write_buff, sizeof(write_buff));
    	}
    
        printf("\n");
        close(acceptfd);
        return;
    }
    
    static void *thread_func(void *arg)
    {
    	int fd;
    	while (1)
    	{
    		pthread_mutex_lock(&mutex);
    		while (client_start >= client_end)
    		{
    			pthread_cond_wait(&cond, &mutex);
    			continue;
    		}
    
    		fd = *client_start;
    		*client_start = -1;
    		client_start++;
    		pthread_mutex_unlock(&mutex);
    		if(fd > 0)
    			handle_request(fd);
    	}
    	return NULL;
    }
    
    static void register_service(in_port_t port)
    {
    	int sockfd = 0;
    	struct sockaddr_in server_addr;
    
    	message *sendmsg, *recvmsg;
    
    	sendmsg = malloc(sizeof(message) + sizeof(serverinfo));
    	if(!sendmsg)
    		handle_error("register_service");
    
    	recvmsg = malloc(sizeof(message) + sizeof(int));
    	if (!recvmsg)
    	{
    		free(sendmsg);
    		handle_error("register_service");
    	}
    
    	sendmsg->cmd = cmd_register;
    	sendmsg->arglen = sizeof(serverinfo);
    	selfinfo.port = port;
    	get_local_ip(IF_NAME, selfinfo.ip);
    	memcpy(sendmsg->argv, &selfinfo, sizeof(serverinfo));
    
    	memset(&server_addr, 0, sizeof(server_addr));
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
    		free(sendmsg);
    		free(recvmsg);
    		handle_error("socket");
    	}
    
    	server_addr.sin_family = AF_INET;
    	server_addr.sin_port = htons(DIS_PORT);
    	inet_pton(sockfd, DIS_IP, &server_addr.sin_addr.s_addr);
    
    	if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    	{
    		free(sendmsg);
    		free(recvmsg);
    		close(sockfd);
    		handle_error("connect");
    	}
    
    	writen(sockfd, sendmsg, sizeof(message) + sizeof(serverinfo));
    	if(readn(sockfd, recvmsg, sizeof(message) + sizeof(int)) != 0)
    		memcpy(&selfinfo.id, recvmsg->argv, sizeof(int));
    	close(sockfd);
    
    	free(sendmsg);
    	free(recvmsg);
    }
    
    static void unregister_service()
    {
    	int sockfd = 0;
    	struct sockaddr_in server_addr;
    
    	message *sendmsg;
    
    	sendmsg = malloc(sizeof(message) + sizeof(int));
    	if (!sendmsg)
    		handle_error("register_service");
    
    	sendmsg->cmd = cmd_unregister;
    	sendmsg->arglen = sizeof(int);
    	memcpy(sendmsg->argv, &selfinfo.id, sendmsg->arglen);
    
    	memset(&server_addr, 0, sizeof(server_addr));
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
    		free(sendmsg);
    		handle_error("socket");
    	}
    
    	server_addr.sin_family = AF_INET;
    	server_addr.sin_port = htons(DIS_PORT);
    	inet_pton(sockfd, DIS_IP, &server_addr.sin_addr.s_addr);
    
    	if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    	{
    		free(sendmsg);
    		close(sockfd);
    		handle_error("connect");
    	}
    
    	writen(sockfd, sendmsg, sizeof(message) + sizeof(int));
    	
    	close(sockfd);
    	free(sendmsg);
    }
    
    int main(int argc, char ** argv)
    {
    	int i = 0;
        int sockfd = 0;
        int acceptfd = 0;
    	in_port_t port = 0;
        socklen_t client_addr_len = 0;
        struct sockaddr_in server_addr, client_addr;
    
        char client_ip[16] = { 0 };
    
    	pthread_t tids[THREAD_COUNT];
    
    	client_start = client_end = clientfd;
    
    	if (argc < 2)
    		handle_error("argc");
    
    	port = atoi(argv[1]);
    
        memset(&server_addr, 0, sizeof(server_addr));
        memset(&client_addr, 0, sizeof(client_addr));
    
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
    		unregister_service();
    		handle_error("socket");
    	}
    
    	int val = 1;
    	if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val)) < 0)
    	{
    		handle_error("setsockopt()");
    	}
    
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);
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
    
    	for (i = 0; i < QUEUE_MAX; ++i)
    	{
    		clientfd[i] = -1;
    	}
    
    	for (i = 0; i < THREAD_COUNT; ++i)
    	{
    		if (pthread_create(tids + i, NULL, thread_func, NULL) != 0)
    		{
    			close(sockfd);
    			handle_error("pthread_create");
    		}
    	}
    
    	register_service(port);
    	if (selfinfo.id == -1)
    	{
    		close(sockfd);
    		handle_error("register_service");
    	}
    
        while(1)
        {
            client_addr_len = sizeof(client_addr);
            if((acceptfd = accept(sockfd, (struct sockaddr *)&client_addr, &client_addr_len)) < 0)
            {
                perror("accept");
                continue;
            }
           
            memset(client_ip, 0, sizeof(client_ip));
            inet_ntop(AF_INET,&client_addr.sin_addr,client_ip,sizeof(client_ip)); 
            printf("client:%s:%d\n",client_ip,ntohs(client_addr.sin_port));
    
    	//	pthread_mutex_lock(&mutex);
    		*client_end = acceptfd;
    		client_end++;
    	//	pthread_mutex_unlock(&mutex);
    		pthread_cond_signal(&cond);
        }
        
        close(sockfd);
    
    	unregister_service();
        return 0;
    }
    

客户端

    
    
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
    
    #define LISTEN_BACKLOG 50
    
    static int tryconnectserver(serverinfo *info)
    {
    	int sockfd = -1;
    	struct sockaddr_in server_addr;
    	memset(&server_addr, 0, sizeof(server_addr));
    
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
    		handle_warning("socket");
    		return -1;
    	}
    
    	server_addr.sin_family = AF_INET;
    	server_addr.sin_port = htons(info->port);
    	inet_pton(sockfd, info->ip, &server_addr.sin_addr.s_addr);
    
    	if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    	{
    		close(sockfd);
    		handle_warning("socket");
    		return -1;
    	}
    
    	return sockfd;
    }
    
    static void connectserver(int *confd, int *serverid)
    {
    	int sockfd = -1;
    	message *sendmsg = NULL;
    	message *recvmsg = NULL;
    	message *backmsg = NULL;
    	serverinfo info;
    	connectback cb;
    	struct sockaddr_in server_addr;
    
    	if (!confd || !serverid)
    		return;
    
    	*confd = -1;
    	cb.id = -1;
    	cb.back = 0;
    
    	sendmsg = malloc(sizeof(message));
    	if (!sendmsg)
    	{
    		handle_warning("malloc");
    		return;
    	}
    
    	recvmsg = malloc(sizeof(message) + sizeof(serverinfo));
    	if (!recvmsg)
    	{
    		free(sendmsg);
    		handle_warning("malloc");
    		return;
    	}
    
    	backmsg = malloc(sizeof(message) + sizeof(connectback));
    	if (!backmsg)
    	{
    		free(recvmsg);
    		free(sendmsg);
    		handle_warning("malloc");
    		return;
    	}
    
    	memset(sendmsg, 0, sizeof(message));
    	memset(recvmsg, 0, sizeof(message) + sizeof(serverinfo));
    	memset(backmsg, 0, sizeof(message) + sizeof(connectback));
    	memset(&info, 0, sizeof(serverinfo));
    	memset(&server_addr, 0, sizeof(server_addr));
    
    	sendmsg->cmd = cmd_connect;
    	sendmsg->arglen = 0;
    
    	backmsg->cmd = cmd_backconnect;
    	backmsg->arglen = sizeof(connectback);
    
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
    		free(sendmsg);
    		free(recvmsg);
    		free(backmsg);
    		handle_warning("socket");
    		return;
    	}
    
    	server_addr.sin_family = AF_INET;
    	server_addr.sin_port = htons(DIS_PORT);
    	inet_pton(sockfd, DIS_IP, &server_addr.sin_addr.s_addr);
    
    	if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    	{
    		free(sendmsg);
    		free(recvmsg);
    		free(backmsg);
    		close(sockfd);
    		handle_warning("socket");
    		return;
    	}
    	while (1)
    	{
    		writen(sockfd, sendmsg, sizeof(message));
    		if (readn(sockfd, recvmsg, sizeof(message) + sizeof(serverinfo)) == 0)
    		{
    			free(sendmsg);
    			free(recvmsg);
    			free(backmsg);
    			close(sockfd);
    			handle_warning("readn");
    			return;
    		}
    
    		memcpy(&info, recvmsg->argv, sizeof(serverinfo));
    		*confd = tryconnectserver(&info);
    		if (*confd > 0)
    		{
    			*serverid = info.id;
    			//这个服务器可以了
    			cb.back = 1;
    			cb.id = info.id;
    			memcpy(backmsg->argv, &cb, sizeof(connectback));
    			writen(sockfd, backmsg, sizeof(message) + sizeof(connectback));
    			break;
    		}
    
    		//这个服务器不行，再给换一个
    		cb.back = 0;
    		cb.id = info.id;
    		memcpy(backmsg->argv, &cb, sizeof(connectback));
    		writen(sockfd, backmsg, sizeof(message) + sizeof(connectback));
    
    		sleep(30);
    	}
    
    	free(sendmsg);
    	free(recvmsg);
    	free(backmsg);
    	close(sockfd);
    	return;
    }
    
    static void unconnectserver(int confd, int serverid)
    {
    	close(confd);
    
    	int sockfd = -1;
    	message *sendmsg = NULL;
    	struct sockaddr_in server_addr;
    
    	memset(sendmsg, 0, sizeof(message));
    	memset(&server_addr, 0, sizeof(server_addr));
    
    	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    	{
    		handle_warning("socket");
    		return;
    	}
    
    	server_addr.sin_family = AF_INET;
    	server_addr.sin_port = htons(DIS_PORT);
    	inet_pton(sockfd, DIS_IP, &server_addr.sin_addr.s_addr);
    
    	if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
    	{
    		close(sockfd);
    		handle_warning("socket");
    		return;
    	}
    
    	sendmsg = malloc(sizeof(message) + sizeof(int));
    	if (!sendmsg)
    	{
    		handle_warning("malloc");
    		return;
    	}
    
    	sendmsg->cmd = cmd_unconnect;
    	sendmsg->arglen = sizeof(int);
    	memcpy(sendmsg->argv, &serverid, sendmsg->arglen);
    
    	writen(sockfd, sendmsg, sizeof(message) + sizeof(int));
    
    	free(sendmsg);
    }
    
    int main(int argc, char ** argv)
    {
        int i = 0;
    	int sockfd = -1;
    	int serverid = 0;
    	ssize_t readret = 0;
    
    	char read_buff[256] = { 0 };
    	char write_buff[256] = { 0 };
    
    	connectserver(&sockfd, &serverid);
    	if (sockfd < 0)
    		handle_error("connectserver");
    
    	for (i = 0; i < 10; ++i)
    	{
    		memset(write_buff, 0, sizeof(write_buff));
    		sprintf(write_buff, "This is client send message:%d", i);
    		write(sockfd, write_buff, strlen(write_buff) + 1);
    
    		memset(read_buff, 0, sizeof(read_buff));
    		readret = read(sockfd, read_buff, sizeof(read_buff));
    		if (readret == 0)
    			break;
    		printf("%s\n", read_buff);
    
    		sleep(1);
    	}
    
    	unconnectserver(sockfd, serverid);
    
        return 0;
    }
    

