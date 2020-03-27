---
layout: post
title: C++从零开始区块链：区块链业务模块之重复交易检测
date: 发布于2018-09-06 11:22:54 +0800
categories: C++从零开始区块链
tag: 4
---

* content
{:toc}

想象这样一个场景：  

<!-- more -->
节点a广播了一条消息，节点b和节点c都收到并记录在自己的交易列表中了。  
然后节点b和节点c挖矿。  
当节点b挖矿成功，将a的交易打包到区块中，并在网络上广播。  
这时节点c接收到节点b的挖矿成功的广播，区块验证通过后挂到自己的区块上，然后继续挖矿。  
当节点c也挖矿成功后，将自己的交易列表打包程区块在节点上广播。  
而节点d是个小透明，先接收到b的区块，后接收到c的区块，然后将自己的区块同步到主链上。  
于是问题来了，b和c都将a的交易记录了一次，并都打包成区块，又都被挂到了主链上。其造成的结果就是a明明只广播了一条交易，但主链上却记录了a的两次交易，很明显是错误的。  
那么怎么解决呢？就是在每个节点的接收到一个挖矿广播后，用自己的交易列表和区块的交易列表进行比对，如果发现自己的列表中的某个交易已经记录在区块上了，就将自己的该交易记录删除。  
单从交易的付款方，收款方，交易金额来区分是否是同一支交易是不合适的，因为很有可能两个人进行了多次金额相同的交易。为解决这个问题，需要在交易中加入一个随机值或者是时间戳。但本例只为演示，就不加了。

    
    
    void BlockChain::DeleteDuplicateTransactions(const Block &block)
    {
        std::list<Transactions>::iterator selfIt;
        std::list<Transactions>::const_iterator otherIt;
    
        pthread_mutex_lock(&m_mutexTs);
        for (selfIt = m_lst_ts.begin(); selfIt != m_lst_ts.end();)
        {
            if (block.lst_ts.end() != std::find(block.lst_ts.begin(), block.lst_ts.end(), *selfIt))
            {
                selfIt = m_lst_ts.erase(selfIt);
            }
            else
            {
                ++selfIt;
            }
        }
        pthread_mutex_unlock(&m_mutexTs);
    }

