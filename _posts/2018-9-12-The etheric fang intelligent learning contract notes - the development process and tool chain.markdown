---
layout: post
title: 以太坊智能合约学习笔记：开发流程及工具链使用
date: 发布于2018-09-12 17:25:14 +0800
categories: 以太坊智能合约
tag: 4
---

* content
{:toc}

本文主要介绍开发流程和工具链的使用，安装过程百度上有好多，这里就不赘述了  
<!-- more -->

网上随便找了一个智能合约的例子，咱们来做一个投票系统，先用传统的中心化方案去实现，然后在过度到区块链1.0，最后再用区块链2.0，感受一下开发思想的不同。

  * 业务分析
  * 传统的中心化方案
  * 区块链1.0的方案
  * 区块链2.0的方案
    * Solidity编写智能合约
    * geth建立以太坊测试节点
    * 部署
    * 交互

# 业务分析

我们做的简单点，首先要有一些候选人，然后我们要可以给这些候选人进行投票，投票结束后要统计每位候选人的选票结果。

# 传统的中心化方案

如果用传统的中心化方案去实现，简直不要太简单，以C艹为例，先来定义一下类

    
    
    class Voting 
    {
    public:
        void voteForCandidate(std::string name);
        int totalVotesFor(std::string name);
    private:
        std::vector<std::string> m_vecName;
        std::map<std::string, int> m_mapReceived;
    };
    
    void Voting::Voting(std::vector<std::string> &vecName)
    {
        m_vecName = vecName;
    }
    
    void Voting::voteForCandidate(std::string name)
    {
        m_mapReceived[name] = m_mapReceived[name]+1;
    }
    
    int Voting::totalVotesFor(std::string name)
    {
        return m_mapReceived[name];
    }

然后再搞台服务器，搞个数据库，将投票结果存储到服务器上，客户端可以投票，可以查看结果等等，这个没啥难度，不多废话了。

# 区块链1.0的方案

比特币出现后，所有的区块链应用都是把比特币的源码拿过来，改一改，这个时期也被称为是区块链1.0时代。  
完整的比特币代码很庞大，我们这里弄简单一点，不用比特币，用之前“C++从零开始区块链”系列的代码来做。  
在“C++从零开始区块链”系列中，我们仿照比特币实现了一个简单的电子货币记账系统，其核心的记账数据如下

    
    
    'transactions': [                                     //交易列表，可以有多个交易
    { 
    'sender': "8527147fe1f5426f9dd545de4b27ee00",        //付款方
    'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",     //收款方
    'amount': 5,                                         //金额
    }
    ]

这是一个json数组，每一个元素就代表一支交易，而交易的含义就是地址为8527147fe1f5426f9dd545de4b27ee00的用户要给地址为a77f5cdfa2934df3954a5c7c7da5df1f的用户5个电子币。  
那么怎么用这个结构来做投票系统呢？代码和数据结构都是一样的，关键是对数据的解读。  
同样是上面的那段json，在投票系统中，我们可以将其解读为地址8527147fe1f5426f9dd545de4b27ee00的用户，为地址为a77f5cdfa2934df3954a5c7c7da5df1f的候选人投了5票。投票的时候只要发起这支交易即可，统计结果的时候查询一下候选人的余额就行了。  
业务主体确定了，在初始化系统的时候，我们将候选人列表写如创世块中

    
    
    'transactions': [                                     //交易列表，可以有多个交易
    { 
    'sender': "0",                                       //付款方
    'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",     //收款方
    'amount': 0,                                         //金额
    }
    ]

然后限制每笔交易能转账的电子币只能是1，收款人地址必须存在于创世块的交易列表中，每个地址只能发起一次交易。  
最后，根据上面的分析，将“C++从零开始区块链”系列中的代码简单改一改就可以了。

# 区块链2.0的方案

以太坊是一个区块链的应用框架，用户不需要关心区块链的底层细节，只要在专注于用智能合约编写业务逻辑就可以了，这个时期也被称为是区块链2.0时代。  
以太坊的客户端有很多，我们这里使用geth。智能合约的编程语言也用很多种，我们这里用使用最多的Solidity，使用<http://remix.ethereum.org>来进行编辑和编译。

## Solidity编写智能合约

我们先来写智能合约，关于Solidity的语法百度一下也有好多，这里就不赘述了，直接上代码

    
    
    pragma solidity ^0.4.24;
    
    contract Voting {
    
      mapping (bytes32 => uint8) public votesReceived;
      bytes32[] public candidateList;
    
      constructor (bytes32[] candidateNames) public {
        candidateList = candidateNames;
      }
    
      function totalVotesFor(bytes32 candidate) view public returns (uint8) {
        require(validCandidate(candidate));
        return votesReceived[candidate];
      }
    
      function voteForCandidate(bytes32 candidate) public {
        require(validCandidate(candidate));
        votesReceived[candidate]  += 1;
      }
    
      function validCandidate(bytes32 candidate) view public returns (bool) {
        for(uint i = 0; i < candidateList.length; i++) {
          if (candidateList[i] == candidate) {
            return true;
          }
        }
        return false;
       }
    }

有些面向对象开发基础的人，看了上面的智能合约代码都不会感觉陌生，如果对比上面的C艹，你会发现，和定义一个class也差不多。需要说明的是，在新版本中，智能合约的构造函数为constructor。  
然后打开<http://remix.ethereum.org>，将上面的代码贴进去，在右边点击settings，在Solidity
version中选择一个编译器，由于代码中我们写的是0.4.24，所以也选一个0.4.24版本的编译器。  
然后点击compile，点击start to
compile进行编译，如果不报错，点击details，在弹出的对话框中找到WEB3DEPLOY，将其中的内容考到文本编辑器中备用。

## geth建立以太坊测试节点

合约写好了，接下来要部署到以太网上，要部署在以太网上，就要先建立一个以太网节点，在终端中输入命令

    
    
    geth --datadir testNet --dev console 2>> test.log

–datadir用来指定数据存放目录，–dev是测试网络，console 是进入控制台，具体命令请查阅相关文档。  
执行以上命令后终端进入geth的控制台，在测试网络中，会默认创建一个账户，并分配一些以太币。部署合约需要消耗一定数量的以太币，通过合约往以太坊的网络上写数据也需要消耗一定数量的以太币（严格说其实是gas），但从以太网上查询数据是免费的。由于测试网络给默认创建的账户以太币太多了，不方便我们观察，所以我们要新建一个用户在终端执行命令

    
    
    personal.newAccount("123")

123是密码，创建成功会返回账户地址  
终端执行命令

    
    
    eth.accounts

可以看到有两个用户了  
然后用默认账户给新用户转账

    
    
    eth.sendTransaction({from: '0x290a8ad7b378ea72c705cc55f0f3ecc029ab4854', to: '0xe93b37033d3ddfc0421304bce726dd50040ba2bf', value: web3.toWei(1, "ether")})

from是支付方，to是收款方，value是金额和单位，我们这里是从第一个账户中向第二个账户中转账1个以太币  
终端输入下面的命令，查询余额

    
    
    eth.getBalance(eth.accounts[1])

结果显示账户中有1个以太币。

## 部署

智能合约写好了，测试节点建立好了，测试账户也都准备好了，接下来就是部署了  
找到刚才保存的智能合约的编译结果

    
    
    var candidateNames = /* var of type bytes32[] here */ ;
    var votingContract = web3.eth.contract([{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"totalVotesFor","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"validCandidate","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"votesReceived","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidateList","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"voteForCandidate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"candidateNames","type":"bytes32[]"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]);
    var voting = votingContract.new(
       candidateNames,
       {
         from: web3.eth.accounts[0], 
         data: '0x608060405234801561001057600080fd5b506040516102f23803806102f283398101604052805101805161003a906001906020840190610041565b50506100ab565b82805482825590600052602060002090810192821561007e579160200282015b8281111561007e5782518255602090920191600190910190610061565b5061008a92915061008e565b5090565b6100a891905b8082111561008a5760008155600101610094565b90565b610238806100ba6000396000f30060806040526004361061006c5763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416632f265cf78114610071578063392e66781461009f5780637021939f146100cb578063b13c744b146100e3578063cc9ab2671461010d575b600080fd5b34801561007d57600080fd5b50610089600435610127565b6040805160ff9092168252519081900360200190f35b3480156100ab57600080fd5b506100b7600435610153565b604080519115158252519081900360200190f35b3480156100d757600080fd5b506100896004356101a0565b3480156100ef57600080fd5b506100fb6004356101b5565b60408051918252519081900360200190f35b34801561011957600080fd5b506101256004356101d4565b005b600061013282610153565b151561013d57600080fd5b5060009081526020819052604090205460ff1690565b6000805b60015481101561019557600180548491908390811061017257fe5b600091825260209091200154141561018d576001915061019a565b600101610157565b600091505b50919050565b60006020819052908152604090205460ff1681565b60018054829081106101c357fe5b600091825260209091200154905081565b6101dd81610153565b15156101e857600080fd5b6000908152602081905260409020805460ff8082166001011660ff199091161790555600a165627a7a72305820943f89b031a215cff20e4d7fdadf277223e47612eac75ad93885f5c01a3930240029', 
         gas: '4700000'
       }, function (e, contract){
        console.log(e, contract);
        if (typeof contract.address !== 'undefined') {
             console.log('Contract mined! address: ' + contract.address + ' transactionHash: ' + contract.transactionHash);
        }
     })

我们要关心的只有两个地方，第一行定义了一个变量，该变量在部署的时候作为参数传递给构造函数，我们要自己给变量赋值。  
第五行的“from: web3.eth.accounts[0]”是要指定使用哪个账户进行部署，我们使用新创建的账户进行部署，所以要改成“from:
web3.eth.accounts[1]”  
修改后的结果如下

    
    
    var candidateNames = ['Rama','Nick','Jose']/* var of type bytes32[] here */ ;
    var votingContract = web3.eth.contract([{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"totalVotesFor","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"validCandidate","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"votesReceived","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidateList","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"voteForCandidate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"candidateNames","type":"bytes32[]"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]);
    var voting = votingContract.new(
       candidateNames,
       {
         from: web3.eth.accounts[1], 
         data: '0x608060405234801561001057600080fd5b506040516102f23803806102f283398101604052805101805161003a906001906020840190610041565b50506100ab565b82805482825590600052602060002090810192821561007e579160200282015b8281111561007e5782518255602090920191600190910190610061565b5061008a92915061008e565b5090565b6100a891905b8082111561008a5760008155600101610094565b90565b610238806100ba6000396000f30060806040526004361061006c5763ffffffff7c01000000000000000000000000000000000000000000000000000000006000350416632f265cf78114610071578063392e66781461009f5780637021939f146100cb578063b13c744b146100e3578063cc9ab2671461010d575b600080fd5b34801561007d57600080fd5b50610089600435610127565b6040805160ff9092168252519081900360200190f35b3480156100ab57600080fd5b506100b7600435610153565b604080519115158252519081900360200190f35b3480156100d757600080fd5b506100896004356101a0565b3480156100ef57600080fd5b506100fb6004356101b5565b60408051918252519081900360200190f35b34801561011957600080fd5b506101256004356101d4565b005b600061013282610153565b151561013d57600080fd5b5060009081526020819052604090205460ff1690565b6000805b60015481101561019557600180548491908390811061017257fe5b600091825260209091200154141561018d576001915061019a565b600101610157565b600091505b50919050565b60006020819052908152604090205460ff1681565b60018054829081106101c357fe5b600091825260209091200154905081565b6101dd81610153565b15156101e857600080fd5b6000908152602081905260409020805460ff8082166001011660ff199091161790555600a165627a7a72305820943f89b031a215cff20e4d7fdadf277223e47612eac75ad93885f5c01a3930240029', 
         gas: '4700000'
       }, function (e, contract){
        console.log(e, contract);
        if (typeof contract.address !== 'undefined') {
             console.log('Contract mined! address: ' + contract.address + ' transactionHash: ' + contract.transactionHash);
        }
     })

结果返回错误

    
    
    Error: authentication needed: password or unlock undefined

这个错误是因为账户被锁定了，所以我们要先给账户进行解锁

    
    
    personal.unlockAccount(eth.accounts[1],"123");

然后在执行部署命令，返回

    
    
    Contract mined! address: 0x9abbc0dc0d688b280e612cb4d1e73a35f61b2895 transactionHash: 0x0d13541db32353e2aba900dc03b2c1de1acd3c1bab267aea9b695043b9958b43

说明部署成功。  
我们来查询一下账户1的余额，发现余额减少了，说明部署是需要消耗以太币的。

## 交互

合约部署完毕，接下来就是进行交互了。  
在部署的时候，我们输入终端的的代码辣么长，但其实只有三句话，每句话定义了一个变量，最后一个变量voting就的定义的合约实例化的对象，可以通过这个变量执行合约中的函数  
在合约构造的收，我们传入了三个人名“[‘Rama’,’Nick’,’Jose’]”，现在我们来查看一下rama的选票数

    
    
    voting.totalVotesFor('Rama')

返回的结果是0，因为还没人给rama投票，我们使用账户1给rama投一票

    
    
    voting.voteForCandidate('Rama', {from: web3.eth.accounts[1]})

然后再看一下rama的选票数，发现rama已经有了一票了  
在看一下账户1的余额

    
    
    eth.getBalance(eth.accounts[1])

发现余额有少了几个wei，投票需要向网络上写数据，所以要消耗以太币，而查询不用写数据，就不用消耗以太币了。

