---
layout: post
title: C++从零开始区块链：区块链业务模块之余额检查
date: 发布于2018-09-06 11:11:11 +0800
categories: C++从零开始区块链
tag: 4
---

比特币中的余额检查实现起来好麻烦，严格来说比特币中并没有所谓的余额，具体请读者自行百度比特币相关的资料。  

<!-- more -->
在本例中，我们采用一个效率低下，但很简单的方法：遍历整个区块链的所有交易，查找要查询的地址参与的所有交易，如果目标地址是支出方，就减少，是收入方就增加，便利后的结果就余额

    
    
    int BlockChain::CheckBalances(const std::string &addr)
    {
        int balan = 0;
    
        std::list<Block>::iterator bit;
        std::list<Transactions>::iterator tit;
    
        pthread_mutex_lock(&m_mutexBlock);
        for (bit = m_lst_block.begin(); bit != m_lst_block.end(); ++bit)
        {
            for (tit = bit->lst_ts.begin(); tit != bit->lst_ts.end(); ++tit)
            {
                if (tit->recipient == addr)
                    balan += tit->amount;
                else if (tit->sender == addr)
                    balan -= tit->amount;
            }
        }
        pthread_mutex_unlock(&m_mutexBlock);
    
        return balan;
    }

* content
{:toc}


