---
layout: post
title: C++从零开始区块链：一个简单的总体介绍
date: 发布于2018-09-05 14:39:01 +0800
categories: C++从零开始区块链
tag: 4
---

本系列博文对理论性的东西叙述的不多，主要是以代码为主，本例是模仿比特币实现的一个电子货币记账系统。  

<!-- more -->
虽然不打算介绍理论性的东西，但交易流程还是要说一下的，毕竟所有的代码都是为这个交易流程服务的。

  * 交易流程
  * 程序设计
    * Cryptography
    * P2PNode
    * BlockChain
  * 完整代码

# 交易流程

当发起一个交易的时候，交易发起方先准备一条“地址a要向地址b转账n个币”的消息，然后用地址a的私钥进行数字签名，用以表明发起方对地址a的所有权，最后再把该消息和签名信息在P2P网络上对其他节点进行广播。  
其他节点收到广播后，先对消息的数字签名进行验证，验证通过后再检查余额是否够用。全部验证通过后将该交易记在自己的交易列表上。至此，交易流程结束。  
虽然交易流程结束了，但还没有记到区块链上，那怎么记到区块链上呢？挖矿啊。当一个节点找到了一个工作量证明，就将自己记录的交易列表打包记到一个区块上，然后再向所有的节点进行广播，告诉其他人。  
其他节点收到区块后，对工作量证明进行验证，验证后将区块挂在区块链上，再将该区块上的交易列表和自己的交易列表进行比对，将自己交易列表中已经在区块上记录的消息删除。  
当然，比特币中的交易流程要比这复杂的多，我们只为学习，把流程进行简化了。

# 程序设计

综上所述，可以看出应该有三个主要模块：数字签名，P2P网络和区块链逻辑。以下是对三个模块的定义：

## Cryptography

该类主要用于处理数字签名，编码解码等数学和密码相关功能。

    
    
    typedef struct __keydata
    {
        size_t len;
        unsigned char key[256];
    } KeyData;
    
    typedef struct __KeyPair
    {
        KeyData pubKey;
        KeyData priKey;
    } KeyPair;
    
    class Cryptography
    {
    public:
        static std::string GetHash(void const* buffer, std::size_t len);
        static std::string Base64Encode(const void*buff, int len);
        static void Base64Decode(const std::string &str64, void *outbuff, size_t outsize, size_t *outlen);
        static void Createkey(KeyPair &keyPair);
        static bool Signature(const KeyData &priKey, const void *data, int datalen, unsigned char *sign, size_t signszie, unsigned int *signlen);
        static int Verify(const KeyData &pubkey, const char *data, int datalen, const unsigned char *sign, size_t signszie, unsigned int signlen);
        static std::string StringToLower(const std::string &str);
        static bool CompareNoCase(const std::string &strA, const std::string &strB);
        static std::vector<std::string> StringSplit(const std::string &str, const char sep);
    
    protected:
        Cryptography();
        virtual ~Cryptography();
    
    private:
    
    };

## P2PNode

该类主要处理网络通信相关功能

    
    
    typedef enum
    {
        p2p_transaction = 0x2000,
        p2p_bookkeeping,
        p2p_result,
        p2p_merge,
        p2p_blockchain,
        p2p_max
    } P2PCommand;
    
    typedef struct st_broadcast
    {
        KeyData pubkey;
        char json[1024];
        unsigned int signlen;
        unsigned char sign[1024];
    } __attribute__((packed))
        BroadcastMessage;
    
    typedef struct st_p2pMessage
    {
        int index;
        int total;
        char messHash[64];
        P2PCommand cmd;
        size_t length;
        char mess[MAX_P2P_SIZE];
    } __attribute__((packed))
        P2PMessage;
    
    typedef struct st_p2pResult
    {
        int index;
        char messHash[64];
    
        bool operator == (const struct st_p2pResult & value) const
        {
            return
                this->index == value.index &&
                !strcmp(this->messHash, value.messHash);
        }
    } __attribute__((packed))
        P2PResult;
    
    class P2PNode
    {
    public:
        static P2PNode *Instance(const char *if_name);
        void Listen();
        void Broadcast(P2PCommand cmd, const BroadcastMessage &bm);
        void MergeChain();
    
    protected:
        P2PNode(const char *if_name);
        virtual ~P2PNode();
    
    private:
        int m_sock;
        Node m_selfNode;
        Node m_otherNode;
        char *m_otherIP;
        int m_otherPort;
        pthread_t m_tid;
        pthread_mutex_t m_mutexPack;
        pthread_mutex_t m_mutexResult;
    
        struct sockaddr_in m_serverAddr;
        struct sockaddr_in m_localAddr;
        struct sockaddr_in m_recvAddr;
    
        typedef struct st_package
        {
            int total;
            char messHash[64];
            P2PCommand cmd;
            std::map<int, std::string> mapMess;
    
            bool operator == (const struct st_package & value) const
            {
                return
                    this->total == value.total &&
                    this->cmd == value.cmd &&
                    !strcmp(this->messHash, value.messHash);
            }
        } Package;
    
        std::list<Package> m_lstPackage;
        std::list<P2PResult> m_lstResult;
    
        static void *threadFunc(void *arg);
        void threadHandler();
        void combinationPackage(P2PMessage &mess);
        int get_local_ip(const char *ifname, char *ip);
        void sendMessage(P2PMessage &mess);
        void sendBlockChain();
    };

## BlockChain

该类处理区块链相关业务逻辑

    
    
    typedef struct __transactions
    {
        std::string sender;
        std::string recipient;
        float amount;
    
        bool operator == (const struct __transactions & value) const
        {
            return
                this->sender == value.sender &&
                this->recipient == value.recipient &&
                this->amount == value.amount;
        }
    }Transactions;
    
    typedef struct __block
    {
        int index;
        time_t timestamp;
        std::list<Transactions> lst_ts;
        long int proof;
        std::string previous_hash;
    
        bool operator == (const struct __block & value) const
        {
            return
                this->index == value.index &&
                this->timestamp == value.timestamp &&
                this->previous_hash == value.previous_hash &&
                this->lst_ts == value.lst_ts &&
                this->proof == value.proof;
        }
    } Block;
    
    class BlockChain
    {
    public:
        static BlockChain *Instance();
    
        std::string GetJsonFromBlock(Block &block);
        std::string GetJsonFromTransactions(Transactions &ts);
        Block GetBlockFromJson(const std::string &json);
        Transactions GetTransactionsFromJson(const std::string &json);
        std::string GetJsonFromBlockList();
        std::string GetJsonFromTransactionsList();
        std::list<Block> GetBlockListFromJson(const std::string &json);
        void GetTransactionsListFromJson(const std::string &json);
        std::string CreateNewAddress(const KeyPair &keyPair);
        Transactions CreateTransactions(const std::string &sender, const std::string &recipient, float amount);
        Block CreateBlock(int index, time_t timestamp, long int proof);
        int WorkloadProof(int last_proof);
        bool WorkloadVerification(int proof);
        std::string Mining(const std::string &addr);
        int CheckBalances(const std::string &addr);
        void DeleteDuplicateTransactions(const Block &block);
        void MergeBlockChain(const std::string &json);
    
        inline void InsertBlock(const Block &block)
        {
            pthread_mutex_lock(&m_mutexBlock);
            if (m_lst_block.end() == std::find(m_lst_block.begin(), m_lst_block.end(), block))
            {
                m_lst_block.push_back(block);
            }
            pthread_mutex_unlock(&m_mutexBlock);
        }
    
        inline void InsertTransactions(const Transactions &ts)
        {
            pthread_mutex_lock(&m_mutexTs);
            if (m_lst_ts.end() == std::find(m_lst_ts.begin(), m_lst_ts.end(), ts))
            {
                m_lst_ts.push_back(ts);
            }
            pthread_mutex_unlock(&m_mutexTs);
        }
    
        inline Block GetLastBlock()
        {
            Block block;
            pthread_mutex_lock(&m_mutexBlock);
            block = m_lst_block.back();
            pthread_mutex_unlock(&m_mutexBlock);
            return block;
        }
    
    protected:
        BlockChain();
        virtual ~BlockChain();
    
    private:
        std::list<Transactions> m_lst_ts;
        std::list<Block> m_lst_block;
        pthread_mutex_t m_mutexTs;
        pthread_mutex_t m_mutexBlock;
    };

具体实现后面会细讲。

# 完整代码

完整代码[戳这里](https://github.com/zhangn1989/shacoin)。

* content
{:toc}


