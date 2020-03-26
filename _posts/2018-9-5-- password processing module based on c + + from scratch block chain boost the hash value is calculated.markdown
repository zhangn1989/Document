---
layout: post
title: C++从零开始区块链：密码处理模块之基于boost的哈希值计算
date: 发布于2018-09-05 14:51:50 +0800
categories: C++从零开始区块链
tag: 4
---

* content
{:toc}

这个没啥可说的，直接上代码
<!-- more -->


    
    
    #include <boost/uuid/sha1.hpp>
    std::string Cryptography::GetHash(void const* buffer, std::size_t len)
    {
        std::stringstream ss;
        boost::uuids::detail::sha1 sha;
        sha.process_bytes(buffer, len);
        unsigned int digest[5];      //摘要的返回值
        sha.get_digest(digest);
        for (int i = 0; i < 5; ++i)
            ss << std::hex << digest[i];
    
        return ss.str();
    }

