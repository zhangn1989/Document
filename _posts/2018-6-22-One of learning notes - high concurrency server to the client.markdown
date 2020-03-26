---
layout: post
title: 高并发服务器学习笔记之一：客户端
date: 发布于2018-06-22 11:50:19 +0800
categories: 一步步打造高并发服务器
tag: 4
---

* content
{:toc}

写在前面：学习本系列需要具备网络基础、socket编程、多进程、多线程等前置知识，如果您对以上前置知识不怎么了解，请先去学习以上前置知识后再来阅读本文，废话不多说我们开始，完整代码[戳这里](https://github.com/zhangn1989/MyRPC)​​​​​​​
<!-- more -->


我们做一个服务简单一点的服务器，客户端先向服务端发送一个字符串，然后等待服务端返回的消息，循环十次后客户端断开连接；服务端等待客户端发来的消息，每收到一条消息，就向该客户端返回一条消息。

首先，我们先准备两个后面会用到的头文件，它们是日志相关的log.h和定义一些服务端和客户端都要用到的公共头文件public_head.h，代码如下

    
    
    //log.h
    #ifndef __LOG_H
    #define __LOG_H
    
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #include <stdarg.h>
    
    typedef enum {
    	SC_LOG_NONE = 0,
    	SC_LOG_EMERGENCY,
    	SC_LOG_ALERT,
    	SC_LOG_CRITICAL,
    	SC_LOG_ERROR,
    	SC_LOG_WARNING,
    	SC_LOG_NOTICE,
    	SC_LOG_INFO,
    	SC_LOG_DEBUG,
    
    	SC_LOG_LEVEL_MAX,
    } log_level;
    
    inline FILE *open_logfile(const char *path)
    {
    	return fopen(path, "a+");
    }
    
    inline void write_logfile(log_level type, FILE *fp, const char *format, ...)
    {
    	char log[128];
    	va_list arg_list;
    
    	memset(log, 0, sizeof(log));
    
    	switch (type)
    	{
    	case SC_LOG_EMERGENCY:
    		sprintf(log, "[log type:%s] ", "emergency");
    		break;
    	case SC_LOG_ALERT:
    		sprintf(log, "[log type:%s] ", "alert");
    		break;
    	case SC_LOG_CRITICAL:
    		sprintf(log, "[log type:%s] ", "critical");
    		break;
    	case SC_LOG_ERROR:
    		sprintf(log, "[log type:%s] ", "error");
    		break;
    	case SC_LOG_WARNING:
    		sprintf(log, "[log type:%s] ", "warning");
    		break;
    	case SC_LOG_NOTICE:
    		sprintf(log, "[log type:%s] ", "notice");
    		break;
    	case SC_LOG_INFO:
    		sprintf(log, "[log type:%s] ", "info");
    		break;
    	case SC_LOG_DEBUG:
    		sprintf(log, "[log type:%s] ", "debug");
    		break;
    	default:
    		sprintf(log, "[log type is error] ");
    		break;
    	}
    
    	fprintf(fp, log);
    
    	va_start(arg_list, format);
    	vfprintf(fp, format, arg_list);
    	va_end(arg_list);
    
    	fprintf(fp, "\n");
    }
    
    inline void close_logfile(FILE *fp)
    {
    	fclose(fp);
    }
    
    #define	writelog_emergency(fp, format, ...) \
    	do { write_logfile(SC_LOG_EMERGENCY, fp, format, __VA_ARGS__); } while (0)
    
    #define	writelog_alert(fp, format, ...) \
    	do { write_logfile(SC_LOG_ALERT, fp, format, __VA_ARGS__); } while (0)
    
    #define	writelog_critical(fp, format, ...) \
    	do { write_logfile(SC_LOG_CRITICAL, fp, format, __VA_ARGS__); } while (0)
    
    #define	writelog_error(fp, format, ...) \
    	do { write_logfile(SC_LOG_ERROR, fp, format, __VA_ARGS__); } while (0)
    
    #define	writelog_warning(fp, format, ...) \
    	do { write_logfile(SC_LOG_WARNING, fp, format, __VA_ARGS__); } while (0)
    
    #define	writelog_notice(fp, format, ...) \
    	do { write_logfile(SC_LOG_NOTICE, fp, format, __VA_ARGS__); } while (0)
    
    #define	writelog_info(fp, format, ...) \
    	do { write_logfile(SC_LOG_INFO, fp, format, __VA_ARGS__); } while (0)
    
    #define	writelog_debug(fp, format, ...) \
    	do { write_logfile(SC_LOG_DEBUG, fp, format, __VA_ARGS__); } while (0)
    
    #endif // !__LOG_H
    
    
    //public_head.h
    #ifndef __PUBLIC_HEAD_H
    #define __PUBLIC_HEAD_H
    
    #include "log.h"
    
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
    
    #endif  //__PUBLIC_HEAD_H
    

客户端实现比较简单，不用多说，直接上代码，以后所有的服务器模型都用这个客户端进行演示

    
    
    //client.c
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
    
    #define LISTEN_BACKLOG 50
    #define handle_error(msg) \
        do { perror(msg); exit(EXIT_FAILURE); } while (0)
    
    int main(int argc, char ** argv)
    {
        int i = 0;
        int sockfd = 0;
        ssize_t readret = 0;
        char read_buff[256] = { 0 };
        char write_buff[256] = { 0 };
        struct sockaddr_in server_addr;
    
        memset(&server_addr, 0, sizeof(server_addr));
    
        if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
            handle_error("socket");
    
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(9527);
        inet_pton(sockfd, "127.0.0.1", &server_addr.sin_addr.s_addr);
    
        if(connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
        {
            close(sockfd);
            handle_error("connect");
        }
    
        for(i = 0; i < 10; ++i)
        {
            memset(write_buff, 0, sizeof(write_buff));
            sprintf(write_buff, "This is client send message:%d", i);
            write(sockfd, write_buff, strlen(write_buff) + 1);
    
            memset(read_buff, 0, sizeof(read_buff));
            readret = read(sockfd, read_buff, sizeof(read_buff));
            if(readret == 0)
                break;
            printf("%s\n", read_buff);   
    		sleep(1);
        }
    
        close(sockfd);
    
        return 0;
    }
    

