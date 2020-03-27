---
layout: post
title: C++从零开始区块链：P2P模块之UDP数据包分组排序
date: 发布于2018-09-06 10:21:46 +0800
categories: C++从零开始区块链
tag: 4
---

udp的特点是不可靠，不连接，数据发过去就完事，至于对方收没收到就不管了。  

<!-- more -->
在使用udp进行通信的时候，要在应用层做分组、排序、组包、校验等工作。  
发送方现将要发送的数据切片，所有的切片组成一组，标上组号，每个切片根据原始数据的顺序有个组内编号。  
发送的时候，每次发送一个切片，并等待接收数据接收方反馈收到数据的信息，如果没有接收到数据接收方的反馈信息就继续发送，接收到数据接收方发送的反馈信息位置。  
数据接收方接收到数据后先给发送方发送一个数据接收成功的反馈，然后对数据进行分组存储。存储之前要先检验一下该块数据是否已经接受过了，因为虽然接收方成功的接收到了数据，并发送了反馈信息给发送方，但发送方可能没有接收到反馈信息，发送方会判定是发送失败，从而再次发送该块数据，从而导致了接收方对同一块数据重复接收了两次。  
当接收方接收到的数据块数与发送方发送的总块数相同时，说明该数据已经全部接收完成，对数据进行排序组合，最后再进行校验，至此一个数据发送完成。  
为了组号处理方便，直接用完整信息的hash作为组号，数据重新组装完成后可以直接用组号进行校验。每一组存到一个map里，有map根据序号自动排序。

    
    
    //数据切片
    void P2PNode::sendBlockChain()
    {
        P2PMessage mess;
        int i = 0;
        BlockChain *bc = BlockChain::Instance();
        std::string strBcJson = bc->GetJsonFromBlockList();
        std::string strBcHash = Cryptography::GetHash(strBcJson.c_str(), strBcJson.length());
        int total = strBcJson.length() / MAX_P2P_SIZE + 1;
    
        for (i = 0; i < total - 1; ++i)
        {
            memset(&mess, 0, sizeof(mess));
            mess.cmd = p2p_blockchain;
            mess.index = i;
            mess.total = total;
            mess.length = MAX_P2P_SIZE;
            strcpy(mess.messHash, strBcHash.c_str());
            strncpy(mess.mess, strBcJson.c_str() + i * MAX_P2P_SIZE, MAX_P2P_SIZE);
    
            sendMessage(mess);
        }
    
        memset(&mess, 0, sizeof(mess));
        mess.cmd = p2p_blockchain;
        mess.index = i;
        mess.total = total;
        mess.length = strBcJson.length() % MAX_P2P_SIZE;
        strcpy(mess.messHash, strBcHash.c_str());
        strncpy(mess.mess, strBcJson.c_str() + i * MAX_P2P_SIZE, mess.length);
    
        sendMessage(mess);
    }
    
    //数据发送
    void P2PNode::sendMessage(P2PMessage &mess)
    {
        sockaddr_in otherAddr;
        memset(&otherAddr, 0, sizeof(otherAddr));
        otherAddr.sin_family = AF_INET;
        otherAddr.sin_port = htons(m_otherPort);
        otherAddr.sin_addr.s_addr = inet_addr(m_otherIP);
    
        P2PResult result;
        result.index = mess.index;
        memcpy(result.messHash, mess.messHash, sizeof(result.messHash));
    
        while (1)
        {
            if (sendto(m_sock, &mess, sizeof(P2PMessage), 0, (struct sockaddr*)&otherAddr, sizeof(otherAddr)) < 0)
            {
                perror("sendto");
                close(m_sock);
                exit(4);
            }
    
            sleep(1);
    
            pthread_mutex_lock(&m_mutexResult);
            if (m_lstResult.end() == std::find(m_lstResult.begin(), m_lstResult.end(), result))
            {
                pthread_mutex_unlock(&m_mutexResult);
                continue;
            }
    
            m_lstResult.remove(result);
            pthread_mutex_unlock(&m_mutexResult);
            break;
        }
    }
    
    //数据接收
    void P2PNode::combinationPackage(P2PMessage &mess)
    {
        Package package;
        int index = mess.index;
        std::list<Package>::iterator it;
    
        pthread_mutex_lock(&m_mutexPack);
        for (it = m_lstPackage.begin(); it != m_lstPackage.end(); ++it)
        {
            if (!strcmp(it->messHash, mess.messHash))
                break;
        }
    
        if (it == m_lstPackage.end())
        {
            package.total = mess.total;
            package.cmd = mess.cmd;
            memcpy(package.messHash, mess.messHash, sizeof(package.messHash));
            package.mapMess.insert(std::pair<int, std::string>(index, std::string(mess.mess, mess.length)));
            m_lstPackage.push_back(package);
        }
        else
        {
            it->mapMess.insert(std::pair<int, std::string>(index, std::string(mess.mess, mess.length)));
            package = *it;
        }
        pthread_mutex_unlock(&m_mutexPack);
    
        if (package.total == (int)package.mapMess.size())
        {
            std::string str;
            std::map<int, std::string>::iterator mapIt;
            for (mapIt = package.mapMess.begin(); mapIt != package.mapMess.end(); ++mapIt)
            {
                str += mapIt->second;
            }
    
            BlockChain *blockChain = BlockChain::Instance();
    
            switch (package.cmd)
            {
            case p2p_transaction:
            {
                BroadcastMessage bm;
                memset(&bm, 0, sizeof(bm));
                memcpy(&bm, str.c_str(), str.length());
    
                std::string strHash = ShaCoin::Cryptography::GetHash(bm.json, strlen(bm.json));
    
                Transactions ts = blockChain->GetTransactionsFromJson(bm.json);
                int balan = blockChain->CheckBalances(ts.sender);
                if (balan < ts.amount)
                    break;
    
                if (Cryptography::Verify(bm.pubkey, strHash.c_str(), strHash.length(), bm.sign, sizeof(bm.sign), bm.signlen) < 1)
                    break;
    
                blockChain->InsertTransactions(ts);
            }
                break;
            case p2p_bookkeeping:
            {
                BroadcastMessage bm;
                memset(&bm, 0, sizeof(bm));
                memcpy(&bm, str.c_str(), str.length());
    
                Block block = blockChain->GetBlockFromJson(std::string(bm.json, strlen(bm.json)));
                if (block.proof > blockChain->GetLastBlock().proof && blockChain->WorkloadVerification(block.proof))
                {
                    blockChain->DeleteDuplicateTransactions(block);
                    blockChain->InsertBlock(block);
                }
            }
                break;
            case p2p_result:
                break;
            case p2p_merge:
                sendBlockChain();
                break;
            case p2p_blockchain:
                blockChain->MergeBlockChain(str);
                break;
            default:
                break;
            }
    
            m_lstPackage.remove(package);
        }
    }

* content
{:toc}


