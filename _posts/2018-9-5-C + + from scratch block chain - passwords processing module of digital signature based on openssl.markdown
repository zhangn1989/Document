---
layout: post
title: C++从零开始区块链：密码处理模块之基于openssl的数字签名
date: 发布于2018-09-05 15:12:50 +0800
categories: C++从零开始区块链
tag: 4
---

关于数字签名的原理请自行百度，我们这里使用椭圆曲线加密算法来进行签名，下面上代码

<!-- more -->

    
    
    void Cryptography::Createkey(KeyPair &keyPair)
    {
        unsigned char *p = NULL;
        keyPair.priKey.len = -1;
        keyPair.pubKey.len = -1;
    
        EC_GROUP *group = EC_GROUP_new_by_curve_name(NID_secp256k1);
        if (!group)
            return;
    
        EC_KEY *key = EC_KEY_new();
        if (!key)
        {
            EC_GROUP_free(group);
            return;
        }
    
        if (!EC_KEY_set_group(key, group))
        {
            EC_GROUP_free(group);
            EC_KEY_free(key);
            return;
        }
    
        if (!EC_KEY_generate_key(key))
        {
            EC_GROUP_free(group);
            EC_KEY_free(key);
            return;
        }
    
        if (!EC_KEY_check_key(key))
        {
            EC_GROUP_free(group);
            EC_KEY_free(key);
            return;
        }
    
        keyPair.priKey.len = i2d_ECPrivateKey(key, NULL);
        if (keyPair.priKey.len > (int)sizeof(keyPair.priKey.key))
        {
            keyPair.priKey.len = -1;
            EC_GROUP_free(group);
            EC_KEY_free(key);
            return;
        }
        p = keyPair.priKey.key;
        keyPair.priKey.len = i2d_ECPrivateKey(key, &p);
    
        keyPair.pubKey.len = i2o_ECPublicKey(key, NULL);
        if (keyPair.pubKey.len > (int)sizeof(keyPair.pubKey.key))
        {
            keyPair.pubKey.len = -1;
            EC_GROUP_free(group);
            EC_KEY_free(key);
            return;
        }
        p = keyPair.pubKey.key;
        keyPair.pubKey.len = i2o_ECPublicKey(key, &p);
    
        EC_GROUP_free(group);
        EC_KEY_free(key);
    }
    
    bool Cryptography::Signature(const KeyData &priKey, const void *data, int datalen, unsigned char *sign, size_t signszie, unsigned int *signlen)
    {
        EC_KEY *ec_key = NULL;
        const unsigned char *pp = (const unsigned char *)priKey.key;
        ec_key = d2i_ECPrivateKey(&ec_key, &pp, priKey.len);
        if (!ec_key)
            return false;
    
        if (ECDSA_size(ec_key) > (int)signszie)
        {
            EC_KEY_free(ec_key);
            return false;
        }
    
        if (!ECDSA_sign(0, (unsigned char *)data, datalen, sign, signlen, ec_key))
        {
            EC_KEY_free(ec_key);
            return false;
        }
    
        EC_KEY_free(ec_key);
        return true;
    }
    
    int Cryptography::Verify(const KeyData &pubkey, const char *data, int datalen, const unsigned char *sign, size_t signszie, unsigned int signlen)
    {
        int ret = -1;
        EC_KEY *ec_key = NULL;
        EC_GROUP *ec_group = NULL;
        const unsigned char *pp = (const unsigned char *)pubkey.key;
    
        ec_key = EC_KEY_new();
        if (!ec_key)
            return ret;
    
        if (ECDSA_size(ec_key) > (int)signszie)
        {
            EC_KEY_free(ec_key);
            return ret;
        }
    
        ec_group = EC_GROUP_new_by_curve_name(NID_secp256k1);
        if (!ec_group)
        {
            EC_KEY_free(ec_key);
            return ret;
        }
    
        if (!EC_KEY_set_group(ec_key, ec_group))
        {
            EC_GROUP_free(ec_group);
            EC_KEY_free(ec_key);
            return ret;
        }
    
        ec_key = o2i_ECPublicKey(&ec_key, &pp, pubkey.len);
        if (!ec_key)
        {
            EC_GROUP_free(ec_group);
            EC_KEY_free(ec_key);
            return ret;
        }
    
        ret = ECDSA_verify(0, (const unsigned char*)data, datalen, sign,
            signlen, ec_key);
    
        EC_GROUP_free(ec_group);
        EC_KEY_free(ec_key);
        return ret;
    }

* content
{:toc}


