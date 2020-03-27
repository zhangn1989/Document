---
layout: post
title: 简单模拟Qt的子类内存释放
date: 发布于2019-08-01 13:41:08 +0800
categories: Qt
tag: 4
---

用过Qt的朋友都知道，继承自QObject的子类，只要delete父对象可以自动delete父对象的所有子对象，今天我们来用几行代码模拟一下

<!-- more -->

    
    
    #include <QList>
    class A
    {
    public:
    	A(A *parent = nullptr)
    	{
    		if (parent)
    			parent->addChild(this);
    	}
    
    	virtual ~A()
    	{
    		QList<A *>::iterator it;
    		for (it = m_lstChild.begin(); it != m_lstChild.end(); ++it)
    		{
    			delete *it;
    		}
    	}
    
    protected:
    	void addChild(A *chlid)
    	{
    		m_lstChild.push_back(chlid);
    	}
    
    private:
    	QList<A *> m_lstChild;
    };
    
    class B : public A
    {
    public:
    	B(int i,A *parent = nullptr):A(parent)
    	{
    		p = new int;
    		*p = i;
    	}
    
    	virtual ~B()
    	{
    		delete p;
    	}
    
    private:
    	int *p;
    };
    
    int main(int argc, char *argv[])
    {
    	B *ch1 = new B(1);
    	B *ch2 = new B(2, ch1);
    
    	delete ch1;
    	
    	return a.exec();
    }
    

简单解释一下上面的代码  
QList这个头文件不重要，这里主要是个链表，可以用Qt的，也可以用stl的，也可以用自己写的  
代码的主要思想是在A类中记录一个子对象的指针链表，当父对象delete的时候，遍历自己的子对象指针链表，依次delete掉自己的所有子对象  
在main函数中，首先new一个父对象ch1，然后new一个子对象ch2，设置其父对象为ch1  
当delete ch1时，首先掉用ch1的B类的析构函数，释放指针p，然后调用ch1的父类A的析构函数，在A的析构函数中遍历自己的子对象指针链表。  
此例中只有一个子对象ch2，遍历到ch2的指针时，delete掉ch2的指针，在该过程中，首先调用ch2的B类虚构函数释放掉ch2的B类p指针，然后调用ch2的A类的析构函数，发现ch2没有子对象，释放掉ch2的A类后delete掉ch2指针这一过程结束，然后继续释放ch1的A类内存，知道ch1释放完成  
这样就可以只通过释放ch1的内存去释放ch2的内存。

* content
{:toc}


