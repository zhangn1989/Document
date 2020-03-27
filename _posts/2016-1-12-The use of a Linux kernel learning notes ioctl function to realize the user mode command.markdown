---
layout: post
title: Linux内核学习笔记之使用ioctl函数实现用户态命令
date: 发布于2016-01-12 22:57:07 +0800
categories: Linux内核学习笔记
tag: 4
---

驱动程序：

<!-- more -->

    
    
    /********************************
     * GPIO驱动程序控制GPIO接口高低电平
     * 基于gpio库，四个GPIO识别为一个设备
     * 使用miscdevice结构体动态分配设备号，自动创建/dev/文件
     * 使用ioctl函数实现用户态命令
     * 更多内容见于笔记05
     * 开发板：Tiny 4412
     * 主控芯片：Exynos 4412
     * author: zhangn
     * date: 2016-1-12
     ********************************/
    
    #include <linux/module.h>
    #include <linux/fs.h>
    #include <linux/uaccess.h>
    #include <linux/miscdevice.h>
    //包含gpio库头文件
    #include <linux/gpio.h>//所有处理器通用
    #include <plat/gpio-cfg.h>//三棒子芯片公用
    #include <mach/gpio.h>//只针对４４１２芯片
    
    #define GPIO_NUM	4
    
    //0.定义ioctl命令,本例我们定义两个带一个参数的命令
    /****************************************************************
      关于_IOW,这是内核中定义的一个用于向内核写数据的一个宏
      其参数是_IOW(幻数, 命令序号, 命令所占内存大小)
      对于第三个字段，这里要使用参数的数据类型，内核里会使用sizeof获得
      这里具体说明详见ldd3的第六章关于ioctl的说明
      最后要注意的是这的宏定义要和用户态程序完全相同
     *****************************************************************/
    #define GPIO_TYPE	'Z'//区分不同命令而取的８位幻数，为简便随便使用一个字母
    #define GPIO_ON		_IOW(GPIO_TYPE, 1, int)//用户态定义命令参数
    #define GPIO_OFF	_IOW(GPIO_TYPE, 2, int)
    
    //四个设备，定义四个gpio号
    static int gpios[GPIO_NUM];
    
    //7.实现ioctl函数
    //这里书上说函数实参应该在file前面还有个inode参数
    //但加上该参数后用户态传进来的命令和参数错位，
    //去掉该参数后程序正常，不晓得什么原因，是版本问题？
    static long gpio_ioctl(struct file *filp,
    						unsigned int req, unsigned long arg)
    {
    	printk("req = %d, arg = %ld\n", req, arg);
    /*	if(arg>3 || arg<0)
    	{
    		printk("Only support gpio 0~3\n");
    		return -1;
    	}*/
    	//req为命令代码，代表开关．arg为命令参数，代表gpio序号
    	switch(req)
    	{
    		case GPIO_ON:
    			gpio_set_value(gpios[arg], 0);
    			printk("arg_on = %ld\n", arg);
    			break;
    		case GPIO_OFF:
    			gpio_set_value(gpios[arg], 1);
    			printk("arg_off = %ld\n", arg);
    			break;
    		default:
    			printk("arg_err = %ld\n", arg);
    			break;
    	}
    	return 0;
    }
    
    //1.准备file_operations
    static struct file_operations fops = 
    {
    	//本例中使用了ｉｏｃｔｌ函数，不需要ｏｐｅｎ，ｒｅａｄ等函数
    	.owner = THIS_MODULE,
    	.unlocked_ioctl = gpio_ioctl,
    };
    
    //2.准备miscdevice
    //如果将４个ＧＰＩＯ看成一个设备，推荐使用miscdevice代替cdev
    //如果一个驱动程序要驱动多个设备，那么就不应该使用miscdevice
    //miscdevice会在内核中使用同一个主设备号，设备间使用次设备号进行区分
    //内核中会为所有使用misc的设备维护一个链表，具体请自行查阅misc相关信息
    //使用misc的好处是内核会自动创建/dev/文件，自动分配设备号
    static struct miscdevice misc = 
    {
    	.minor = MISC_DYNAMIC_MINOR,//次设备号，使用MISC_DYNAMIC_MINOR系统会自动分配
    	.name  = "gpios",//设备名称，自动创建的/dev/文件也使用这个名字
    	.fops  = &fops,
    };
    
    static int __init my_init(void)
    {
    	int i, ret, gpio_num;
    	//以下工作，每个设备完成一次
    	for(i = 0; i < GPIO_NUM; ++i)
    	{
    		//3.在头文件中找到寄存器的宏定义
    		gpios[i] = EXYNOS4_GPX3(i+2);
    		gpio_num = gpios[i];
    		printk("i = %d, gpios[%d] = %d, num = %d\n", i, i, gpios[i], gpio_num);
    		//4.申请gpio
    		ret = gpio_request(gpio_num, "myio");
    		if(ret)
    		{
    			printk("Request failed...%d\n", ret);
    			for(; i-1 > 0; --i)
    				gpio_free(gpios[i-1]);
    			return ret;
    		}
    		//5.对io进行配置
    		s3c_gpio_cfgpin(gpio_num, S3C_GPIO_OUTPUT);
    		//写入数据，这里是设置默认值
    		gpio_set_value(gpio_num, 0);
    	}
    
    	//6.注册misc
    	ret = misc_register(&misc);
    	if(ret)
    		for(i = 0; i < GPIO_NUM; ++i)
    			gpio_free(gpios[i]);
    
    	return ret;
    }
    
    static void __exit my_exit(void)
    {
    	int i;
    	misc_deregister(&misc);
    	for(i = 0; i < GPIO_NUM; ++i)
    		gpio_free(gpios[i]);
    
    }
    
    
    module_init(my_init);
    module_exit(my_exit);
    
    MODULE_LICENSE("GPL");
    MODULE_AUTHOR("ZhangN");
    

用户态测试程序

    
    
    /*******************************
     * GPIO的用户态测试
     * &> test /dev/gpios 0|1|2|3 on|off
     * author:zhangn
     * date:2016-1-12
     *******************************/
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <sys/ioctl.h>
    
    #define GPIO_TYPE   'Z'
    #define GPIO_ON     _IOW(GPIO_TYPE, 1, int)
    #define GPIO_OFF    _IOW(GPIO_TYPE, 2, int)
    
    int main(int argc, char **argv)
    {
    	int fd;
    	int gpio_num;
    	char *endp;
    	
    	fd = open(argv[1], O_RDWR);
    	if(fd < 0)
    	{
    		printf("Cannot open %s\n", argv[1]);
    		exit(1);
    	}
    
    	gpio_num = strtol(argv[2], &endp, 10);
    	if(gpio_num > 3)
    	{
    		close(fd);
    		printf("Only support gpio 0~3\n");
    		exit(1);
    	}
    
    	printf("arg = %d\n", gpio_num);
    
    	if(strncmp(argv[3], "on", 2) == 0)
    	{
    		ioctl(fd, GPIO_ON, gpio_num);
    	}
    	else if(strncmp(argv[3], "off", 3) == 0)
    	{
    		ioctl(fd, GPIO_OFF, gpio_num);
    	}
    	else
    	{
    		close(fd);
    		exit(1);
    	}
    
    	close(fd);
    	exit(0);
    
    }

* content
{:toc}


