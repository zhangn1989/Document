---
layout: post
title: C++从零开始区块链：区块链业务模块之工作量证明与验证
date: 发布于2018-09-06 10:50:03 +0800
categories: C++从零开始区块链
tag: 4
---

原则上说，工作量证明算法应该是计算困难，验证容易，但我们这里只为学习，一切从简，使用一个简单的工作量证明算法：先取一个字符串，如“Hello

<!-- more -->
Shacoin!”，然后取一个自然整数，再将该整数转成字符串，衔接到前面的字符串后面，形成一个新的字符串。然后将这个新字符串取哈希，判断哈希的最后一位是不是为0，如果是，则工作量证明通过，不是再将整数加一，继续重复上面的步骤，直到满足验证条件为止。为了简化对该工作量证明是否已存在的验证工作，每次证明都从上一次的结果处开始，并依次递增。  
工作量验证要容易，直接把证明的结果作为参数，衔接到固定字符串后面，然后取哈希，再判断最后一位是否为0，如果是验证通过，否则验证失败。  
如果想要提高工作量证明的难度，把验证后一位是不是0提高到验证后面的两位，三位是不是连续的0即可

    
    
    int BlockChain::WorkloadProof(int last_proof)
    {
        std::string strHash;
        std::string strTemp;
        int proof = last_proof + 1;
    
        std::string str = "Hello Shacoin!";
    
        while (true)
        {
            strTemp = str + std::to_string(proof);
            strHash = Cryptography::GetHash(strTemp.c_str(), strTemp.length());
            if (strHash.back() == '0')
                return proof;
            else
                ++proof;
        }
    }
    
    bool BlockChain::WorkloadVerification(int proof)
    {
        std::string str = "Hello Shacoin!" + std::to_string(proof);
        std::string strHash = Cryptography::GetHash(str.c_str(), str.length());
        return (strHash.back() == '0');
    }

* content
{:toc}


