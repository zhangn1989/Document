---
layout: post
title: C++从零开始区块链：区块链业务模块之主链同步
date: 发布于2018-09-06 11:27:49 +0800
categories: C++从零开始区块链
tag: 4
---

* content
{:toc}

同样是采用一个简单，但效率低下的方案，遍历自己的链和其他节点的链，谁的长谁的就是主链。  

<!-- more -->
然后将自己的链和主链进行比较，将自己的链上的区块挂在主链上，挂的同时验证一下自己的区块是否已经存在于主链上，如果存在就跳过。

    
    
    void BlockChain::MergeBlockChain(const std::string &json)
    {
        std::list<Block> lst_block = GetBlockListFromJson(json);
        lst_block.pop_front();
    
        if (lst_block.size() > m_lst_block.size())
        {
            std::list<Block>::iterator it;
    
            pthread_mutex_lock(&m_mutexBlock);
    
            for (it = m_lst_block.begin(); it != m_lst_block.end(); ++it)
            {
                Block block = lst_block.back();
                if(it->proof <= block.proof)
                    continue;
                std::string strJson = GetJsonFromBlock(block);
                std::string strHash = Cryptography::GetHash(strJson.c_str(), strJson.length());
    
                it->index = block.index + 1;
                it->previous_hash = strHash;
                lst_block.push_back(*it);
            }
    
            m_lst_block = lst_block;
    
            pthread_mutex_unlock(&m_mutexBlock);
        }
        else
        {
            std::list<Block>::iterator it;
            for (it = lst_block.begin(); it != lst_block.end(); ++it)
            {
                pthread_mutex_lock(&m_mutexBlock);
    
                Block block = m_lst_block.back();
                if (it->proof <= block.proof)
                {
                    pthread_mutex_unlock(&m_mutexBlock);
                    continue;
                }
                std::string strJson = GetJsonFromBlock(block);
                std::string strHash = Cryptography::GetHash(strJson.c_str(), strJson.length());
    
                it->index = block.index + 1;
                it->previous_hash = strHash;
                m_lst_block.push_back(*it);
    
                pthread_mutex_unlock(&m_mutexBlock);
            }
        }
    }

