---
layout: post
title: 观察者模式
date: 发布于2019-08-01 17:57:49 +0800
categories: 设计模式
tag: 4
---

* content
{:toc}

观察者模式适用于在一个一对多模型中，一者状态变化，多者需要根据变化做出相应调整的情况，下面我们通过一个简单的例子简单说明观察者模式的设计方法  
<!-- more -->

注：本利旨在说明观察者模式的设计思想，例子中存在一定的内存泄露没有处理

假设我们有一台电脑主机，这台电脑主机不干别的事，只是向屏幕发送一个数字。  
同时有多台显示器连接到这台主机上，并根据发送来的数字做自己的逻辑处理再显示出来  
首先我们做一个只有一个显示器的情况

    
    
    class Display
    {
    public:
    	void update(int num)
    	{
    		m_num = num;
    		show();
    	}
    
    	void show()
    	{
    		std::cout << m_num << std::endl;
    	}
    private:
    	int m_num;
    };
    
    class Computer
    {
    public:
    	void setNum(int num)
    	{
    		m_num = num;
    		numChange();
    	}
    	int getNum()
    	{
    		return m_num;
    	}
    	
    	void numChange()
    	{
    		m_display->update(m_num);
    	}
    
    	void setDisplay(Display *display)
    	{
    		m_display = display;
    	}
    
    private:
    	int m_num;
    	Display *m_display;
    };
    
    int main(int argc, char **argv)
    {
    	Display *display = new Display;
    
    	Computer *computer = new Computer;
    	computer->setDisplay(display);
    
    	computer->setNum(10);
    
    	computer->setNum(100);
    
    	return 0;
    }
    

在上面代码中，我们首先定义了一个显示器和一个主机，并为主机绑定了显示器。当主机的数字变化时，会自动调用显示器的更新方法，将新的数字显示出来。

现在，我们将情景变的复杂一些，如果我们需要有两台显示器，一台显示器用来显示主机发送的原始数据，另一台需要将主机发送的数据加1后再显示出来。  
可见，在上面的代码中，想实现这个功能非常麻烦，不但要添加一个显示器类的定义，还要修改主机类的定义，而且每次需要添加或删除显示器，都要修改主机类。而观察者模式就是解决类似情况的，我们只需要添加一个显示器类就可以了，而不需要修改主机类，下面是代码

    
    
    class Observer
    {
    public:
    	virtual void update(int num)
    	{
    		m_num = num;
    		show();
    	}
    	virtual void show() = 0;
    
    protected:
    	int m_num;
    };
    
    class Subject
    {
    public:
    	virtual void registerObserver(Observer *observer) = 0;
    	virtual void removeObserver(Observer *observer) = 0;
    	virtual void notifyObserver() = 0;
    };
    
    class Display1 : public Observer
    {
    public:
    	void show() override
    	{
    		std::cout << m_num << std::endl;
    	}
    };
    
    class Display2 : public Observer
    {
    public:
    	void show() override
    	{
    		std::cout << m_num + 1 << std::endl;
    	}
    };
    
    class Computer : public Subject
    {
    public:
    	void setNum(int num)
    	{
    		m_num = num;
    		numChange();
    	}
    	int getNum()
    	{
    		return m_num;
    	}
    	
    	void numChange()
    	{
    		notifyObserver();
    	}
    
    	void registerObserver(Observer *observer) override {
    		m_observerList.push_back(observer);
    	}
    
    	void removeObserver(Observer *observer) override {
    		for (std::vector<Observer*>::iterator iter = m_observerList.begin(); iter != m_observerList.end();)
    		{
    			if (*iter == observer)
    				iter = m_observerList.erase(iter);
    			else
    				iter++;
    		}
    	}
    
    	void notifyObserver() override {
    		for (int i = 0; i < m_observerList.size(); i++) {
    			m_observerList.at(i)->update(m_num);
    		}
    	}
    
    private:
    	int m_num;
    	std::vector<Observer*> m_observerList;
    };
    
    int main(int argc, char **argv)
    {
    	Display1 *display1 = new Display1();
    	Display2 *display2 = new Display2();
    
    	Computer *computer = new Computer();
    
    
    	computer->registerObserver(display1);
    	computer->registerObserver(display2);
    	computer->setNum(10);
    	std::cout << "========================================\n";
    	computer->removeObserver(display1);
    	computer->setNum(100);
    
    	return 0;
    }
    

这里，我们添加了两个虚基类  
Subject：就是“被观察”的角色，它将所有观察者对象的引用保存在一个集合中。  
Observer：是抽象的“观察”角色，它定义了一个更新接口，使得在被观察者状态发生改变时通知自己。  
在本例中，我们创建了一个被观察者主机，和两个观察者显示器1和2，对象创建完成后，将显示器1和2添加到被观察者主机的观察者集合中  
每当被观察者的数据变化时，就向观察者集合中的所有观察者发送数据变化事件，观察者接收到被观察者发送的变化事件并接收到变化后的数据后，根据自己的逻辑进行显示，本例中1是原样显示，2是加1后显示  
被观察者还可以将某个观察者从自己的观察者集合中删除，这样数据变化时就不会向已删除的观察者发送变化事件了。

