---
layout: post
title: OpenGL学习笔记：坐标系统
date: 发布于2019-08-20 17:29:32 +0800
categories: OpenGL学习笔记
tag: 4
---

# 坐标系转换

* content
{:toc}


在开始这一节内容之前，我们先研究一下如何通过矩阵乘法实现坐标系转换  
<!-- more -->

在XYZ坐标系中，有一个向量v⃗=(xyz)\vec{v}=\left( \begin{array}{ccc}x \\\y \\\z \end{array}
\right)v=⎝⎛​xyz​⎠⎞​，我们可以改写成下面两种形式：  
v⃗=(x00)+(0y0)+(00z)⇓v⃗=x⋅(100)+y⋅(010)+z⋅(001) \vec{v}=\left(
\begin{array}{ccc}x\\\0\\\0\end{array} \right)+\left(
\begin{array}{ccc}0\\\y\\\0\end{array} \right)+\left(
\begin{array}{ccc}0\\\0\\\z\end{array} \right) \\\\\Downarrow{}\\\
\vec{v}=x\cdot\left( \begin{array}{ccc}1\\\0\\\0\end{array}
\right)+y\cdot\left( \begin{array}{ccc}0\\\1\\\0\end{array}
\right)+z\cdot\left( \begin{array}{ccc}0\\\0\\\1\end{array} \right)
v=⎝⎛​x00​⎠⎞​+⎝⎛​0y0​⎠⎞​+⎝⎛​00z​⎠⎞​⇓v=x⋅⎝⎛​100​⎠⎞​+y⋅⎝⎛​010​⎠⎞​+z⋅⎝⎛​001​⎠⎞​  
从这个书写形式中可以看出XYZ三轴的基准向量分别为(100),(010),(001)\left( \begin{array}{ccc}1 \\\0 \\\0
\end{array} \right),\left( \begin{array}{ccc}0 \\\1 \\\0 \end{array}
\right),\left( \begin{array}{ccc}0 \\\0 \\\1 \end{array}
\right)⎝⎛​100​⎠⎞​,⎝⎛​010​⎠⎞​,⎝⎛​001​⎠⎞​。  
同理，在RUD坐标系中，有一个向量w⃗=(rud)\vec{w}=\left( \begin{array}{ccc}r \\\u \\\d
\end{array} \right)w=⎝⎛​rud​⎠⎞​，改写成基准式如下：  
w⃗=(r00)+(0u0)+(00d)⇓w⃗=r⋅(100)+u⋅(010)+d⋅(001) \vec{w}=\left(
\begin{array}{ccc}r\\\0\\\0\end{array} \right)+\left(
\begin{array}{ccc}0\\\u\\\0\end{array} \right)+\left(
\begin{array}{ccc}0\\\0\\\d\end{array} \right) \\\\\Downarrow{}\\\
\vec{w}=r\cdot\left( \begin{array}{ccc}1\\\0\\\0\end{array}
\right)+u\cdot\left( \begin{array}{ccc}0\\\1\\\0\end{array}
\right)+d\cdot\left( \begin{array}{ccc}0\\\0\\\1\end{array} \right)
w=⎝⎛​r00​⎠⎞​+⎝⎛​0u0​⎠⎞​+⎝⎛​00d​⎠⎞​⇓w=r⋅⎝⎛​100​⎠⎞​+u⋅⎝⎛​010​⎠⎞​+d⋅⎝⎛​001​⎠⎞​  
同XYZ坐标系一样，RUD坐标系的三轴的基准向量分别为(100),(010),(001)\left( \begin{array}{ccc}1 \\\0
\\\0 \end{array} \right),\left( \begin{array}{ccc}0 \\\1 \\\0 \end{array}
\right),\left( \begin{array}{ccc}0 \\\0 \\\1 \end{array}
\right)⎝⎛​100​⎠⎞​,⎝⎛​010​⎠⎞​,⎝⎛​001​⎠⎞​。  
到这里，我们不难看出，一个向量在一个坐标系的表示方法其实是用每一个轴的偏移乘以该轴的基准向量，再将所有的乘积进行相加。  
现在，我们将RUD坐标系放在XYZ坐标系中，设R轴的基准向量为R⃗\vec{R}R，U轴的基准向量为U⃗\vec{U}U，D轴的基准向量为D⃗\vec{D}D，RUD三个轴的基准向量都可以用XYZ坐标系表示，即：  
R⃗=(RxRyRz)U⃗=(UxUyUz)D⃗=(DxDyDz) \vec{R}=\left(
\begin{array}{ccc}R_x\\\R_y\\\R_z\end{array} \right)\\\ \vec{U}=\left(
\begin{array}{ccc}U_x\\\U_y\\\U_z\end{array} \right)\\\ \vec{D}=\left(
\begin{array}{ccc}D_x\\\D_y\\\D_z\end{array} \right)\\\
R=⎝⎛​Rx​Ry​Rz​​⎠⎞​U=⎝⎛​Ux​Uy​Uz​​⎠⎞​D=⎝⎛​Dx​Dy​Dz​​⎠⎞​  
至此，我们知道了一个向量在一个坐标系中的表示方法，同时也知道了向量v⃗\vec{v}v在XYZ坐标系中的信息和RUD坐标系的三个轴在XYZ坐标系中的向量表示，就可以使用RUD坐标系来表示向量v⃗\vec{v}v了，也就是将向量v⃗\vec{v}v从XYZ坐标系转换到RUD坐标系中：  
v⃗=x⋅R⃗+y⋅U⃗+z⋅D⃗⇓v⃗=x⋅(RxRyRz)+y⋅(UxUyUz)+z⋅(DxDyDz)⇓v⃗=(x⋅Rx+y⋅Ux+z⋅Dxx⋅Ry+y⋅Uy+z⋅Dzx⋅Rz+y⋅Uy+z⋅Dz)⇓(x⋅Rx+y⋅Ux+z⋅Dxx⋅Ry+y⋅Uy+z⋅Dzx⋅Rz+y⋅Uy+z⋅Dz)=(RxUxDxRyUyDzRzUyDz)⋅(xyz)
\vec{v}=x\cdot\vec{R}+y\cdot\vec{U}+z\cdot\vec{D}\\\\\Downarrow{}\\\
\vec{v}=x\cdot\left( \begin{array}{ccc}R_x\\\R_y\\\R_z\end{array}
\right)+y\cdot\left( \begin{array}{ccc}U_x\\\U_y\\\U_z\end{array}
\right)+z\cdot\left( \begin{array}{ccc}D_x\\\D_y\\\D_z\end{array} \right)\\\
\Downarrow{}\\\ \vec{v}=\left( \begin{array}{ccc}x\cdot R_x+y\cdot U_x+z\cdot
D_x\\\ x\cdot R_y+y\cdot U_y+z\cdot D_z\\\ x\cdot R_z+y\cdot U_y+z\cdot
D_z\end{array} \right) \\\\\Downarrow{}\\\ \left( \begin{array}{ccc}x\cdot
R_x+y\cdot U_x+z\cdot D_x\\\ x\cdot R_y+y\cdot U_y+z\cdot D_z\\\ x\cdot
R_z+y\cdot U_y+z\cdot D_z\end{array} \right)= \left(
\begin{array}{ccc}R_x&amp;U_x&amp;D_x\\\ R_y&amp;U_y&amp;D_z\\\ R_z&amp;
U_y&amp; D_z\end{array} \right) \cdot\left( \begin{array}{ccc}x\\\ y\\\
z\end{array} \right)
v=x⋅R+y⋅U+z⋅D⇓v=x⋅⎝⎛​Rx​Ry​Rz​​⎠⎞​+y⋅⎝⎛​Ux​Uy​Uz​​⎠⎞​+z⋅⎝⎛​Dx​Dy​Dz​​⎠⎞​⇓v=⎝⎛​x⋅Rx​+y⋅Ux​+z⋅Dx​x⋅Ry​+y⋅Uy​+z⋅Dz​x⋅Rz​+y⋅Uy​+z⋅Dz​​⎠⎞​⇓⎝⎛​x⋅Rx​+y⋅Ux​+z⋅Dx​x⋅Ry​+y⋅Uy​+z⋅Dz​x⋅Rz​+y⋅Uy​+z⋅Dz​​⎠⎞​=⎝⎛​Rx​Ry​Rz​​Ux​Uy​Uy​​Dx​Dz​Dz​​⎠⎞​⋅⎝⎛​xyz​⎠⎞​  
总结一下坐标系转换的过程：首先将目的坐标系左右轴的基准向量在源坐标系中表示出来，并写成转换矩阵，然后再将这个矩阵与源坐标系的待转换向量相乘，乘积就是源坐标系向量在目的坐标系的表示了。

# 坐标系统

OpenGL希望在每次顶点着色器运行后，我们可见的所有顶点都为标准化设备坐标(Normalized Device Coordinate,
NDC)。也就是说，每个顶点的x，y，z坐标都应该在-1.0到1.0之间，超出这个坐标范围的顶点都将不可见。我们通常会自己设定一个坐标的范围，之后再在顶点着色器中将这些坐标变换为标准化设备坐标。然后将这些标准化设备坐标传入光栅器(Rasterizer)，将它们变换为屏幕上的二维坐标或像素。  
这一过程中，坐标需要在多个坐标系中进行转换，对我们来说比较重要的总共有5个不同的坐标系统：

  * 局部空间(Local Space，或者称为物体空间(Object Space)，这就是我们程序中定义的坐标)
  * 世界空间(World Space)
  * 观察空间(View Space，或者称为视觉空间(Eye Space)，摄像机的坐标系)
  * 裁剪空间(Clip Space)
  * 屏幕空间(Screen Space)

为了将坐标从一个坐标系变换到另一个坐标系，我们需要用到几个变换矩阵，最重要的几个分别是模型(Model)、观察(View)、投影(Projection)三个矩阵。我们的顶点坐标起始于局部空间(Local
Space)，在这里它称为局部坐标(Local Coordinate)，它在之后会变为世界坐标(World Coordinate)，观察坐标(View
Coordinate)，裁剪坐标(Clip Coordinate)，并最后以屏幕坐标(Screen Coordinate)的形式结束。  
![坐标系转换](/styles/images/blog/OpenGL learning notes - coordinate system_1.png)

# 模型矩阵

这个矩阵主要用来进行缩放、平移、旋转等变换，前面[OpenGL学习笔记：矩阵变换](https://blog.csdn.net/mumufan05/article/details/99743170)章节介绍过，这里不在赘述。

# 观察矩阵

这个在后面的[OpenGL学习笔记：摄像机](https://blog.csdn.net/mumufan05/article/details/99947977)章节会详细介绍，这里先不说

# 投影矩阵

投影分为正射投影和透视投影，比如我们画一个立方体，数学上的画法是三条棱要保持平行，这就是正射投影，美术上的画法是三条棱的延长线要能交于一点，这就是透视投影。  
每种投影都定义一个裁剪空间，将裁剪空间以外的坐标删除，将裁剪空间以内的坐标转换成裁剪空间坐标。正射投影和透视投影主要就是这个裁剪空间不同，具体可以查看原教程的坐标系统小节，这个不难理解，这里不需要多做总结。

# 整体过程

首先将局部坐标通过模型矩阵转换成世界坐标，然后再通过观察矩阵转换成观察空间坐标（摄像机的坐标系就是观察空间坐标系），接下来是通过投影矩阵转换为裁剪坐标（将不在显示范围的坐标删除），最后使用一个叫做视口变换(Viewport
Transform)的过程转换为屏幕坐标。  
为实现这一过程，我们需要将顶点坐标和以上的变换矩阵组合在一起，一个顶点坐标将会根据以下过程被变换到裁剪坐标：

> Vclip=Mprojection⋅Mview⋅Mmodel⋅Vlocal

注意矩阵运算的顺序是相反的（记住我们需要从右往左阅读矩阵的乘法，为什么要从右向左计算请看[  
OpenGL学习笔记：数学基础和常用矩阵总结（二）](https://blog.csdn.net/mumufan05/article/details/100045770#_437)中的矩阵的组合小节）。最后的顶点应该被赋值到顶点着色器中的gl_Position，OpenGL将会自动进行透视除法和裁剪。

# 示例程序

    
    
    #include <glad/glad.h>
    #include <GLFW/glfw3.h>
    
    #include <iostream>
    #include <windows.h>
    
    #define STB_IMAGE_IMPLEMENTATION
    #include "stb_image.h"
    
    #include <glm/glm.hpp>
    #include <glm/gtc/matrix_transform.hpp>
    #include <glm/gtc/type_ptr.hpp>
    
    const unsigned int SCR_WIDTH = 800;
    const unsigned int SCR_HEIGHT = 600;
    
    // 定义顶点着色器
    // 在顶点着色器中定义一个uniform变量用来传递变换矩阵
    // 然后用变换矩阵乘以位置向量得到变换后的位置向量赋值给gl_Position
    // 注意乘法要从右向左读
    const char *vertexShaderSource = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "layout (location = 1) in vec2 aTexCoord;\n"
    "out vec2 TexCoord;\n"
    "uniform mat4 model;\n"
    "uniform mat4 view;\n"
    "uniform mat4 projection; \n"
    "void main()\n"
    "{\n"
    "   gl_Position = projection * view * model * vec4(aPos, 1.0);\n"
    "	TexCoord = vec2(aTexCoord.x, aTexCoord.y);\n"
    "}\0";
    
    // 定义片段着色器
    // texture是GLSL内建的采样纹理颜色的函数
    // 它第一个参数是纹理采样器，第二个参数是对应的纹理坐标。
    // texture函数会使用之前设置的纹理参数对相应的颜色值进行采样
    // 最终输出颜色现在是两个纹理的结合。
    // GLSL内建的mix函数需要接受两个值作为参数，并对它们根据第三个参数进行线性插值。
    // 如果第三个值是0.0，它会返回第一个输入；如果是1.0，会返回第二个输入值。
    // 0.2会返回80%的第一个输入颜色和20%的第二个输入颜色，即返回两个纹理的混合色。
    const char *fragmentShaderSource = "#version 330 core\n"
    "in vec2 TexCoord;\n"
    "out vec4 FragColor;\n"
    "uniform sampler2D texture1;\n"
    "uniform sampler2D texture2;\n"
    "void main()\n"
    "{\n"
    "	FragColor = mix(texture(texture1, TexCoord), texture(texture2, TexCoord), 0.2);\n"
    "}\n\0";
    
    void framebuffer_size_callback(GLFWwindow *window, int width, int height)
    {
    	// 每次窗口变化时重新设置图形的绘制窗口，可以理解为画布
    	glViewport(0, 0, width, height);
    }
    
    void processInput(GLFWwindow *window)
    {
    	if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS)
    		glfwSetWindowShouldClose(window, true);
    }
    
    int main(int argc, char **argv)
    {
    	// 初始化，配置版本号，配置核心模式
    	glfwInit();
    	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    
    	// 创建窗口
    	GLFWwindow *window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "mytest", NULL, NULL);
    	if (!window)
    	{
    		std::cout << "Create Window Error!\n";
    		glfwTerminate();
    		return -1;
    	}
    	glfwMakeContextCurrent(window);
    	// 注册窗口大小变化的回调函数
    	glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
    
    	// 初始化glad
    	// 我们给GLAD传入了用来加载系统相关的OpenGL函数指针地址的函数。
    	// GLFW给我们的是glfwGetProcAddress，它根据我们编译的系统定义了正确的函数。
    	if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    	{
    		std::cout << "Failed to initialize GLAD" << std::endl;
    		glfwTerminate();
    		glfwDestroyWindow(window);
    		return -1;
    	}
    
    	unsigned int vertexShader;
    	// 创建一个顶点着色器
    	// 给着色器附加源码
    	// 编译着色器
    	vertexShader = glCreateShader(GL_VERTEX_SHADER);
    	glShaderSource(vertexShader, 1, &vertexShaderSource, NULL);
    	glCompileShader(vertexShader);
    
    	int success;
    	char infoLog[512] = { 0 };
    	// 获取着色器编译状态
    	glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
    	if (!success)
    	{
    		// 如果编译错误，获取错误信息
    		glGetShaderInfoLog(vertexShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
    	}
    
    	// 编译片段着色器，过程如上面的顶点着色器
    	int fragmentShader;
    	fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    	glShaderSource(fragmentShader, 1, &fragmentShaderSource, NULL);
    	glCompileShader(fragmentShader);
    
    	glGetShaderiv(fragmentShader, GL_COMPILE_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetShaderInfoLog(fragmentShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" << infoLog << std::endl;
    	}
    
    	/* 创建好着色器后，要将多个着色器链接为一个着色器程序对象 */
    	// 创建一个着色器程序对象
    	unsigned int shaderProgram;
    	shaderProgram = glCreateProgram();
    
    	// 添加着色器到着色器程序对象
    	glAttachShader(shaderProgram, vertexShader);
    	glAttachShader(shaderProgram, fragmentShader);
    
    	// 链接它们
    	glLinkProgram(shaderProgram);
    
    	// 与编译着色器一样，需要检测链接是否成功
    	glGetProgramiv(shaderProgram, GL_LINK_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetProgramInfoLog(shaderProgram, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::PROGRAM::LINK_FAILED\n" << infoLog << std::endl;
    	}
    
    	// 链接成功后就可以激活着色器程序
    	glUseProgram(shaderProgram);
    
    	// 至此，我们已经不需要之前的两个片段着色器了，就删了吧
    	glDeleteShader(vertexShader);
    	glDeleteShader(fragmentShader);
    
    	// 加载图片纹理
    	// 加载图片可以自己写，也可以使用库，什么方式不重要，只要能把图片读取到内存就行
    	int width, height, nrChannels;
    	unsigned char *data = stbi_load("container.jpg", &width, &height, &nrChannels, 0);
    	if (!data)
    	{
    		std::cout << "Failed to load texture" << std::endl;
    		// 由于是示例代码，错误处理就不做了，直接退出
    		return 0;
    	}
    
    	// 创建一个纹理内存对象
    	unsigned int texture1;
    	glGenTextures(1, &texture1);
    
    	// 绑定纹理对象
    	glBindTexture(GL_TEXTURE_2D, texture1);
    
    	// 与之前的单一纹理不同，我们需要为每个纹理设置属性
    	// 因此，需要将设置纹理属性的代码放在纹理对象绑定之后，下一个纹理对象绑定之前
    	// 不知道为什么这样，我在纹理对象绑定之前设置纹理属性也没什么问题
    	// 估计应该是如果纹理属性一样设置一个就行了，如果不一样需要分别设置
    	// 但他是怎么找到不同的纹理属性的呢？搞不懂，看来需要等OpenGL使用熟练以后深扒其机制的时候才能搞懂了
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT);
    
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    
    	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data);
    	glGenerateMipmap(GL_TEXTURE_2D);
    
    	// 图片生成纹理之后就用不掉了，可以删掉了
    	stbi_image_free(data);
    
    	// 因为OpenGL要求y轴0.0坐标是在图片的底部的，但是图片的y轴0.0坐标通常在顶部。
    	// 为防止图像颠倒，在图像加载时翻转y轴
    	stbi_set_flip_vertically_on_load(true);
    	data = stbi_load("awesomeface.png", &width, &height, &nrChannels, 0);
    	if (!data)
    	{
    		std::cout << "Failed to load texture" << std::endl;
    		// 由于是示例代码，错误处理就不做了，直接退出
    		return 0;
    	}
    
    	// 创建一个纹理内存对象
    	unsigned int texture2;
    	glGenTextures(1, &texture2);
    
    	// 绑定纹理对象
    	glBindTexture(GL_TEXTURE_2D, texture2);
    
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT);
    
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    
    	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data);
    	glGenerateMipmap(GL_TEXTURE_2D);
    
    	// 图片生成纹理之后就用不掉了，可以删掉了
    	stbi_image_free(data);
    
    	// 使用纹理
    	// 首先定义包含纹理坐标的顶点数组
    	float vertices[] = {
    		//     ---- 位置 ----     - 纹理坐标 -
    		0.5f,  0.5f, 0.0f,  1.0f, 1.0f,   // 右上
    		0.5f, -0.5f, 0.0f,  1.0f, 0.0f,   // 右下
    		-0.5f, -0.5f, 0.0f,  0.0f, 0.0f,   // 左下
    		-0.5f,  0.5f, 0.0f,  0.0f, 1.0f    // 左上
    	};
    
    	// 定义索引数组，就是每个三角形都用哪三个点
    	unsigned int indices[] = { // 注意索引从0开始! 
    		0, 1, 3, // 第一个三角形
    		1, 2, 3  // 第二个三角形
    	};
    
    	unsigned int VBO;
    	unsigned int VAO;
    	unsigned int EBO;
    
    	// 创建一个内存缓冲对象
    	glGenBuffers(1, &VBO);
    	// 创建一个索引缓冲对象
    	glGenBuffers(1, &EBO);
    	// 创建一个顶点数组对象
    	glGenVertexArrays(1, &VAO);
    
    	// 首先绑定顶点数组对象，，。
    	glBindVertexArray(VAO);
    
    	// 然后将内存对象绑定为顶点缓冲对象
    	glBindBuffer(GL_ARRAY_BUFFER, VBO);
    	// 向缓冲内存写入数据
    	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    
    	// 本例中，我们还要为索引缓冲对象绑定内存对象
    	glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO);
    	// 向索引缓冲对象写入数据
    	glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), indices, GL_STATIC_DRAW);
    
    	// 位置属性
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(0);
    	// 颜色属性
    	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    	glEnableVertexAttribArray(1);
    
    	// 请注意，这是允许的，
    	// 对glVertexAttribPointer的调用将VBO注册为顶点属性的绑定顶点缓冲区对象，
    	// 因此我们可以安全地解除绑定
    	glBindBuffer(GL_ARRAY_BUFFER, 0);
    
    	// 您可以在之后取消绑定VAO，以便其他VAO调用不会意外地修改此VAO，但这种情况很少发生。
    	// 修改其他VAO需要调用glBindVertexArray，因此我们通常不会在不直接需要时取消绑定VAO（也不是VBO）。
    	glBindVertexArray(0);
    
    
    	// 激活着色器程序
    	glUseProgram(shaderProgram);
    	// 设置每个采样器的方式告诉OpenGL每个着色器采样器属于哪个纹理单元
    	// 我们只需要设置一次即可，所以这个会放在渲染循环的前面
    	glUniform1i(glGetUniformLocation(shaderProgram, "texture1"), 0);
    	glUniform1i(glGetUniformLocation(shaderProgram, "texture2"), 1);
    
    	// 由于本例是静态图像，所以可以把矩阵放到渲染循坏外面
    	// 首先创建一个模型矩阵。这个模型矩阵包含了位移、缩放与旋转操作，
    	// 它们会被应用到所有物体的顶点上，以变换它们到全局的世界空间
    	// 这里是围绕x轴旋转55度
    	glm::mat4 model(1.0f);
    	model = glm::rotate(model, glm::radians(-55.0f), glm::vec3(1.0f, 0.0f, 0.0f));
    
    	// 观察矩阵，下节细讲
    	// 注意，我们将矩阵向我们要进行移动场景的反方向移动。
    	glm::mat4 view(1.0f);
    	view = glm::translate(view, glm::vec3(0.0f, 0.0f, -3.0f));
    
    	// 最后需要一个投影矩阵
    	glm::mat4 projection(1.0f);
    	// 第一个参数是视野的俯仰角，通常为45度
    	// 第二个参数是物体拉伸比例，一般设为显示窗体的宽高比，如果不是窗体的宽高比则图像会被拉伸
    	// 第三个参数是最近视野范围，所有小于这个范围的物体都不显示
    	// 第四个参数是最远视野范围，所有大于找个范围的物体都不显示
    	projection = glm::perspective(glm::radians(45.0f), 800.0f / 600.0f, 0.1f, 100.0f);
    
    	// 创建渲染循环
    	while (!glfwWindowShouldClose(window))
    	{
    		// 处理输入事件
    		processInput(window);
    
    		// 清空背景颜色
    		// 当调用glClear函数，清除颜色缓冲之后，
    		// 整个颜色缓冲都会被填充为glClearColor里所设置的颜色
    		// 在这里，我们将屏幕设置为了类似黑板的深蓝绿色
    		glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
    		glClear(GL_COLOR_BUFFER_BIT);
    
    		/*****************************************************************
    		OpenGL至少保证有16个纹理单元供你使用，也就是说你可以激活从GL_TEXTURE0到GL_TEXTRUE15。
    		它们都是按顺序定义的，所以我们也可以通过GL_TEXTURE0 + 8的方式获得GL_TEXTURE8，
    		这在当我们需要循环一些纹理单元的时候会很有用。
    		*******************************************************************/
    		// 在绑定纹理之前先激活纹理单元
    		glActiveTexture(GL_TEXTURE0);
    		// 绑定纹理，自动把纹理赋值给片段着色器的采样器
    		glBindTexture(GL_TEXTURE_2D, texture1);
    
    		glActiveTexture(GL_TEXTURE1);
    		glBindTexture(GL_TEXTURE_2D, texture2);
    
    		glUseProgram(shaderProgram);
    		// 每个矩阵对应一个uniform，这里是将矩阵赋值给着色器的uniform
    		int modelLoc = glGetUniformLocation(shaderProgram, "model");
    		glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
    		int modelView = glGetUniformLocation(shaderProgram, "view");
    		glUniformMatrix4fv(modelView, 1, GL_FALSE, glm::value_ptr(view));
    		int modelProj = glGetUniformLocation(shaderProgram, "projection");
    		glUniformMatrix4fv(modelProj, 1, GL_FALSE, glm::value_ptr(projection));
    
    		glBindVertexArray(VAO);
    		glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
    
    		glfwPollEvents();
    		glfwSwapBuffers(window);
    		Sleep(1);
    	}
    
    	glDeleteVertexArrays(1, &VAO);
    	glDeleteBuffers(1, &VBO);
    
    	glfwTerminate();
    	glfwDestroyWindow(window);
    
    	return 0;
    }
    

