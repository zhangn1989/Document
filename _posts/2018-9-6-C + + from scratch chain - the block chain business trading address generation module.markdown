---
layout: post
title: C++从零开始区块链：区块链业务模块之交易地址生成
date: 发布于2018-09-06 10:47:01 +0800
categories: C++从零开始区块链
tag: 4
---

在比特币中，为了避免地址重复、安全性等各种问题，比特币的地址的生成过程是很繁琐的。我们这里由于只是学习其原理，一些实际中可能会遇到的问题就不予考虑了，将地址生成的过程最大程度的简化。  

<!-- more -->
简化后的流程是：首先生成一对秘钥，然后对公钥取哈希，再将哈希转成BASE64，最后生成的一组BASE64编码的字符串就是最终看到的地址了，代码很简单，就两行

    
    
    std::string BlockChain::CreateNewAddress(const KeyPair &keyPair)
    {
        std::string hash = Cryptography::GetHash(keyPair.pubKey.key, keyPair.pubKey.len);
        return Cryptography::Base64Encode(hash.c_str(), hash.length());
    }

* content
{:toc}


