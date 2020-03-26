---
layout: post
title: C++从零开始区块链：区块链业务模块之基于boost的json读写
date: 发布于2018-09-06 10:43:03 +0800
categories: C++从零开始区块链
tag: 4
---

* content
{:toc}


    #include <boost/property_tree/ptree.hpp>
<!-- more -->

    #include <boost/property_tree/json_parser.hpp>
    
    std::string BlockChain::GetJsonFromBlock(Block &block)
    {
        boost::property_tree::ptree item;
    
        boost::property_tree::ptree lstts;
        {
            std::list<Transactions>::iterator it;
            for (it = block.lst_ts.begin(); it != block.lst_ts.end(); ++it)
            {
                boost::property_tree::ptree ts;
                ts.put("sender", it->sender);
                ts.put("recipient", it->recipient);
                ts.put("amount", it->amount);
                lstts.push_back(make_pair("", ts));
            }
        }
    
        item.put("index", block.index);
        item.put("timestamp", block.timestamp);
        item.put_child("transactions", lstts);
        item.put("proof", block.proof);
        item.put("previous_hash", block.previous_hash);
    
        std::stringstream is;
        boost::property_tree::write_json(is, item);
        return is.str();
    }
    
    std::string BlockChain::GetJsonFromTransactions(Transactions &ts)
    {
        boost::property_tree::ptree item;
    
        item.put("sender", ts.sender);
        item.put("recipient", ts.recipient);
        item.put("amount", ts.amount);
    
        std::stringstream is;
        boost::property_tree::write_json(is, item);
        return is.str();
    }
    
    Block BlockChain::GetBlockFromJson(const std::string &json)
    {
        Block block;
        std::stringstream ss(json);
        boost::property_tree::ptree pt;
        boost::property_tree::ptree array;
        boost::property_tree::read_json(ss, pt);
        block.index = pt.get<int>("index");
        block.previous_hash = pt.get<std::string>("previous_hash");
        block.proof = pt.get<long int>("proof");
        block.timestamp = pt.get<time_t>("timestamp");
        array = pt.get_child("transactions");
    
        for (auto v : array)
        {
            Transactions ts;
            ts.sender = v.second.get<std::string>("sender");
            ts.recipient = v.second.get<std::string>("recipient");
            ts.amount = v.second.get<float>("amount");
            block.lst_ts.push_back(ts);
        }
    
        return block;
    }
    
    Transactions BlockChain::GetTransactionsFromJson(const std::string &json)
    {
        Transactions ts;
        std::stringstream ss(json);
        boost::property_tree::ptree pt;
        boost::property_tree::read_json(ss, pt);
    
        ts.sender = pt.get<std::string>("sender");
        ts.recipient = pt.get<std::string>("recipient");
        ts.amount = pt.get<float>("amount");
    
        return ts;
    }
    
    std::string BlockChain::GetJsonFromBlockList()
    {
        int i = 0;
    
        boost::property_tree::ptree item;
    
        boost::property_tree::ptree pblock;
        {
            std::list<Block>::iterator bit;
    
            pthread_mutex_lock(&m_mutexBlock);
            for (bit = m_lst_block.begin(); bit != m_lst_block.end(); ++bit)
            {
                boost::property_tree::ptree b;
                boost::property_tree::ptree pts;
                {
                    std::list<Transactions>::iterator tit;
                    for (tit = bit->lst_ts.begin(); tit != bit->lst_ts.end(); ++tit)
                    {
                        boost::property_tree::ptree t;
                        t.put("sender", tit->sender);
                        t.put("recipient", tit->recipient);
                        t.put("amount", tit->amount);
                        pts.push_back(make_pair("", t));
                    }
                }
    
                b.put("index", bit->index);
                b.put("timestamp", bit->timestamp);
                b.put_child("transactions", pts);
                b.put("proof", bit->proof);
                b.put("previous_hash", bit->previous_hash);
                pblock.push_back(make_pair("", b));
    
                ++i;
            }
            pthread_mutex_unlock(&m_mutexBlock);
        }
    
        item.put_child("chain", pblock);
        item.put("length", i);
    
        std::stringstream is;
        boost::property_tree::write_json(is, item);
        return is.str();
    }
    
    std::string BlockChain::GetJsonFromTransactionsList()
    {
        int i = 0;
    
        boost::property_tree::ptree item;
    
        boost::property_tree::ptree pts;
        {
            std::list<Transactions>::iterator bit;
    
            pthread_mutex_lock(&m_mutexTs);
            for (bit = m_lst_ts.begin(); bit != m_lst_ts.end(); ++bit)
            {
                boost::property_tree::ptree b;
    
                b.put("sender", bit->sender);
                b.put("recipient", bit->recipient);
                b.put("amount", bit->amount);
    
                pts.push_back(make_pair("", b));
    
                ++i;
            }
            pthread_mutex_unlock(&m_mutexTs);
        }
    
        item.put_child("transactions", pts);
        item.put("length", i);
    
        std::stringstream is;
        boost::property_tree::write_json(is, item);
        return is.str();
    }
    
    std::list<Block> BlockChain::GetBlockListFromJson(const std::string &json)
    {
        std::list<Block> lst_block;
        std::stringstream ss(json);
        boost::property_tree::ptree pt;
        boost::property_tree::ptree barray;
        boost::property_tree::read_json(ss, pt);
        barray = pt.get_child("chain");
    
        for (auto bv : barray)
        {
            Block block;
            boost::property_tree::ptree tarray;
    
            block.index = bv.second.get<int>("index");
            block.previous_hash = bv.second.get<std::string>("previous_hash");
            block.proof = bv.second.get<long int>("proof");
            block.timestamp = bv.second.get<time_t>("timestamp");
            tarray = bv.second.get_child("transactions");
    
            for (auto tv : tarray)
            {
                Transactions ts;
                ts.sender = tv.second.get<std::string>("sender");
                ts.recipient = tv.second.get<std::string>("recipient");
                ts.amount = tv.second.get<float>("amount");
                block.lst_ts.push_back(ts);
            }
    
            lst_block.push_back(block);
        }
    
        return lst_block;
    }
    
    void BlockChain::GetTransactionsListFromJson(const std::string &json)
    {
        pthread_mutex_lock(&m_mutexTs);
        m_lst_ts.clear();
        pthread_mutex_unlock(&m_mutexTs);
    
        std::stringstream ss(json);
        boost::property_tree::ptree pt;
        boost::property_tree::ptree array;
        boost::property_tree::read_json(ss, pt);
        array = pt.get_child("transactions");
    
        for (auto v : array)
        {
            Transactions ts;
            ts.sender = v.second.get<std::string>("sender");
            ts.recipient = v.second.get<std::string>("recipient");
            ts.amount = v.second.get<float>("amount");
    
            pthread_mutex_lock(&m_mutexTs);
            m_lst_ts.push_back(ts);
            pthread_mutex_unlock(&m_mutexTs);
        }
    }

