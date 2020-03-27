---
layout: post
title: 简单实现Qt的信号槽
date: 发布于2019-08-05 17:05:48 +0800
categories: Qt
tag: 4
---

* content
{:toc}


    #include <stdio.h>

<!-- more -->
    #include <string.h>
    #include <vector>
    #include <map>
    #include <iostream>
    
    # define slots
    # define signals
    # define emit
    
    class Object;
    
    // 首先，我们定义一个元对象，用来存放对象的所有信号和槽的关键字
    // active是供信号函数调用的静态函数，用来查找并调用对应的槽函数
    struct MetaObject 
    {
    	std::vector<const char *>signal_name;
    	std::vector<const char *>slot_name;
    	static void active(Object * sender, int index);
    };
    
    // 然后，我们定义一个绑定结构，用来将槽的对象和其槽函数进行关联
    struct Connection
    {
    	Object * receiver;
    	int method;
    };
    
    typedef std::multimap<int, Connection> ConnectionMap;
    typedef std::multimap<int, Connection>::iterator ConnectionMapIt;
    
    
    // 接下来我们就可以声明object类了
    class Object 
    {
    	friend class MetaObject;
    public:
    	// 首先，我们先声明一个元对象
    	MetaObject meta;
    
    	// 然后，就是关键的绑定函数
    	// 在绑定函数中主要做两件事
    	// 1，查找对象的信号和槽的索引
    	// 2，将索引进行绑定
    	// 因此，我们还需要一个查找索引的辅助函数和一个用来存放绑定关系的map
    	static void connect(Object*, const char*, Object*, const char*);
    	static int find_index(std::vector<const char *> &vec, const char * str);
    	// 辅助函数，根据索引调用槽函数，在qt中，该函数由moc自动生成
    	void metacall(int idx);  
    private:
    	ConnectionMap connections;
    
    
    // 信号和槽的函数可以声明在object中，也可以声明在子类中，为了测试方便，就不用子类了
    // 信号和槽函数没什么特别的，就是普通的成员函数
    // 关键字signals和slots并不是必要的，这个仅仅是为了让别人知道，这是信号和槽函数
    // 或者是给一些自动化工具看的，比如qt的moc
    public signals :
    	void signal1();
    	void signal2();
    
    public slots:
    	void slot1();
    	void slot2();
    
    };
    
    // 实现active函数
    // 在信号对象中，找到相应编号的信号和其绑定的所有槽函数
    void MetaObject::active(Object* sender, int idx)
    {
    	ConnectionMapIt it;
    	std::pair<ConnectionMapIt, ConnectionMapIt> ret;
    	ret = sender->connections.equal_range(idx);
    	for (it = ret.first; it != ret.second; ++it)
    	{
    		Connection c = (*it).second;
    		c.receiver->metacall(c.method);
    	}
    }
    
    // 查找信号和槽的索引编号
    int Object::find_index(std::vector<const char *> &vec, const char * str)
    {
    	int i;
    	for (i = 0; i < vec.size(); ++i)
    	{
    		if (!strcmp(str, vec[i]))
    			return i;
    	}
    	return -1;
    }
    
    void Object::connect(Object* sender, const char* signal, Object* receiver, const char* slot)
    {
    	// 找到发送者的信号索引和接受者的槽索引
    	int signal_index = Object::find_index(sender->meta.signal_name, signal);
    	int slot_index = Object::find_index(receiver->meta.slot_name, slot);
    	if (signal_index == -1 || slot_index == -1) {
    		perror("signal or slot not found!");
    	}
    	else {
    		// Connection用来存放接受者对象和其槽函数的索引
    		// 同一个对象的不同槽函数写成多个Connection
    		// 每个Connection对应一次信号调用
    		Connection c = { receiver, slot_index };  
    		// 将接受者的Connection绑定到发送者的信号索引上
    		sender->connections.insert(std::pair<int, Connection>(signal_index, c));
    	}
    }
    
    void Object::slot1()
    {
    	printf("this is slot1!\n");
    }
    
    void Object::slot2()
    {
    	printf("this is slot2!\n");
    }
    
    void Object::metacall(int index)
    {
    	switch (index) {
    	case 0:
    		slot1();
    		break;
    	case 1:
    		slot2();
    		break;
    	default:
    		break;
    	};
    }
    
    // 信号函数实现，active的第二个参数就是信号索引
    // 信号函数实现的过程也是将信号函数索引绑定的过程
    // 在qt中，这已过成有moc完成，并写在moc_xxx.cpp中
    void Object::signal1()
    {
    	MetaObject::active(this, 0);
    }
    
    void Object::signal2()
    {
    	MetaObject::active(this, 1);
    }
    
    using namespace std;
    
    int main()
    {
    	Object obj1, obj2;
    
    	// 将信号索引与字符串绑定
    	// 借助vector的特性简单实现
    	// vector的索引就是信号函数的索引
    	// 当然，qt中比这要复杂，并且此过程有moc在moc_xxx.cpp中实现
    	obj1.meta.signal_name.push_back("signal1");
    	obj1.meta.signal_name.push_back("signal2");
    	obj2.meta.slot_name.push_back("slot1");
    	obj2.meta.slot_name.push_back("slot2");
    
    	// 绑定信号槽，发射信号，这个就和在qt中常用的方法一样了
    	Object::connect(&obj1, "signal1", &obj2, "slot1");
    	Object::connect(&obj1, "signal2", &obj2, "slot2");
    	// emit也是给人看的，即使在qt中，没有emit直接调信号函数也是可以的
    	emit obj1.signal1();
    	emit obj1.signal2();
    	return 0;
    }
    

