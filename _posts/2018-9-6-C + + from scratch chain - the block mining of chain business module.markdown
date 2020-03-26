---
layout: post
title: C++从零开始区块链：区块链业务模块之挖矿
date: 发布于2018-09-06 11:00:24 +0800
categories: C++从零开始区块链
tag: 4
---

* content
{:toc}

挖矿就是找到一个满足工作量验证条件的工作量证明，当一个节点找到了一个工作量证明之后，首先以给自己添加一个挖矿交易的形式进行金额奖励，即添加一个付款地址为0，收款地址为自己的交易到自己的交易记录。然后录他会将自己记录的所有交易信息打包程一个区块，并向其他节点进行广播。其他节点接收到以后会对工作量证明进行验证，验证通过后就会将该区块挂到自己的区块链上，等下次与主链同步的时候同步到主链上。  
<!-- more -->

为了简化验证一个工作量证明是否已经存在与链上的工作，每次挖矿都从上一个区块的工作量证明开始。

    
    
    std::string BlockChain::Mining(const std::string &addr)
    {
        //挖矿的交易，交易支出方地址为0
        //每次挖矿成功奖励10个币
        Block last = GetLastBlock();
        int proof = WorkloadProof(last.proof);
        Transactions ts = CreateTransactions("0", addr, 10);
        InsertTransactions(ts);
        Block block = CreateBlock(last.index + 1, time(NULL), proof);
        return GetJsonFromBlock(block);
    }

以上就是挖矿流程，创建交易和区块将在下篇介绍，如何广播到P2P网络中以后再介绍。

