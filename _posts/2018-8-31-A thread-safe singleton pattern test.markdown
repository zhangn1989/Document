---
layout: post
title: 一个线程安全的单例模式测试
date: 发布于2018-08-31 15:14:56 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}

单例模式，一般我喜欢这样实现
<!-- more -->


    
    
    class SingleTest
    {
    public:
        static SingleTest *Instance();
    
    protected:
        SingleTest();
        ~SingleTest();
    
    private:
        int m;
    };
    
    SingleTest *SingleTest::Instance()
    {
        static SingleTest st;
        return &st;
    }
    
    SingleTest::SingleTest()
    {
        m = 0;
        printf("SingleTest Create\n");
    }
    
    SingleTest::~SingleTest()
    {
        printf("SingleTest Destroy\n");
    }

然后这样用

    
    
    SingleTest *ts = SingleTest::Instance();

这么实现的一个好处就是比较简单，而且不会有内存泄露。但如果在多线程环境下是否安全呢？多线程环境下可能会有两种情况：  
第一，如果两个线程同时调用SingleTest *ts =
SingleTest::Instance();，如果线程一先执行构造，但还没构造完，线程二构造的时候发现还没有构造实例，会再次执行构造，单例就变成了两例。  
第二，如果两个线程都要对成员变量进行读写，那么会不会发生竞争呢？  
理论分析一下：  
第一种情况，C++11标准的编译器是线程安全的，C++11标准要求编译器保证static的线程安全。而C++11之前标准的编译器则是不确定，关键看编译器的实现。  
第二种情况，任何标准下都不是线程安全的。  
第一种情况，因为有标准的硬性规定，倒是不需要测试了。那么第二种情况什么样？写个代码测试一下

    
    
    #include <stdio.h>
    
    #include <pthread.h>
    #include <unistd.h>
    
    class SingleTest
    {
    public:
        static SingleTest *Instance();
        void test();
        int get();
    
    protected:
        SingleTest();
        ~SingleTest();
    
    private:
        int m;
    };
    
    SingleTest *SingleTest::Instance()
    {
        static SingleTest st;
        return &st;
    }
    
    void SingleTest::test()
    {
        int i, loc;
        for (i = 0; i < 5000; ++i)
        {
            loc = m;
            ++loc;
            m = loc;
        }
    }
    
    int SingleTest::get()
    {
        return m;
    }
    
    SingleTest::SingleTest()
    {
        m = 0;
        printf("SingleTest Create\n");
    }
    
    SingleTest::~SingleTest()
    {
        printf("SingleTest Destroy\n");
    }
    
    void *threadFunc(void *arg)
    {
        SingleTest *ts = SingleTest::Instance();
        ts->test();
    
        return NULL;
    }
    
    int main(int argc, char* argv[])
    {
        int s;
        pthread_t tid1;
        pthread_t tid2;
    
        s = pthread_create(&tid1, NULL, threadFunc, NULL);
        if (s != 0)
            printf("thread 1 create error:%d\n", s);
    
        s = pthread_create(&tid2, NULL, threadFunc, NULL);
        if (s != 0)
            printf("thread 2 create error:%d\n", s);
    
        s = pthread_join(tid1, NULL);
        if (s != 0)
            printf("thread 1 join error:%d\n", s);
    
        s = pthread_join(tid2, NULL);
        if (s != 0)
            printf("thread 2 join error:%d\n", s);
    
        SingleTest *ts = SingleTest::Instance();
        printf("%d\n", ts->get());
        return 0;
    }

SingleTest::test()函数执行了5000次累加，两个线程同时调用该函数，如果是线程安全的，最后的结果应该是10000，如果线程是不安全的，最后的结果应该不确定。  
经过测试，最后的结果也确实是不确定的，说明的确是线程不安全。  
既然线程不安全，那么加个锁会是什么样？代码加个锁，再试一下。

    
    
    class SingleTest
    {
    public:
        static SingleTest *Instance();
        void test();
        int get();
    
    protected:
        SingleTest();
        ~SingleTest();
    
    private:
        int m;
        pthread_mutex_t m_mutex;
    };
    
    SingleTest *SingleTest::Instance()
    {
        static SingleTest st;
        return &st;
    }
    
    void SingleTest::test()
    {
        int i, loc, s = 0;
        for (i = 0; i < 5000; ++i)
        {
            s = pthread_mutex_lock(&m_mutex);
            if (s != 0)
                printf("lock error \n");
            loc = m;
            ++loc;
            m = loc;
            s = pthread_mutex_unlock(&m_mutex);
            if (s != 0)
                printf("unlock error\n");
        }
    }
    
    int SingleTest::get()
    {
        return m;
    }
    
    SingleTest::SingleTest()
    {
        m = 0;
        pthread_mutex_init(&m_mutex, NULL);
        printf("SingleTest Create\n");
    }
    
    SingleTest::~SingleTest()
    {
        pthread_mutex_destroy(&m_mutex);
        printf("SingleTest Destroy\n");
    }

经过测试，这样就线程安全了。  
但新的问题又来了，如果有多个成员变量，是一个变量加一个锁？还是用同一个锁？  
如果用同一个锁，那么每次对成员变量进行读写的时候都要上锁。一个线程需要访问成员变量a，先上锁，另一个线程要访问b，此时a和b是没有发生竞争的，但由于用了同一个锁，那么b也要等着a将锁释放后才能进行操作。  
如果一个变量用一个锁，倒是不会发生之前的那种无必要的资源浪费，但锁多了难免麻烦也就多了。  
这就是一个取舍问题了。

还有一种方案，把锁放在类的外面，由线程函数去处理锁

    
    
    static pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    
    class SingleTest
    {
    public:
        static SingleTest *Instance();
        void test();
        int get();
    
    protected:
        SingleTest();
        ~SingleTest();
    
    private:
        int m;
    };
    
    SingleTest *SingleTest::Instance()
    {
        static SingleTest st;
        return &st;
    }
    
    void SingleTest::test()
    {
        int i, loc;
        for (i = 0; i < 5000; ++i)
        {
            loc = m;
            ++loc;
            m = loc;
        }
    }
    
    int SingleTest::get()
    {
        return m;
    }
    
    SingleTest::SingleTest()
    {
        m = 0;
        printf("SingleTest Create\n");
    }
    
    SingleTest::~SingleTest()
    {
        printf("SingleTest Destroy\n");
    }
    
    void *threadFunc(void *arg)
    {
        int s;
        SingleTest *ts = SingleTest::Instance();
    
        s = pthread_mutex_lock(&mutex);
        if (s != 0)
            printf("lock error \n");
    
        ts->test();
    
        s = pthread_mutex_unlock(&mutex);
        if (s != 0)
            printf("unlock error\n");
    
        return NULL;
    }

这样也是线程安全的，但也有一个问题，类的外面并不知道究竟哪个成员函数需要上锁，为了安全，每次调用成员函数都要上锁，还是会存在资源浪费的情况。  
看来，这种单例的实现方式也与不爽的地方，而且，如果是C++11之前的编译器，构造的线程安全性也是不确定的。  
如果是C++11之前的编译器，可以这样实现

    
    
    class SingleTest
    {
    public:
        static SingleTest *Instance();
        void test();
        int get();
    
    protected:
        SingleTest();
        ~SingleTest();
    
    private:
        int m;
        static SingleTest st;
        pthread_mutex_t m_mutex;
    };
    
    SingleTest SingleTest::st;
    
    SingleTest *SingleTest::Instance()
    {
    //  static SingleTest st;
        return &st;
    }
    
    void SingleTest::test()
    {
        int i, loc, s = 0;
        for (i = 0; i < 5000; ++i)
        {
            s = pthread_mutex_lock(&m_mutex);
            if (s != 0)
                printf("lock error \n");
            loc = m;
            ++loc;
            m = loc;
            s = pthread_mutex_unlock(&m_mutex);
            if (s != 0)
                printf("unlock error\n");
        }
    }
    
    int SingleTest::get()
    {
        return m;
    }
    
    SingleTest::SingleTest()
    {
        m = 0;
        pthread_mutex_init(&m_mutex, NULL);
        printf("SingleTest Create\n");
    }
    
    SingleTest::~SingleTest()
    {
        pthread_mutex_destroy(&m_mutex);
        printf("SingleTest Destroy\n");
    }

这种方法有个缺陷，就是如果构造的时候需要传入参数，这种方法就不行了，而且也存在成员变量锁的问题。  
再试试下面这种实现

    
    
    class SingleTest
    {
    public:
        static SingleTest *Instance();
        void test();
        int get();
    
    protected:
        SingleTest();
        ~SingleTest();
    
    private:
    
        class CGarbo {
        public:
            ~CGarbo()
            {
                if (SingleTest::m_instance) {
                    delete m_instance;
                }
            }
        };
    
        int m;
        static SingleTest* m_instance;
        pthread_mutex_t m_mutex;
        static pthread_mutex_t m_insMutex;
        static CGarbo Garbo;
    
    };
    
    pthread_mutex_t SingleTest::m_insMutex = PTHREAD_MUTEX_INITIALIZER;
    SingleTest* SingleTest::m_instance = NULL;
    SingleTest::CGarbo SingleTest::Garbo;
    
    SingleTest *SingleTest::Instance()
    {
        if (NULL == m_instance)
        {
            int s = 0;
            s = pthread_mutex_lock(&m_insMutex);
            if (s != 0)
                printf("lock error \n");
            if (NULL == m_instance)
            {
                m_instance = new SingleTest;
            }
            s = pthread_mutex_unlock(&m_insMutex);
            if (s != 0)
                printf("unlock error\n");
        }
        return m_instance;
    }
    
    void SingleTest::test()
    {
        int i, loc, s = 0;
        for (i = 0; i < 5000; ++i)
        {
            s = pthread_mutex_lock(&m_mutex);
            if (s != 0)
                printf("lock error \n");
            loc = m;
            ++loc;
            m = loc;
            s = pthread_mutex_unlock(&m_mutex);
            if (s != 0)
                printf("unlock error\n");
        }
    }
    
    int SingleTest::get()
    {
        return m;
    }
    
    SingleTest::SingleTest()
    {
        m = 0;
        pthread_mutex_init(&m_mutex, NULL);
        printf("SingleTest Create\n");
    }
    
    SingleTest::~SingleTest()
    {
        pthread_mutex_destroy(&m_mutex);
        printf("SingleTest Destroy\n");
    }

这种实现任何标准下都是构造线程安全的，也不会有内存泄露，同时也支持构造时输入，但实现起来太麻烦，单单构造都需要一个锁。  
但成员变量锁的问题还是存在的，一直没有找到比较完美的方法。

