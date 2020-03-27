---
layout: post
title: C++从零开始区块链：密码处理模块之基于openssl的BASE64编码与解码
date: 发布于2018-09-05 15:10:00 +0800
categories: C++从零开始区块链
tag: 4
---

* content
{:toc}


    #include <openssl/rsa.h>

<!-- more -->
    #include <openssl/x509.h>
    #include <openssl/bn.h>
    #include <openssl/evp.h>
    #include <openssl/bio.h>
    #include <openssl/buffer.h>
    
    std::string Cryptography::Base64Encode(const void*buff, int len)
    {
        int i;
        std::string str;
        int outl = -1;
        char out[(1024 * 5) / 3];
        EVP_ENCODE_CTX *ctx = EVP_ENCODE_CTX_new();
    
        if (!ctx)
            return str;
    
        EVP_EncodeInit(ctx);
    
        for (i = 0; i < len / 1024; ++i)
        {
            memset(out, 0, sizeof(out));
            EVP_EncodeUpdate(ctx, (unsigned char *)out, &outl, (unsigned char *)buff + i * 1024, 1024);
            str += std::string(out, outl);
        }
    
        memset(out, 0, sizeof(out));
        EVP_EncodeUpdate(ctx, (unsigned char *)out, &outl, (unsigned char *)buff + i * 1024, len % 1024);
        str += std::string(out, outl);
    
        memset(out, 0, sizeof(out));
        EVP_EncodeFinal(ctx, (unsigned char *)out, &outl);
        str += std::string(out, outl);
    
        EVP_ENCODE_CTX_free(ctx);
    
        str.erase(std::remove(str.begin(), str.end(), '\n'), str.end());
    
        return str;
    }
    
    void Cryptography::Base64Decode(const std::string &str64, void *outbuff, size_t outsize, size_t *outlen)
    {
        unsigned int i;
        unsigned int inlen = str64.length();
        if (outsize * 5 / 3 < inlen)
        {
            *outlen = -1;
            return;
        }
    
        int outl = -1;
        char out[(1024 * 5) / 3];
        char *p = (char *)outbuff;
    
        EVP_ENCODE_CTX *ctx = EVP_ENCODE_CTX_new();
    
        if (!ctx)
        {
            *outlen = -1;
            return;
        }
    
        EVP_DecodeInit(ctx);
    
        for (i = 0; i < str64.length() / 1024; ++i)
        {
            memset(out, 0, sizeof(out));
            EVP_DecodeUpdate(ctx, (unsigned char *)out, &outl, (unsigned char *)str64.c_str() + i * 1024, 1024);
            memcpy(p, out, outl);
            p += outl;
            *outlen += outl;
        }
    
        memset(out, 0, sizeof(out));
        EVP_DecodeUpdate(ctx, (unsigned char *)out, &outl, (unsigned char *)str64.c_str() + i * 1024, str64.length() % 1024);
        memcpy(p, out, outl);
        p += outl;
        *outlen += outl;
    
        memset(out, 0, sizeof(out));
        EVP_DecodeFinal(ctx, (unsigned char *)out, &outl);
        memcpy(p, out, outl);
        p += outl;
        *outlen += outl;
    }

