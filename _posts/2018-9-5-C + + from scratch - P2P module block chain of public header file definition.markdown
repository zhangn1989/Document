---
layout: post
title: C++从零开始区块链：P2P模块之公共头文件定义
date: 发布于2018-09-05 15:20:02 +0800
categories: C++从零开始区块链
tag: 4
---

搞了台阿里云做内网打洞测试，宏开关ALITEST用来内外网测试转换  

<!-- more -->
#define SERVERIP “xx.xx.xx.xx” 是外网测试机的外网IP

    
    
    #include <cstdio>
    #include <cstdlib>
    #include <cstring>
    
    #include <sys/ioctl.h>
    #include <net/if.h>
    
    namespace ShaCoin
    {
    #define ALITEST 0
    
    #if ALITEST
    #define SERVERIP    "xxx.xxx.xxx.xxx"
    #define LOCALPORT   10000
    
    #else //1
    #define SERVERIP    "192.168.180.133"
    #define LOCALPORT   20000
    
    #endif //1
    
    #define SERVERPORT  9527
    
        typedef enum
        {
            cmd_register = 0x1000,
            cmd_unregister,
            cmd_getnode,
            cmd_max
        } Command;
    
        typedef struct st_node
        {
            int count;
            char queryIp[16];
            int queryPort;
            char recvIp[16];
            int recvPort;
    
            bool operator == (const struct st_node & value) const
            {
                return
                    this->count == value.count &&
                    this->queryPort == value.queryPort &&
                    this->recvPort == value.recvPort &&
                    !strcmp(this->queryIp, value.queryIp) &&
                    !strcmp(this->recvIp, value.recvIp);
            }
        } __attribute__((packed))
            Node;
    
        typedef struct st_nodeinfo
        {
            Command cmd;
            Node node;
        } __attribute__((packed))
            NodeInfo;
    }

* content
{:toc}


