---
layout: post
title: MinGW下载安装
date: 发布于2015-03-14 17:02:37 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}

神马情况？？截图居然都不见了，算了，懒得补了。

<!-- more -->

MinGW是什么我这里就不介绍了，百度上好多。

关于MinGW的安装方法，百度上也能找到好多，但都是比较老的版本的，对于英语不好的朋友看着比较困难，将自己的安装过程写下来，既可以帮助英语不太好的朋友，又能让自己以后找着方便。

好了，废话不多说了，我们先去MinGW的官网：[http://www.mingw.org](http://www.mingw.org/)

如果英语比较好，可以阅读下官网上的介绍和安装方法，很详细。

MinGW安装方法分为两种，一种方法是下载自动安装工具，优点是安装简单，缺点是自由度相对较低和天朝的局域网，适合新手朋友；另一种是手动下载各个文件，优点是自由度高，可以根据自己的需要进行选择，缺点是手动下载麻烦，适合老手。

好，我们来到的官网的主页，自动安装可以点击下面的Download Installer下载自动安装工具，手动安装点击下面的Download进入文件下载页面。

文件下载页面如下图，同样可以点击下图红框中的连接下载自动安装工具。

无论是手动安装还是自动安装，都有必要进入这个页面，由于天朝的局域网，自动安装的时候经常会有文件下载失败，需要来到这里手动下载。

手动安装就不说了，点进去下载想要的文件和库就行了，对于tar.lzma文件，可以用7z解压。

至于都需要下载哪些文件，抱歉，我也不清楚，我用自动下载的方法下的。

下面我们来说下自动安装工具的使用。

这就是那个安装工具了，双击运行，单击Install，选择安装路径，其他配置默认就性，单击Continue，等待下载安装管理器。

下载完成后单击Continue自动运行下载管理器

选择Basic Setup，在右边选择你所用到的工具，鼠标单击可以在下面看到介绍。

mingw32-base是基本的C语言编译工具，包括编译器、连接器、调试器、运行库等等之类的，必选，其他的可以根据需要。

msys-base是一个模拟Linux终端的一个工具，如果你的cmd命令无法，可以用这个工具。

mingw-developer-toolkit是什么我也不太清楚，百度也没找到什么结果，有知道的麻烦给说下，谢谢。既然不知道是干什么用的，我通常都会选上。

其他的几项是其他语言的编译工具，可以根据自己的需要进行选择，我的选择如下图。

选好后点击Installation，选择Apply Changes，点击Apply开始下载

剩下的事情就是等了。

中间如果下载出错，先把出错的关掉再重新下载几次。如果重新下载是失败，就要到文件下载页面去手动下载，然后将下载后的文件放到MinGW安装目录下的\var\cache\mingw-
get\packages文件夹下，我的是D:\MinGW\var\cache\mingw-
get\packages，然后在重新下载一次，这个时候程序验证全部文件已下载完毕，就自动解压了。

接下来添加环境变量，怎么添加我这里就不说了，这里只说下需要添加哪些值。

1.将bin文件夹路径添加到PATH变量中，注意分号，我的路径是D:\MinGW\bin

2.新建环境变量LIBRARY_PATH，值为lib文件夹的路径，我的是D:\MinGW\lib

3.新建环境变量C_INCLUDE_PATH，值include文件夹路径，我的是D:\MinGW\include

到此，环境就安装完毕了，接下来我们才测试一下

打开cmd，或者msys（MinGW\msys\1.0\msys.bat），在命令行中输入gcc -v，如果安装成功返回gcc的版本信息。

找个c程序编译一下，找段C代码，如下

    
    
    #include <windows.h>
    
    LRESULT CALLBACK WndProc(HWND, UINT, WPARAM, LPARAM);
    
    int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevIntance,
    	PSTR szCmdLine, int iCmdShow)
    {
    	static   TCHAR szAppName[] = TEXT("HelloWin");
    	HWND     hwnd;
    	MSG      msg;
    	WNDCLASS wndclass;
    
    	wndclass.style         = CS_HREDRAW | CS_VREDRAW;
    	wndclass.lpfnWndProc   = WndProc;
    	wndclass.cbClsExtra    = 0;
    	wndclass.cbWndExtra    = 0;
    	wndclass.hInstance     = hInstance;
    	wndclass.hIcon         = LoadIcon(NULL, IDI_APPLICATION);
    	wndclass.hCursor       = LoadCursor(NULL, IDC_ARROW);
    	wndclass.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH);
    	wndclass.lpszClassName = szAppName;
    	wndclass.lpszMenuName  = NULL;
    
    	if(!RegisterClass(&wndclass))
    	{
    		MessageBox(NULL, TEXT("This program requires Windows NT!"),
    			szAppName, MB_ICONERROR);
    		return 0;
    	}
    
    	hwnd = CreateWindow(szAppName,
    			    TEXT("The Hello Program"),
    			    WS_OVERLAPPEDWINDOW,
    			    CW_USEDEFAULT,
    			    CW_USEDEFAULT,
    			    CW_USEDEFAULT,
    			    CW_USEDEFAULT,
    			    NULL,
    			    NULL,
    			    hInstance,
    			    NULL);
    
    	ShowWindow(hwnd, iCmdShow);
    	UpdateWindow(hwnd);
    
    	while (GetMessage(&msg, NULL, 0, 0))
    	{
    		TranslateMessage(&msg);
    		DispatchMessage(&msg);
    	}
    	return msg.wParam;
    }
    
    LRESULT CALLBACK WndProc(HWND hwnd, UINT message, WPARAM wParam, LPARAM lParam)
    {
    	HDC         hdc;
    	PAINTSTRUCT ps;
    	RECT	    rect;
    
    	switch(message)
    	{
    	case WM_CREATE:
    		return 0;
    	case WM_PAINT:
    		hdc = BeginPaint(hwnd, &ps);
    		GetClientRect(hwnd,&rect);
    		DrawText(hdc, TEXT("Hello, Windows!"), -1, &rect,
    				DT_SINGLELINE | DT_CENTER | DT_VCENTER);
    		EndPaint(hwnd,&ps);
    		return 0;
    	case WM_DESTROY:
    		PostQuitMessage(0);
    		return 0;
    	}
    	return DefWindowProc(hwnd,message,wParam,lParam);
    }

  
将上面代码保存在“HelloWin.C”中（注意后缀的C是大写字母），然后执行命令gcc HelloWin.C，返回结果如下图

编译通过，但链接的时候出现了两个错误。

第二个错误“(.eh_frame+0x13): undefined reference to
`__gxx_personality_v0'”真心蛋疼，只要把后缀的大写字母C改成小写字母c就可以了。

对于第一个错误“(.text+0x67): undefined reference to
`GetStockObject@4'”，只要加上参数“-mwindows” 就可以了。

好，我们再试一下，首先把“HelloWin.C”重命名为“HelloWin.c”，再执行命令“gccHelloWin.c
-mwindows”，返回结果如下图

OK，编译通过，在同目录下生成了a.exe，我们运行下试试

生成的a.exe可以正常运行。

另外需要说明的是，Makefile也是可以用的，写法和Linux的完全一样，不同的是执行的命令不是make，而是mingw32-make。

当然，你也可以把MinGW\bin目录下的mingw32-make.exe文件重命名为make.exe，就可以使用make命令去执行Makefile了

