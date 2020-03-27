---
layout: post
title: C++从零开始区块链：P2P模块之节点注册和监听
date: 发布于2018-09-05 15:29:46 +0800
categories: C++从零开始区块链
tag: 4
---

ThreadPool是一个线程池，具体实现就不贴了，随便找个线程池实现就行，也可以[戳这里](https://github.com/zhangn1989/shacoin)查看程序完整代码。

<!-- more -->

    
    
    P2PNode::P2PNode(const char *if_name)
    {
        m_sock = socket(AF_INET, SOCK_DGRAM, 0);//IPV4  SOCK_DGRAM 数据报套接字（UDP协议）  
        if (m_sock < 0)
        {
            perror("socket\n");
            return ;
        }
    
        int val = 1;
        if (setsockopt(m_sock, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val)) < 0)
        {
            perror("setsockopt");
        }
    
        struct timeval tv_out;
        tv_out.tv_sec = 10;//等待10秒
        tv_out.tv_usec = 0;
        if (setsockopt(m_sock, SOL_SOCKET, SO_RCVTIMEO, &tv_out, sizeof(tv_out)) < 0)
        {
            perror("setsockopt");
        }
    
        memset(&m_serverAddr, 0, sizeof(m_serverAddr));
        m_serverAddr.sin_family = AF_INET;
        m_serverAddr.sin_port = htons(SERVERPORT);
        m_serverAddr.sin_addr.s_addr = inet_addr(SERVERIP);
        socklen_t serverLen = sizeof(m_serverAddr);
    
        memset(&m_localAddr, 0, sizeof(m_localAddr));
        m_localAddr.sin_family = AF_INET;
        m_localAddr.sin_port = htons(LOCALPORT);
        m_localAddr.sin_addr.s_addr = htonl(INADDR_ANY);
        if (bind(m_sock, (struct sockaddr*)&m_localAddr, sizeof(m_localAddr)) < 0)
        {
            perror("bind");
            close(m_sock);
            exit(2);
        }
    
    
        memset(&m_recvAddr, 0, sizeof(m_recvAddr));
        socklen_t recvLen = sizeof(m_recvAddr);
    
        NodeInfo sendNode, recvNode;
        memset(&sendNode, 0, sizeof(NodeInfo));
        memset(&recvNode, 0, sizeof(NodeInfo));
        sendNode.cmd = cmd_register;
        sendNode.node.recvPort = LOCALPORT;
        get_local_ip(if_name, sendNode.node.recvIp);
    
        while (1)
        {
            if (sendto(m_sock, &sendNode, sizeof(NodeInfo), 0, (struct sockaddr*)&m_serverAddr, serverLen) < 0)
            {
                perror("sendto");
                close(m_sock);
                exit(4);
            }
    
            memset(&m_recvAddr, 0, sizeof(m_recvAddr));
            memset(&recvNode, 0, sizeof(NodeInfo));
            if (recvfrom(m_sock, &recvNode, sizeof(NodeInfo), 0, (struct sockaddr*)&m_recvAddr, &recvLen) < 0)
            {
                if (errno == EINTR || errno == EAGAIN)
                    continue;
    
                perror("recvfrom");
                close(m_sock);
                exit(2);
            }
    
            if (recvNode.cmd != cmd_register)
                continue;
    
            m_selfNode = recvNode.node;
            break;
        }
    
        while (1)
        {
            memset(&sendNode, 0, sizeof(NodeInfo));
            memset(&recvNode, 0, sizeof(NodeInfo));
            memset(&m_recvAddr, 0, sizeof(m_recvAddr));
    
            sendNode.cmd = cmd_getnode;
            sendNode.node = m_selfNode;
            if (sendto(m_sock, &sendNode, sizeof(NodeInfo), 0, (struct sockaddr*)&m_serverAddr, serverLen) < 0)
            {
                perror("sendto");
                close(m_sock);
                exit(4);
            }
    
            if (recvfrom(m_sock, &recvNode, sizeof(NodeInfo), 0, (struct sockaddr*)&m_recvAddr, &recvLen) < 0)
            {
                if (errno == EINTR || errno == EAGAIN)
                    continue;
    
                perror("recvfrom");
                close(m_sock);
                exit(2);
            }
    
            if (recvNode.cmd != cmd_getnode)
                continue;
    
            m_otherNode = recvNode.node;
            break;
        }
    
        //查询到的IP和接收到的IP如果不相同，则是内网环境
        //自己查询到的IP和另一个节点查询到的IP如果相同，则处于同一内网
        //同一内网的节点用内网传输数据，不在同一内网的节点只能用公网传输数据
        if (strcmp(m_selfNode.queryIp, m_selfNode.recvIp) &&
            !strcmp(m_selfNode.queryIp, m_otherNode.queryIp))
        {
            m_otherIP = m_otherNode.recvIp;
            m_otherPort = m_otherNode.recvPort;
        }
        else
        {
            m_otherIP = m_otherNode.queryIp;
            m_otherPort = m_otherNode.queryPort;
        }
    
        pthread_mutex_init(&m_mutexPack, NULL);
        pthread_mutex_init(&m_mutexResult, NULL);
    }
    
    P2PNode::~P2PNode()
    {
        NodeInfo sendNode;
        memset(&sendNode, 0, sizeof(NodeInfo));
    
        socklen_t serverLen = sizeof(m_serverAddr);
    
        sendNode.cmd = cmd_unregister;
        sendNode.node = m_selfNode;
        if (sendto(m_sock, &sendNode, sizeof(NodeInfo), 0, (struct sockaddr*)&m_serverAddr, serverLen) < 0)
        {
            perror("sendto");
            close(m_sock);
            exit(4);
        }
    
        close(m_sock);
    
        pthread_mutex_destroy(&m_mutexPack);
        pthread_mutex_destroy(&m_mutexResult);
    }
    
    P2PNode* P2PNode::Instance(const char *if_name)
    {
        static P2PNode node(if_name);
        return &node;
    }
    
    void P2PNode::Listen()
    {
        if (pthread_create(&m_tid, NULL, threadFunc, this) != 0)
        {
            close(m_sock);
            exit(2);
        }
    }
    void *P2PNode::threadFunc(void *arg)
    {
        P2PNode *p = (P2PNode*)arg;
        p->threadHandler();
        return NULL;
    }
    
    void P2PNode::threadHandler()
    {
        sockaddr_in otherAddr;
        memset(&otherAddr, 0, sizeof(otherAddr));
        otherAddr.sin_family = AF_INET;
        otherAddr.sin_port = htons(m_otherPort);
        otherAddr.sin_addr.s_addr = inet_addr(m_otherIP);
    
        P2PMessage recvMess;
        P2PMessage sendMess;
        P2PResult result;
    
        socklen_t recvLen = sizeof(m_recvAddr);
    
        ThreadPool<P2PMessage, P2PNode> tp(1);
        tp.setTaskFunc(this, &P2PNode::combinationPackage);
        tp.start();
    
        while (1)
        {
            memset(&recvMess, 0, sizeof(P2PMessage));
            memset(&sendMess, 0, sizeof(P2PMessage));
            memset(&result, 0, sizeof(P2PResult));
            memset(&m_recvAddr, 0, sizeof(m_recvAddr));
    
            if (recvfrom(m_sock, &recvMess, sizeof(P2PMessage), 0, (struct sockaddr*)&m_recvAddr, &recvLen) < 0)
            {
                if (errno == EINTR || errno == EAGAIN)
                    continue;
    
                perror("recvfrom");
                tp.stop();
                close(m_sock);
                exit(2);
            }
    
            if (recvMess.cmd == p2p_result)
            {
                memcpy(&result, recvMess.mess, recvMess.length);
                pthread_mutex_lock(&m_mutexResult);
                m_lstResult.push_back(result);
                pthread_mutex_unlock(&m_mutexResult);
                continue;
            }
    
            tp.addTask(recvMess);
    
            result.index = recvMess.index;
            memcpy(result.messHash, recvMess.messHash, sizeof(recvMess.messHash));
            sendMess.cmd = p2p_result;
            sendMess.length = sizeof(result);
            memcpy(sendMess.mess, &result, sendMess.length);
            if (sendto(m_sock, &sendMess, sizeof(sendMess), 0, (struct sockaddr*)&m_recvAddr, sizeof(m_recvAddr)) < 0)
            {
                perror("sendto");
                tp.stop();
                close(m_sock);
                exit(4);
            }
        }
        tp.stop();
    }

* content
{:toc}


