---
layout: post
title: 小型内存池
date: 发布于2020-04-12 13:00:00 +0800
categories: C++内存管理
tags: c++ new 内存 内存池 内存管理
---

* content    
我们都知道，不管是用new还是用malloc，每次系统分配内存的时候都要占用系统资源的。而且每次我们向操作系统分配内存的时候，得到的都是包含cookie的内存块，其实际大小要大于我们所申请的内存大小。    
对于频繁申请内存的情况，我们可以一次向系统申请一大块内存，然后自己管理，这样既能节省系统调用的时间，能节省多个cookie所占用的空间。    
<!-- more -->

# pre-class allocator

## 第一版最简单的实现

``` c++

#include <cstddef>
#include <iostream>
using namespace std;

class Scree
{
public:
    Screen(int x) : i(x) { };
    int get() { return i; }

    void *operator new(size_t);
    void operator delete(void *);

private:
    Screen *next;
    static Screen *freeStore;
    static const int screenChunk;

private:
    int i;
};

Screen *Screen::freeStore = 0;
const int Screen::screenChunk = 24;

void *Screen::operator new(size_t size)
{
    Screen *p;
    if(!freeStore)
    {
        size_t chunk = screenChunk * size;
        freeStore = p = reinterpret_cast<Screen *>(new char[chunk]);
        
        // 分割内存，转成链表形式使用
        for (; p != &freeStore[screenChunk - 1]; ++p)
            p->next = p + 1;
        p->next = 0;
    }

    p = freeStore;
    freeStore = freeStore->next;
    return p;
}

void Screen::operator delete(void *p)
{
    // freeStore指向下一块未使用的内存
    // 这里将自身设置为下一块未使用，就是删除了
    // 这个实现方式还有很多问题，看看就行，关键是领会思想
    (static_cast<Screen *>(p))->next = freeStore;
    freeStore = static_cast<Screen *>(p);
}

```

## 第二个版本

```c++

class Airplane
{
private:
    struct AirplanceRep
    {
        unsigned long miles;
        char type;
    };

private:
// 这个联合体的用法叫嵌入式指针
// 感觉这个方法针对性太强，通用性很差，看看就行了
    union
    {
        AirplaneRep rep;
        Airplane *next;
    };

public:
    unsigned long getMiles() { return rep.miles; }
    char getType() { return rep.type; }
    void set(unsigned long m, char t)
    {
        rep.miles = m;
        rep.type = t;
    }

public:
    static void *operator new(size_t size);
    static void operator delete(void *deadObject);

private:
    static const int BLOCK_SIZE;
    static Airplane *headOfFreeList;
};

Airplance *Airplane::headOfFreeList;
const int Airplane::BLOCK_SIZE = 512;

void *Airplane::operator new(size_t size)
{
    // 如果是继承的子类，此处可能会有问题，所以需要判断一下
    if(size != sizeof(Airplance))
        return ::operator new(size);

    Airplane *p = headOfFreeList;
    if (p) 
    {
        headOfFreeList = p->next;
    }
    else
    {
        Airplane *newBlock = static_cast<Airplane *>
        (::operator new(BLOCK_SIZE * sizeof(Airplane)));

        // 跳过0，不知道为什么，应该是用第0号元素干些别的事
        for(int i = 1; i < BLOCK_SIZE - 1; ++i)
            newBlock[i].next = &newBlock[i + 1];
        
        newBlock[BLOCK_SIZE - 1].next = 0;
        p = newBlokc;
        headOfFreeList = &newBlock[1];
    }

    return p;
}

void Airplane::operator delete(void *deadObject)
{
    if(deadObject == 0) return;
    if(size != sizeof(Airplane))
    {
        ::operator delete(deadObject);
        return;
    }

    Airplane *carcass = static_cast<Airplane *>(deadObject);
    carcass->next = headOfFreeList;
    headOfFreeList = carcass;
}

```

与第一版最大的区别是用union中使用了嵌套指针。
