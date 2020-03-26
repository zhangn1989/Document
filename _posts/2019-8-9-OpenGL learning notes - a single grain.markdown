---
layout: post
title: OpenGL学习笔记：单一纹理
date: 发布于2019-08-09 16:52:20 +0800
categories: OpenGL学习笔记
tag: 4
---

* content
{:toc}

纹理简单说就是用一张图片贴到我们的图形上，在贴图的时候，需要指定图形的各个顶点都对应在纹理的哪个部分，这样每个顶点就会关联着一个纹理坐标(Texture
<!-- more -->

Coordinate)，用来标明该从纹理图像的哪个部分采样（就是采集片段颜色）。  
纹理坐标在x和y轴上，范围为0到1之间（注意我们使用的是2D纹理图像）。使用纹理坐标获取纹理颜色叫做采样(Sampling)。纹理坐标起始于(0,
0)，也就是纹理图片的左下角，终始于(1, 1)，即纹理图片的右上角

# 纹理使用步骤

## 着色器部分

首先在顶点着色器中将纹理坐标传递给片段着色器，然后在片段着色器中将调用GLSL内建的texture函数来采样纹理的颜色

## 代码部分

定义顶点数组，将顶点传递给着色器。读取纹理文件数据，创建纹理ID，并绑定内存。设置环绕和过滤方式。使用纹理数据生成纹理，自动创建多级纹理，成功后释放纹理数据内存。设置纹理单元，启用纹理。

    
    
    #include <glad/glad.h>
    #include <GLFW/glfw3.h>
    
    #include <iostream>
    #include <windows.h>
    
    // 一个非常流行的单头文件图像加载库，下载地址在[这里](https://github.com/nothings/stb/blob/master/stb_image.h)
    #define STB_IMAGE_IMPLEMENTATION
    #include "stb_image.h"
    
    const unsigned int SCR_WIDTH = 800;
    const unsigned int SCR_HEIGHT = 600;
    
    // 定义顶点着色器
    // 我们需要调整顶点着色器使其能够接受顶点坐标为一个顶点属性，并把坐标传给片段着色器
    const char *vertexShaderSource = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "layout (location = 1) in vec3 aColor;\n"
    "layout (location = 2) in vec2 aTexCoord;\n"
    "out vec3 ourColor;\n"
    "out vec2 TexCoord;\n"
    "void main()\n"
    "{\n"
    "   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);\n"
    "	ourColor = aColor;\n"
    "	TexCoord = aTexCoord;\n"
    "}\0";
    
    // 定义片段着色器
    // texture是GLSL内建的采样纹理颜色的函数
    // 它第一个参数是纹理采样器，第二个参数是对应的纹理坐标。
    // texture函数会使用之前设置的纹理参数对相应的颜色值进行采样
    // #if这个条件编译用来控制纹理颜色与顶点颜色是否混合
    const char *fragmentShaderSource = "#version 330 core\n"
    "in vec3 ourColor;\n"
    "in vec2 TexCoord;\n"
    "out vec4 FragColor;\n"
    "uniform sampler2D ourTexture;\n"
    "void main()\n"
    "{\n"
    #if 0
    "   FragColor = texture(ourTexture, TexCoord);\n"
    #else
    "	FragColor = texture(ourTexture, TexCoord) * vec4(ourColor, 1.0);\n"
    #endif
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
    
    
    	// 设置纹理环绕方式
    	// 环绕方式				描述
    	// GL_REPEAT			对纹理的默认行为。重复纹理图像。
    	// GL_MIRRORED_REPEAT	和GL_REPEAT一样，但每次重复图片是镜像放置的。
    	// GL_CLAMP_TO_EDGE		纹理坐标会被约束在0到1之间，超出的部分会重复纹理坐标的边缘，产生一种边缘被拉伸的效果。
    	// GL_CLAMP_TO_BORDER	超出的坐标为用户指定的边缘颜色。
    	// 前面提到的每个选项都可以使用glTexParameter*函数对单独的一个坐标轴设置（s、t（如果是使用3D纹理那么还有一个r）它们和x、y、z是等价的）：
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT);
    
    	// 如果我们选择GL_CLAMP_TO_BORDER选项，我们还需要指定一个边缘的颜色。这需要使用glTexParameter函数的fv后缀形式，用GL_TEXTURE_BORDER_COLOR作为它的选项，并且传递一个float数组作为边缘的颜色值：
    	float borderColor[] = { 1.0f, 1.0f, 0.0f, 1.0f };
    	glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor);
    
    	// GL_NEAREST（邻近过滤）：产生了颗粒状的图案，我们能够清晰看到组成纹理的像素
    	// GL_LINEAR（线性过滤）：产生更平滑的图案，很难看出单个的纹理像素
    	// GL_LINEAR可以产生更真实的输出，但有些开发者更喜欢8-bit风格，所以他们会用GL_NEAREST选项
    	// 当进行放大(Magnify)和缩小(Minify)操作的时候可以设置纹理过滤的选项，比如你可以在纹理被缩小的时候使用邻近过滤，被放大时使用线性过滤
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    
    	// 设置多级渐远纹理
    	// 后一级纹理是前一级纹理的二分之一
    	// 距观察者的距离超过一定的阈值，OpenGL会使用不同的多级渐远纹理，即最适合物体的距离的那个
    	// 切换多级渐远纹理级别时你也可以在两个不同多级渐远纹理级别之间使用NEAREST和LINEAR过滤。为了指定不同多级渐远纹理级别之间的过滤方式，你可以使用下面四个选项中的一个代替原有的过滤方式：
    	// 过滤方式						描述
    	// GL_NEAREST_MIPMAP_NEAREST	使用最邻近的多级渐远纹理来匹配像素大小，并使用邻近插值进行纹理采样
    	// GL_LINEAR_MIPMAP_NEAREST		使用最邻近的多级渐远纹理级别，并使用线性插值进行采样
    	// GL_NEAREST_MIPMAP_LINEAR		在两个最匹配像素大小的多级渐远纹理之间进行线性插值，使用邻近插值进行采样
    	// GL_LINEAR_MIPMAP_LINEAR		在两个邻近的多级渐远纹理之间使用线性插值，并使用线性插值进行采样
    	// 纹理放大不会使用多级渐远纹理，为放大过滤设置多级渐远纹理的选项会产生一个GL_INVALID_ENUM错误代码
    	 glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    
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
    	unsigned int texture;
    	glGenTextures(1, &texture);
    
    	// 绑定纹理对象
    	glBindTexture(GL_TEXTURE_2D, texture);
    
    	// 使用文件数据生成纹理
    	// 第一个参数指定了纹理目标(Target)。设置为GL_TEXTURE_2D意味着会生成与当前绑定的纹理对象在同一个目标上的纹理（任何绑定到GL_TEXTURE_1D和GL_TEXTURE_3D的纹理不会受到影响）。
    	// 第二个参数为纹理指定多级渐远纹理的级别，如果你希望单独手动设置每个多级渐远纹理的级别的话。这里我们填0，也就是基本级别。
    	// 第三个参数告诉OpenGL我们希望把纹理储存为何种格式。我们的图像只有RGB值，因此我们也把纹理储存为RGB值。
    	// 第四个和第五个参数设置最终的纹理的宽度和高度。我们之前加载图像的时候储存了它们，所以我们使用对应的变量。
    	// 下个参数应该总是被设为0（历史遗留的问题）。
    	// 第七第八个参数定义了源图的格式和数据类型。我们使用RGB值加载这个图像，并把它们储存为char(byte)数组，我们将会传入对应值。
    	// 最后一个参数是真正的图像数据。
    	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data);
    	glGenerateMipmap(GL_TEXTURE_2D);
    
    	// 图片生成纹理之后就用不掉了，可以删掉了
    	stbi_image_free(data);
    
    	// 使用纹理
    	// 首先定义包含纹理坐标的顶点数组
    	float vertices[] = {
    		//     ---- 位置 ----       ---- 颜色 ----     - 纹理坐标 -
    		0.5f,  0.5f, 0.0f,   1.0f, 0.0f, 0.0f,   1.0f, 1.0f,   // 右上
    		0.5f, -0.5f, 0.0f,   0.0f, 1.0f, 0.0f,   1.0f, 0.0f,   // 右下
    		-0.5f, -0.5f, 0.0f,   0.0f, 0.0f, 1.0f,   0.0f, 0.0f,   // 左下
    		-0.5f,  0.5f, 0.0f,   1.0f, 1.0f, 0.0f,   0.0f, 1.0f    // 左上
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
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(0);
    	// 颜色属性
    	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(3 * sizeof(float)));
    	glEnableVertexAttribArray(1);
    	// 纹理属性
    	glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(6 * sizeof(float)));
    	glEnableVertexAttribArray(2);
    
    	// 请注意，这是允许的，
    	// 对glVertexAttribPointer的调用将VBO注册为顶点属性的绑定顶点缓冲区对象，
    	// 因此我们可以安全地解除绑定
    	glBindBuffer(GL_ARRAY_BUFFER, 0);
    
    	// 您可以在之后取消绑定VAO，以便其他VAO调用不会意外地修改此VAO，但这种情况很少发生。
    	// 修改其他VAO需要调用glBindVertexArray，因此我们通常不会在不直接需要时取消绑定VAO（也不是VBO）。
    	glBindVertexArray(0);
    
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
    
    		// 激活着色器程序
    		glUseProgram(shaderProgram);
    
    		// 绑定纹理，自动把纹理赋值给片段着色器的采样器
    		glBindTexture(GL_TEXTURE_2D, texture);
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
    

