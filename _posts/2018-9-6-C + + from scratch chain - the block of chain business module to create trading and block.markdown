---
layout: post
title: C++从零开始区块链：区块链业务模块之创建交易和区块
date: 发布于2018-09-06 11:07:10 +0800
categories: C++从零开始区块链
tag: 4
---

创建交易简单，直接给结构体赋值就行

<!-- more -->

    
    
        Transactions BlockChain::CreateTransactions(const std::string &sender, const std::string &recipient, float amount)
    {
        Transactions ts;
        ts.sender = sender;
        ts.recipient = recipient;
        ts.amount = amount;
        return ts;
    }

创建区块需要从上一个区块中获取相关信息，然后将已经记录的交易打包加到区块中，最后再将之前的交易记录清空  
下面的代码参数设计的有些重复，只要一个工作量证明的参数即可，其他参数都可以从上一个区块中读取到，但接口改动都很麻烦，我这里就不改了

    
    
    Block BlockChain::CreateBlock(int index, time_t timestamp, long int proof)
    {
        Block block;
    
        ShaCoin::Block last = GetLastBlock();
        std::string strLastBlock = GetJsonFromBlock(last);
    
        block.index = index;
        block.timestamp = timestamp;
        block.proof = proof;
        block.previous_hash = Cryptography::GetHash(strLastBlock.c_str(), strLastBlock.length());
    
        pthread_mutex_lock(&m_mutexTs);
        block.lst_ts = m_lst_ts;
        m_lst_ts.clear();
        pthread_mutex_unlock(&m_mutexTs);
    
        return block;
    }

* content
{:toc}


