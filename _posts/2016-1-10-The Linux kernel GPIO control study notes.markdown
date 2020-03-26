---
layout: post
title: Linux内核学习笔记之GPIO控制
date: 发布于2016-01-10 18:23:22 +0800
categories: Linux内核学习笔记
tag: 4
---

* content
{:toc}


    /********************************
<!-- more -->

     * GPIO驱动程序控制GPIO接口高低电平
     * 四个GPIO识别为四个设备
     * 创建四个文件分别控制四个GPIO
     * echo on|off > /dev/driverx
     * 使用电表测量管脚电压观察结果
     * 本例内容详见LDD3第三章
     * 开发板：Tiny 4412
     * 主控芯片：Exynos 4412
     * author: zhangn
     * date: 2016-1-10
     ********************************/
    
    #include <linux/module.h>
    #include <linux/ioport.h>
    #include <linux/io.h>
    #include <linux/fs.h>
    #include <linux/uaccess.h>
    #include <linux/cdev.h>
    #include <linux/proc_fs.h>
    
    //定义设备号
    #define GPIO_MAJOR  60  //主
    #define GPIO_NUM    4   //次
    
    //定义寄存器地址
    #define GP_BASE    0X11000000  //设备的物理基地址，ioremap函数要用到
    #define GP_SIZE    0X1000      //物理地址映射到内核的空间大小
    
    //寄存器基于物理基地址偏移量
    #define GPX3CON     0x0C60
    #define GPX3DAT     0x0C64
    #define GPX3PUD		0x0c68
    
    //1.为每个char设备准备一个私有结构体
    struct mygpio
    {
    	int gpio_num;//设备编号，本例中共有四个设备
    	int gpio_state;//设备状态:on/1,off/0
    	dev_t dev_id;//设备号，内核驱动必须有
    	struct cdev gpio_cdev;//内核内部使用该结构来表示字符设备，内核调用设备操作之前必须分配该结构
    };
    
    static struct mygpio *gpios[GPIO_NUM];
    static void __iomem *vir_base;//如果映射多次，写再结构体内部
    
    //9.实现file_operations中的函数指针
    static int gpio_open(struct inode *inode, struct file *filp)
    {
    	/*应用层每打开一次文件，内核维护一个ｆｉｌｅ结构体
    	  同时为每个打开的文件维护一个ｉｎｏｄｅ结构体
    	  一个文件多次打开有多个ｆｉｌｅ，但都指向同一个ｉｎｏｄｅ
    	  对于inode结构体，我们这里只关心两个成员
    	  dev_t i_rdev,包含init时注册到系统的设备编号
    	  struct cdev *i_cdev指向一个cdev结构体的指针,一个cdev对应一个设备
    	  在这里就是私有结构体mygpio的成员gpio_cdev的指针
    	  应用层打开一个文件，内核创建一个ｆｉｌｅ结构体
    	  ｆｉｌｅ中通过file_operations结构体讲一组操作文件的函数关联
    	  同时内核维护一个ｉｎｏｄｅ，同一文件第一次打开创建，多次打开增加计数
    	  详情请自行查阅ｖｆｓ相关资料
    	  内核调用gpio_open函数时，通过inode参数将设备信息传进来
    	  同时将每次打开文件的ｆｉｌｅ的信息传进来
    	  这里详见ldd3第三章
    	   */
    	struct mygpio *tmp = container_of(inode->i_cdev, struct mygpio, gpio_cdev);
    	filp->private_data = tmp;//该成员主要用来在不同函数中通过ｆｉｌｅ传递数据
    	return 0;
    }
    
    static int gpio_release(struct inode *inode, struct file *filp)
    {
    	//如果ｏｐｅｎ中有需要释放的资源在这里释放
    	//ｏｐｅｎ中的ｔｍｐ指向的内存在外面分配和释放，这里不需要释放
    	return 0;
    }
    
    static ssize_t gpio_write(struct file *filp, const char __user *buf,
    							size_t count, loff_t *f_pos)
    {
    	struct mygpio *dev = filp->private_data;
    	char tmp[10] = {0};
    	int value;
    
    	if(copy_from_user(tmp, buf, 3))
    		return -EFAULT;
    	if(strncmp(tmp, "on", 2) == 0)
    	{
    		value = readl(vir_base + GPX3DAT);
    		value &= ~(1 << (dev->gpio_num+2));
    		writel(value, vir_base + GPX3DAT);
    		dev->gpio_state = 1;
    	}
    	else if(strncmp(tmp, "off", 3) == 0)
    	{
    		value = readl(vir_base + GPX3DAT);
    		value |= 1 << (dev->gpio_num + 2);
    		writel(value, vir_base + GPX3DAT);
    		dev->gpio_state = 0;
    	}
    	else
    		return -1;
    	return count;
    }
    
    //2.准备file_operations结构体
    static struct file_operations gpio_fops = 
    {
    	.owner   = THIS_MODULE,
    	.open    = gpio_open,
    	.release = gpio_release,
    	.write   = gpio_write,
    };
    
    static int __init my_init(void)
    {
    	int i, value;
    	//3.物理地址映射到内核虚拟地址
    	vir_base = ioremap(GP_BASE, GP_SIZE);
    	if(!vir_base)
    	{
    		printk("Cannot ioremap\n");
    		return -EIO;
    	}
    
    	//以下工作每个设备完成一次
    	for(i = 0; i < GPIO_NUM; ++i)
    	{
    		//4.为每个设备的私有结构体分配内存
    		gpios[i] = kzalloc(sizeof(*gpios[i]), GFP_KERNEL);
    		if(!gpios[i])
    		{
    			//为已分配成功的结构体释放内存
    			for(; i >= 0; --i)
    				kfree(gpios[i]);
    			//释放地址映射
    			iounmap(vir_base);
    			return -ENOMEM;
    		}
    
    		//5.为每个设备初始化寄存器
    		value = readl(vir_base + GPX3CON);
    		value |= 0x11111111;
    		writel(value, vir_base + GPX3CON);
    
    		value = readl(vir_base + GPX3DAT);
    		value |= 1 << (i+2);//使用寄存器的第２３４５号管脚
    		writel(value, vir_base + GPX3DAT);
    
    		value = readl(vir_base + GPX3PUD);
    		value = 0x3;
    		writel(value, vir_base + GPX3PUD);
    
    		gpios[i]->gpio_num = i;
    		gpios[i]->gpio_state = 0;
    
    		//6.为设备分配主次设备号
    		gpios[i]->dev_id = MKDEV(GPIO_MAJOR, i);
    		//7.初始化cdev结构体，并和file_operations结构体关联
    		cdev_init(&gpios[i]->gpio_cdev, &gpio_fops);
    		gpios[i]->gpio_cdev.owner = THIS_MODULE;
    		gpios[i]->gpio_cdev.ops = &gpio_fops;
    		//8.通过cdev_add将mygpio中的设备号添加到cdev结构体中
    		cdev_add(&gpios[i]->gpio_cdev, gpios[i]->dev_id, 1);
    	}
    
    	return 0;
    }
    
    static void __exit my_exit(void)
    {
    	int i;
    	iounmap(vir_base);
    	for(i = 0; i < GPIO_NUM; ++i)
    	{
    		if(gpios[i])
    		{
    			cdev_del(&gpios[i]->gpio_cdev);
    			kfree(gpios[i]);
    		}
    	}
    }
    
    
    module_init(my_init);
    module_exit(my_exit);
    
    MODULE_LICENSE("GPL");
    MODULE_AUTHOR("ZhangN");

