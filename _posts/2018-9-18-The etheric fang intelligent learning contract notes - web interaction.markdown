---
layout: post
title: 以太坊智能合约学习笔记：网页交互
date: 发布于2018-09-18 17:08:09 +0800
categories: 以太坊智能合约
tag: 4
---

没搞过web程序，花了几天研究一下，总算是搞懂了网页与以太坊节点的交互流程。  

<!-- more -->
网页与智能合约交互，需要使用web3.js，它实现了通用JSON PRC规范，通过JSON
RPC协议与以太坊节点进行交互。除了js以外，以太坊还提供了Java、Python等语言的API，对于没有提供API的语言，只能自己直接使用JSON
RPC来与以太坊进行交互了，关于以太坊的JSON
RPC协议，请[戳这里](https://github.com/ethereum/wiki/wiki/JSON-RPC)。  
我们还是以之前的投票合约为例，来介绍一下网页交互。

首先，我们需要建立一个以太坊节点

    
    
    geth --datadir testNet --dev --rpc  --rpcaddr 0.0.0.0 --rpccorsdomain "*" console --dev.period 1 2>>test.log
    

和之前的命令相比，多了几项

  * –rpcaddr 0.0.0.0 该选项是指定监听IP
  * –rpccorsdomain “*” 这是浏览器强制要求选项，用来指定可以访问的IP和端口，“*”代表无访问限制
  * –dev.period 1 自动挖矿间隔，这里是间隔一秒

然后回到合约工程目录进行编译和部署

    
    
    truffle compile && truffle deplo
    

接下来我们要准备一个html，简单一点，两个文本框用来输入人名和显示结果，两个按钮用来投票和查询，布局就不加了。

    
    
    <!DOCTYPE html>
    <html>
    	<head>
    		<title>MetaCoin - Truffle Webpack Demo w/ Frontend</title>
    		<link rel="shortcut icon" href="#" />
    		<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/ethereum/web3.js/dist/web3.min.js"></script>
    	</head>
    	<body>
    		<br><label for="candidate">Candidate:</label><input type="text" id="candidate" placeholder="Rama"></input>
    		<br><label for="votes">Votes:</label><input type="text" id="votes"></input>
    		<input type="button" value="query" onclick="totalVotesFor()"></input>
    		<input type="button" value="votes" onclick="voteForCandidate()"></input>
    		
    		<script type="text/javascript">
    		  	if (typeof web3 !== 'undefined') {
    			 web3 = new Web3(web3.currentProvider);
    			} else {
    			 // set the provider you want from Web3.providers
    			 web3 = new Web3(new Web3.providers.HttpProvider("http://192.168.180.130:8545"));
    			}
    
    		    web3.eth.defaultAccount = web3.eth.accounts[0];
    		    var abi = [{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"totalVotesFor","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"validCandidate","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"votesReceived","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidateList","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"candidate","type":"bytes32"}],"name":"voteForCandidate","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"candidateNames","type":"bytes32[]"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"}];
    		    var votingContract = web3.eth.contract(abi);
    		    var voting = votingContract.at('0x4121629c08fd86b7133761baa2e047ec23a17661');
    		    function totalVotesFor() {
    		    //	document.getElementById("votes").value = "abc";
    		    	document.getElementById("votes").value = voting.totalVotesFor(document.getElementById("candidate").value);
    		    }
    		    function voteForCandidate() {
    		    	voting.voteForCandidate(document.getElementById("candidate").value);
    		    }
    		</script>
    	</body>
    </html>
    

HttpProvider的IP不能是127.0.0.1，这里被坑惨了。  
变量abi的值是合约编译的结果，变量voting后面的大长串十六进制数是合约的地址，这里可以看[之前的文章](https://blog.csdn.net/mumufan05/article/details/82688939)。  
然后搭建个简易的web服务器，我们这里用Python

    
    
    python -m SimpleHTTPServer
    

最后用浏览器访问“[http://192.168.180.130:8000/”看结果。](http://192.168.180.130:8000/%E2%80%9D%E7%9C%8B%E7%BB%93%E6%9E%9C%E3%80%82)  
![](/styles/images/blog/The etheric fang intelligent learning contract notes - web interaction_1.png)  
在Candidate中输入人名，点击votes进行投票，点击query查询结果，结果显示在Votes中。

* content
{:toc}


