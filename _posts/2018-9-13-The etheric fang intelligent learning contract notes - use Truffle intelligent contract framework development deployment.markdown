---
layout: post
title: 以太坊智能合约学习笔记：使用Truffle框架开发部署智能合约
date: 发布于2018-09-13 15:31:22 +0800
categories: 以太坊智能合约
tag: 4
---

* content
{:toc}

truffle是一个智能合约的开发框架，具体的就不介绍了，我们主要是说说怎么使用这个框架来进行智能合约的开发，官网[戳这里](https://truffleframework.com)。

<!-- more -->

### 文章目录

  * 安装
  * 创建项目
  * 编译合约
  * 部署
    * 部署到geth
    * 部署到truffle的内建测试网络
    * 部署到Ganache
  * 交互
    * geth控制台合约交互
    * truffle的内建测试网络交互
    * Ganache测试网络交互

# 安装

首先我们要先安装npm和truffle，安装命令如下

    
    
     sudo apt install npm
     sudo npm install -g truffle
    

# 创建项目

首先创建一个空目录，然后进去，终端执行

    
    
    truffle init
    

该命令一定要在空目录下执行，否则会出错  
命令执行完毕后会下载一些初始文件，这些文件不用动，目录结构如下  
![初始化后的目录结构](/styles/images/blog/The etheric fang intelligent learning contract notes - use Truffle intelligent contract framework development deployment_1.png)

# 编译合约

在contracts目录下创建Voting.sol，将上一篇[以太坊智能合约学习笔记：开发流程及工具链使用](https://blog.csdn.net/mumufan05/article/details/82665101)中我们用到的合约的内容写进去  
然后在migrations目录下创建2_deploy_contracts.js，写入如下内容

    
    
    var Voting = artifacts.require("./Voting.sol");
      
    module.exports = function(deployer) {
              deployer.deploy(Voting,["Rama","Nick","Jose"]);
    };
    

其中[“Rama”,“Nick”,“Jose”]是合约的构造参数  
然后编辑truffle.js，将其中的内容修改如下

    
    
    module.exports = {
            networks: {
                    development: {
                            host: "127.0.0.1",
                            port: 8545,
                            network_id: "*", // Match any network id
                            gas:500000
                    }
            }
    };
    

最后，执行“truffle test”命令进行测试，测试没问题了执行“truffle compile”命令进行编译。

# 部署

## 部署到geth

另启一个终端，换个其他目录，执行下面的命令

    
    
    geth --datadir testNet --dev --rpc console 2>>test.log
    

和上一篇不用truffle的命令相比，多了一个–rpc参数  
启动geth监听后，回到truffle项目目录，执行“truffle migrate”命令进行部署，如果成功，将输出如下内容

    
    
    Using network 'development'.
    
    Running migration: 1_initial_migration.js
      Deploying Migrations...
      ... 0x39ffa2af2418c0c4ccc2cd2ad4514cd529f6bc9cba055e409e76538eada2da98
      Migrations: 0xec910e955228312bf018f845fe402444881b6723
    Saving successful migration to network...
      ... 0x80f21dbda606d0fbd2a7c9ff3e45bb6356ef8ac04fb6aec052018edf57495ac9
    Saving artifacts...
    Running migration: 2_deploy_contracts.js
      Deploying Voting...
      ... 0x2143e82ca657417e388a30ed0db4fb5b36928ea979da7f366537f6de374820d1
      Voting: 0xa2ac81866309c37b5e8d54e275df07fa7bdd74b5
    Saving successful migration to network...
      ... 0x855c0c19ee0a8baf0dfb42a88203d5307bb1b3ed772f901ed843c20999964d64
    Saving artifacts...
    

记住 Voting: 0xa2ac81866309c37b5e8d54e275df07fa7bdd74b5这个地址，后面我们还会用到。  
接下来打开build/contracts/Voting.json，找到abi字段的内容，将内容压缩成一行，内容如下

    
    
    [{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"votesReceived","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidateList","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"candidateNames","type":"bytes32[]"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"totalVotesFor","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"voteForCandidate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"validCandidate","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"}]
    

然后回到geth控制台，定义变量abi，并将上面的json值赋值给变量abi，即在geth的控制台中输入如下内容

    
    
    abi = [{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"votesReceived","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidateList","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"candidateNames","type":"bytes32[]"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"totalVotesFor","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"voteForCandidate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"validCandidate","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"}]
    

合约的abi定义完成，接下来是使用部署时返回的合约地址去实例化合约，geth的控制台中输入如下内容

    
    
    voting = eth.contract(abi).at('0xa2ac81866309c37b5e8d54e275df07fa7bdd74b5')
    

至此，geth合约部署完成。

## 部署到truffle的内建测试网络

自带了一个测试网络，不与以太网络相连，只是一个单机的测试网络。  
将工作目录切换到truffle工程目录，在终端输入truffle develop进入测试控制台  
测试网络会初始化10个账户用于测试，然后在测试控制台输入“migrate”进行部署  
部署的完成后的返回结果和上面的geth返回的结果完全相同，同样包含一个合约地址

## 部署到Ganache

Ganache也是一个用于测试的工具，分为命令行和图形界面两种  
图形界面的下载[戳这里](https://truffleframework.com/ganache)  
命令行下载用这条命令

    
    
    sudo npm install -g ganache-cli
    

由于我是使用ssh在远程机器上做测试，图形界面用着不方便，我们这里使用命令行  
新开个终端，在终端中输入“ganache-cli”，同样会创建10个测试账户  
看输出信息的最后一行显示的IP和端口

    
    
    Listening on 127.0.0.1:8545
    

修改truffle.js的内容如下

    
    
    module.exports = {
    	networks: {
    	    development: {
    	        host: "127.0.0.1",
    	        port: 8545,
    	        network_id: "*"
    	    }
    	}
    };
    

host和port改成上面输出的IP和端口  
然后回到truffle工程目录的控制台，终端输入truffle migrate进行部署，同样要记住返回的合约地址，部署完成。

# 交互

## geth控制台合约交互

交互和前面一篇没有使用truffle的交互一样，可以查看前一篇[以太坊智能合约学习笔记：开发流程及工具链使用](https://blog.csdn.net/mumufan05/article/details/82665101)的内容。

## truffle的内建测试网络交互

部署完成后，返回一个合约地址，我们就可以用这个合约地址进行交互了，比如要查询Rama的票数可以这样写

    
    
    Voting.at("0x345ca3e014aaf5dca488057592ee47305d9b3e10").totalVotesFor("Rama")
    

然后返回如下结果

    
    
    BigNumber { s: 1, e: 0, c: [ 0 ] }
    

其中c的值就是查询的值了  
但是这样使用合约有点麻烦，所以我们用一个变量保存合约实例

    
    
    voting = Voting.at("0x345ca3e014aaf5dca488057592ee47305d9b3e10")
    

以后就可以直接用变量voting来调用合约的方法了，例如

    
    
    voting.voteForCandidate('Rama', {from: web3.eth.accounts[0]})
    voting.totalVotesFor('Rama')
    

还可以使用下面的方法查询余额

    
    
    web3.eth.getBalance(web3.eth.accounts[0])
    

其他就和geth的用法差不多了

## Ganache测试网络交互

输入命令“truffle console”进入truffle控制台  
输入“voting =
[Voting.at](http://Voting.at)(“0x27f77eeae7d192c300d5776acb782cc971fc8423”)”，那个大长串的十六进制就是合约的地址  
然后就和在truffle的内建测试网络交互一样了。

