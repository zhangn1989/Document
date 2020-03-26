---
layout: post
title: C语言使用表驱动法重构if-else分支太多的情况
date: 发布于2018-11-16 18:11:54 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}

今天工作中遇到这么一个情况：将25种字符串分成17类，然后统计每一类中的数量  
<!-- more -->

第一版代码简单粗暴，直接上if-else，代码如下

    
    
    if (strcasestr(str, "a")
    {
    	type = 0;
    }
    else if (strcasestr(str, "b")
    {
    	type = 1;
    }
    else if (strcasestr(str, "c")
    {
    	type = 2;
    }
    

类似于这种，当我写到第5个分支的时候就写不下去了，何况是25个，果断放弃。  
那用什么方法代替if-else呢？以前写C艹倒是有种设计模式可以解决这个问题，可在纯C里玩这么玩，代码只会更加难以维护。  
那么有没有适用于纯C的解决方案呢？请教了一下百度大神，原来还有表驱动法可以很优雅的解决if-else分支太多的问题。  
表驱动法简单说就是将要判断的数据存到一个数组里，然后从这个数组里查询满足条件的数据。最简单的办法就是将数据和数组的索引进行绑定，但局限性比较大，我遇到的情况不适用。既然不能和索引进行绑定，那就只能自己做数据映射，然后用循环替换掉判断，遍历数组，依次判断元素是否满足条件，首先定义全局绑定数据结构和全局的只读数组

    
    
    typedef struct st_type_ {
    	int type;
    	char *str;
    }st_type;
    
    static const st_type gTabtype[] = {
    	{1, "a"},	{2, "b"},	{2, "c"},	{3, "d"}, ...., {0, NULL}
    };
    

然后是在函数中使用

    
    
    int index = 0;
    int type = -1;
    while (gTabtype[index].str)
    {
    	if (strcasestr(str, gTabtype[index].str))
    	{
    		type = gTabtype[index].type;
    		break;
    	}
    	++index;
    }
    
    if (type < 0)
    	return 0;
    

这样的代码看起来就整洁多了，也更好维护。

