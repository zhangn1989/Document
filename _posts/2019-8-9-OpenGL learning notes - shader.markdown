---
layout: post
title: OpenGL学习笔记：着色器
date: 发布于2019-08-09 15:32:07 +0800
categories: OpenGL学习笔记
tag: 4
---

# 着色器输入输出关联

* content
{:toc}


当类型和名字都一样的时候，OpenGL就会把两个变量链接到一起，它们之间就能发送数据了（这是在链接程序对象时完成的）。  
<!-- more -->

下面的代码展示了一个着色器的输出作为一个着色器的输入，vec4
vertexColor就是关联变量，可将该着色器定义替换掉之前的测试代码看效果，重复代码就不贴了

    
    
    // 定义顶点着色器
    const char *vertexShaderSource = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "out vec4 vertexColor;\n"
    "void main()\n"
    "{\n"
    "   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);\n"
    "	vertexColor = vec4(0.5, 0.0, 0.0, 1.0);\n"
    "}\0";
    
    //定义片段着色器
    const char *fragmentShaderSource = "#version 330 core\n"
    "in vec4 vertexColor;\n"
    "out vec4 FragColor;\n"
    "void main()\n"
    "{\n"
    "   FragColor = vertexColor;\n"
    "}\n\0";
    
    

# uniform

uniform用来从CPU向GPU发送数据，可以简单理解为多个着色器都可以访问的全局变量，在一个着色器中改变了uniform变量的值，其他着色器读取的时候也是变化后的值  
下面代码是在着色器中重新定义了一个uniform变量的示例

    
    
    // 定义顶点着色器
    const char *vertexShaderSource = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "out vec4 vertexColor;\n"
    "void main()\n"
    "{\n"
    "   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);\n"
    "	vertexColor = vec4(0.5, 0.0, 0.0, 1.0);\n"
    "}\0";
    
    //定义片段着色器
    const char *fragmentShaderSource = "#version 330 core\n"
    "uniform vec4 outColor;\n"
    "out vec4 FragColor;\n"
    "void main()\n"
    "{\n"
    "   FragColor = outColor;\n"
    "}\n\0";
    

示例代码中，除了渲染循坏以外的代码不变，和之前的例子一样，下面只贴出修改后的渲染循环

    
    
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
    
    		// 获取运行的秒数
    		float timeValue = glfwGetTime();
    
    		// 通过sin函数控制颜色的值在0.0到1.0之间改变
    		// sin函数的值域为-1到1，除以2以后值域为-0.5到0.5，再加0.5后，其值域为0到1
    		float greenValue = (sin(timeValue) / 2.0f) + 0.5f;
    
    		// 查询uniform ourColor的位置值
    		// 查询uniform地址不要求你之前使用过着色器程序
    		// 但是更新一个uniform之前你必须先使用程序（调用glUseProgram)
    		// 因为它是在当前激活的着色器程序中设置uniform的
    		int vertexColorLocation = glGetUniformLocation(shaderProgram, "outColor");
    
    		// 设置uniform值
    		glUniform4f(vertexColorLocation, 0.0f, greenValue, 0.0f, 0.0f);
    
    
    		// 因为我们只有一个VAO，所以不需要每次都绑定它，但我们会这样做，以使事情更有条理
    		glBindVertexArray(VAO); 
    		// 使用当前激活的着色器，之前定义的顶点属性配置，和VBO的顶点数据（通过VAO间接绑定）来绘制图元。
    		glDrawArrays(GL_TRIANGLES, 0, 3);
    
    		glfwPollEvents();
    		glfwSwapBuffers(window);
    		Sleep(1);
    	}
    

# 多属性着色器

    
    
    #include <glad/glad.h>
    #include <GLFW/glfw3.h>
    
    #include <iostream>
    #include <windows.h>
    
    const unsigned int SCR_WIDTH = 800;
    const unsigned int SCR_HEIGHT = 600;
    
    // 定义顶点着色器
    const char *vertexShaderSource = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "layout (location = 1) in vec3 aColor;\n"
    "out vec3 outColor;\n"
    "void main()\n"
    "{\n"
    "   gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);\n"
    "	outColor = aColor;\n"
    "}\0";
    
    //定义片段着色器
    const char *fragmentShaderSource = "#version 330 core\n"
    "in vec3 outColor;\n"
    "out vec4 FragColor;\n"
    "void main()\n"
    "{\n"
    "   FragColor = vec4(outColor, 1.0);\n"
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
    
    
    	//定义顶点位置坐标数组
    	float vertices[] = {
    		// 位置              // 颜色
    		0.5f, -0.5f, 0.0f,  1.0f, 0.0f, 0.0f,   // 右下
    		-0.5f, -0.5f, 0.0f,  0.0f, 1.0f, 0.0f,   // 左下
    		0.0f,  0.5f, 0.0f,  0.0f, 0.0f, 1.0f    // 顶部
    	};
    
    	unsigned int VBO;
    	unsigned int VAO;
    
    	// 创建一个内存对象
    	glGenBuffers(1, &VBO);
    	// 创建一个顶点数组对象
    	glGenVertexArrays(1, &VAO);
    	// 首先绑定顶点数组对象，，。
    	glBindVertexArray(VAO);
    	// 然后将内存对象绑定为顶点缓冲对象
    	glBindBuffer(GL_ARRAY_BUFFER, VBO);
    	// 向缓冲内存写入数据
    	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    
    	// 然后配置顶点属性，告诉OpenGL如何把顶点数据链接到顶点着色器的顶点属性上
    	// 第一个参数指定我们要配置的顶点属性。还记得我们在顶点着色器中使用layout(location = 0)定义了position顶点属性的位置值(Location)吗？它可以把顶点属性的位置值设置为0。因为我们希望把数据传递到这一个顶点属性中，所以这里我们传入0。
    	// 第二个参数指定顶点属性的大小。顶点属性是一个vec3，它由3个值组成，所以大小是3。
    	// 第三个参数指定数据的类型，这里是GL_FLOAT(GLSL中vec*都是由浮点数值组成的)。
    	// 下个参数定义我们是否希望数据被标准化(Normalize)。如果我们设置为GL_TRUE，所有数据都会被映射到0（对于有符号型signed数据是 - 1）到1之间。我们把它设置为GL_FALSE。
    	// 第五个参数叫做步长(Stride)，它告诉我们在连续的顶点属性组之间的间隔。由于下个组位置数据在3个float之后，我们把步长设置为3 * sizeof(float)。要注意的是由于我们知道这个数组是紧密排列的（在两个顶点属性之间没有空隙）我们也可以设置为0来让OpenGL决定具体步长是多少（只有当数值是紧密排列时才可用）。一旦我们有更多的顶点属性，我们就必须更小心地定义每个顶点属性之间的间隔，我们在后面会看到更多的例子（译注: 这个参数的意思简单说就是从这个属性第二次出现的地方到整个数组0位置之间有多少字节）。
    	// 最后一个参数的类型是void*，所以需要我们进行这个奇怪的强制类型转换。它表示位置数据在缓冲中起始位置的偏移量(Offset)。由于位置数据在数组的开头，所以这里是0。我们会在后面详细解释这个参数。
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void *)0);
    	
    	// 由于我们现在有了两个顶点属性，我们不得不重新计算步长值。为获得数据队列中下一个属性值（比如位置向量的下个x分量）我们必须向右移动6个float，其中3个是位置值，另外3个是颜色值。这使我们的步长值为6乘以float的字节数（ = 24字节）。
    	// 同样，这次我们必须指定一个偏移量。对于每个顶点来说，位置顶点属性在前，所以它的偏移量是0。颜色属性紧随位置数据之后，所以偏移量就是3 * sizeof(float)，用字节来计算就是12字节。
    	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void *)(3 * sizeof(float)));
    	
    	// 启用顶点属性
    	glEnableVertexAttribArray(0);
    	glEnableVertexAttribArray(1);
    
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
    		// 因为我们只有一个VAO，所以不需要每次都绑定它，但我们会这样做，以使事情更有条理
    		glBindVertexArray(VAO); 
    		// 使用当前激活的着色器，之前定义的顶点属性配置，和VBO的顶点数据（通过VAO间接绑定）来绘制图元。
    		glDrawArrays(GL_TRIANGLES, 0, 3);
    
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
    

