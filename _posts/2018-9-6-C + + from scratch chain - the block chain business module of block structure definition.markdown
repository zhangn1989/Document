---
layout: post
title: C++从零开始区块链：区块链业务模块之区块结构定义
date: 发布于2018-09-06 10:38:51 +0800
categories: C++从零开始区块链
tag: 4
---

* content
{:toc}

区块链的对外展示主要是以json的形式，我们先来定义一下json，主要是说明格式，数据什么的我瞎写的。实际应用中应该加入一个随机值用作校验，这里就不加了
<!-- more -->


    
    
    block = {
    'index': 1,                                           //索引
    'timestamp': 1506057125,                              //时间戳
    'transactions': [                                     //交易列表，可以有多个交易
    { 
    'sender': "8527147fe1f5426f9dd545de4b27ee00",        //付款方
    'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",     //收款方
    'amount': 5,                                         //金额
    }
    ],
    'proof': 324984774000,                               //工作量证明
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b"       //前一块的hash
    }  

json对应的C++结构体

    
    
    typedef struct __transactions
    {
        std::string sender;
        std::string recipient;
        float amount;
    
        bool operator == (const struct __transactions & value) const
        {
            return
                this->sender == value.sender &&
                this->recipient == value.recipient &&
                this->amount == value.amount;
        }
    }Transactions;
    
    typedef struct __block
    {
        int index;
        time_t timestamp;
        std::list<Transactions> lst_ts;
        long int proof;
        std::string previous_hash;
    
        bool operator == (const struct __block & value) const
        {
            return
                this->index == value.index &&
                this->timestamp == value.timestamp &&
                this->previous_hash == value.previous_hash &&
                this->lst_ts == value.lst_ts &&
                this->proof == value.proof;
        }
    } Block;

