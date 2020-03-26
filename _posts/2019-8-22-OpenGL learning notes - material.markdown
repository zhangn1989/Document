---
layout: post
title: OpenGL学习笔记：材质
date: 发布于2019-08-22 17:46:52 +0800
categories: OpenGL学习笔记
tag: 4
---

* content
{:toc}

目测以后的着色器会越来越复杂，还像之前拼接字符串的方式去写可读性会非常差，又不想像原教程那样封装在单独的文件里（这样在网上看代码很麻烦），所以在以后的代码中，着色器采用c++11的格式化字符串的方法去写，c++11以下的编译器可能会编译不过，关于c++11格式化的问题可以看我之前的文章[C++11的一个格式化字符串的黑科技](https://blog.csdn.net/mumufan05/article/details/95199095)  
<!-- more -->

在现实世界中，不同材质的物体反射的光是不同的，比如金属和木头。在OpenGL中通过对环境光照(Ambient Lighting)、漫反射光照(Diffuse
Lighting)和镜面光照(Specular Lighting)三个分量指定一个颜色来模拟材质颜色(Material
Color)。为达到真实想过，要为每个光照分量都指定一个强度向量。

    
    
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
    
    // 定义摄像机的初始信息
    glm::vec3 cameraPos = glm::vec3(0.0f, 0.0f, 3.0f);		// 位置向量
    glm::vec3 cameraFront = glm::vec3(0.0f, 0.0f, -1.0f);	// 方向向量
    glm::vec3 cameraUp = glm::vec3(0.0f, 1.0f, 0.0f);		// 上向量
    
    // 控制移动速度
    float deltaTime = 0.0f;
    float lastFrame = 0.0f; 
    
    // 上一次鼠标的位置，默认是屏幕中心
    float lastX = 400;
    float lastY = 300;
    
    float yaw = -90.0f;
    float pitch = 0.0f;
    float fov = 45.0f;
    
    bool firstMouse = true;
    
    // 灯在世界坐标的位置
    glm::vec3 lightPos(1.2f, 1.0f, 2.0f);
    
    // 本例需要两个着色器
    const char *lightingVertexShaderSource = R"1234(#version 330 core
    layout (location = 0) in vec3 aPos;
    layout(location = 1) in vec3 aNormal;  // 添加法线向量
    out vec3 Normal;
    out vec3 FragPos;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection; 
    void main()
    {
       gl_Position = projection * view * model * vec4(aPos, 1.0);
    // 我们会在世界空间中进行所有的光照计算，因此我们需要一个在世界空间中的顶点位置。
    // 我们可以通过把顶点位置属性乘以模型矩阵（不是观察和投影矩阵）来把它变换到世界空间坐标。
    	FragPos = vec3(model * vec4(aPos, 1.0));
    // 生成法线矩阵，防止不等比缩放导致法线向量方向错误
    // 注意我们还要把被处理过的矩阵强制转换为3×3矩阵，来保证它失去了位移属性以及能够乘以vec3的法向量。
    // 即使是对于着色器来说，逆矩阵也是一个开销比较大的运算，
    // 因此，只要可能就应该避免在着色器中进行逆矩阵运算，它们必须为你场景中的每个顶点都进行这样的处理。
    // 用作学习目这样做是可以的，但是对于一个对效率有要求的应用来说，
    // 在绘制之前你最好用CPU计算出法线矩阵，然后通过uniform把值传递给着色器（像模型矩阵一样）
    	Normal = mat3(transpose(inverse(model))) * aNormal;
    })1234";
    
    // 这个是被光照射的物体的片段着色器，从uniform变量中接受物体的颜色和光源的颜色。
    // 将光照的颜色和物体自身的颜色作分量相乘，结果就是最终要显示出来的颜色向量
    const char *lightingFragmentShaderSource = R"1234(#version 330 core
    // 定义材质结构体
    struct Material {
        vec3 ambient;		// 定义了在环境光照下这个物体反射得是什么颜色，通常这是和物体颜色相同的颜色
        vec3 diffuse;		// 定义了在漫反射光照下物体的颜色。（和环境光照一样）漫反射颜色也要设置为我们需要的物体颜色
        vec3 specular;		// 设置的是镜面光照对物体的颜色影响（或者甚至可能反射一个物体特定的镜面高光颜色）
        float shininess;	// 影响镜面高光的散射/半径
    };
    uniform Material material;
    
    // 定义光的属性结构体用来对光照的三个属性进行控制
    struct Light {
        vec3 position;
    
        vec3 ambient;
        vec3 diffuse;
        vec3 specular;
    };
    
    uniform Light light;
    
    out vec4 FragColor;
    in vec3 Normal;
    in vec3 FragPos;
    uniform vec3 viewPos;
    void main()
    {
    	// 环境光
    	vec3 ambient  = light.ambient * material.ambient;
    
    	// 漫反射 
        vec3 norm = normalize(Normal);
    	vec3 lightDir = normalize(light.position - FragPos);
        float diff = max(dot(norm, lightDir), 0.0);
    	vec3 diffuse  = light.diffuse * (diff * material.diffuse);
    
        // 镜面光
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, norm);  
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    	vec3 specular = light.specular * (spec * material.specular);
    
        vec3 result = ambient + diffuse + specular;
        FragColor = vec4(result, 1.0);
    })1234";
    
    
    // 当我们修改顶点或者片段着色器后，灯的位置或颜色也会随之改变，这并不是我们想要的效果。
    // 我们不希望灯的颜色在接下来的教程中因光照计算的结果而受到影响，而是希望它能够与其它的计算分离。
    // 我们希望灯一直保持明亮，不受其它颜色变化的影响（这样它才更像是一个真实的光源）。
    // 为了实现这个目标，我们需要为灯的绘制创建另外的一套着色器，
    // 从而能保证它能够在其它光照着色器发生改变的时候不受影响。
    // 顶点着色器与我们当前的顶点着色器是一样的，所以你可以直接把现在的顶点着色器用在灯上。
    // 灯的片段着色器给灯定义了一个不变的常量白色，保证了灯的颜色一直是亮的：
    const char *lampVertexShaderSource = R"1234(#version 330 core
    layout (location = 0) in vec3 aPos;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection; 
    void main()
    {
       gl_Position = projection * view * model * vec4(aPos, 1.0);
    })1234";
    
    const char *lampFragmentShaderSource = R"1234(#version 330 core
    out vec4 FragColor;
    void main()
    {
    	FragColor = vec4(1.0);
    })1234";
    
    
    void framebuffer_size_callback(GLFWwindow *window, int width, int height)
    {
    	// 每次窗口变化时重新设置图形的绘制窗口，可以理解为画布
    	glViewport(0, 0, width, height);
    }
    
    void processInput(GLFWwindow *window)
    {
    	if (glfwGetKey(window, GLFW_KEY_SPACE) == GLFW_PRESS)
    		glfwSetWindowShouldClose(window, true);
    
    	// 由于前后平移方向上并没有改变，直接在观察方向上进行移动，所以直接加减就可以了
    	// 但是左右平移需要在左右向量上进行加减，因此需要利用叉乘计算出右向量
    	// glm::normalize是对右向量的标准化
    	// 如果我们没对这个向量进行标准化，最后的叉乘结果会根据cameraFront变量返回大小不同的向量。
    	// 如果我们不对向量进行标准化，我们就得根据摄像机的朝向不同加速或减速移动了，
    	// 但如果进行了标准化移动就是匀速的。
    	float cameraSpeed = 2.5f * deltaTime; // 相应调整
    	if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)
    		cameraPos += cameraSpeed * cameraFront;
    	if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)
    		cameraPos -= cameraSpeed * cameraFront;
    	if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)
    		cameraPos -= glm::normalize(glm::cross(cameraFront, cameraUp)) * cameraSpeed;
    	if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)
    		cameraPos += glm::normalize(glm::cross(cameraFront, cameraUp)) * cameraSpeed;
    }
    
    void cursor_position_callback(GLFWwindow* window, double x, double y)
    {
    	// 防止第一次进入时图像跳动
    	if (firstMouse)
    	{
    		lastX = x;
    		lastY = y;
    		firstMouse = false;
    	}
    
    	float xoffset = x - lastX;
    	float yoffset = lastY - y; // 注意这里是相反的，因为y坐标是从底部往顶部依次增大的
    	lastX = x;
    	lastY = y;
    
    	// 判断右键是否按下，如果不判断右键按下，每次移动鼠标都会转动视角
    	// 但计算偏移量必须在if外面，否则右键没有按下时鼠标移动不会更新last坐标导致下次右键图像跳动
    	if (glfwGetMouseButton(window, GLFW_MOUSE_BUTTON_RIGHT) == GLFW_PRESS)
    	{
    		float sensitivity = 0.5f;
    		xoffset *= sensitivity;
    		yoffset *= sensitivity;
    
    		yaw += xoffset;
    		pitch += yoffset;
    
    		if (pitch > 89.0f)
    			pitch = 89.0f;
    		if (pitch < -89.0f)
    			pitch = -89.0f;
    
    		// 数学太渣，这里是真心看不懂
    		glm::vec3 front;
    		front.x = cos(glm::radians(pitch)) * cos(glm::radians(yaw));
    		front.y = sin(glm::radians(pitch));
    		front.z = cos(glm::radians(pitch)) * sin(glm::radians(yaw));
    		cameraFront = glm::normalize(front);
    	}
    }
    
    void scroll_callback(GLFWwindow* window, double xoffset, double yoffset)
    {
    	if (fov >= 1.0f && fov <= 45.0f)
    		fov -= yoffset;
    	if (fov <= 1.0f)
    		fov = 1.0f;
    	if (fov >= 45.0f)
    		fov = 45.0f;
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
    	glfwSetCursorPosCallback(window, cursor_position_callback);
    	glfwSetScrollCallback(window, scroll_callback);
    	// 让鼠标消失
    	//	glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    
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
    
    	// 分别创建物体着色器和光源着色器
    	int success;
    	char infoLog[512] = { 0 };
    
    	unsigned int lightingVertexShader;
    	lightingVertexShader = glCreateShader(GL_VERTEX_SHADER);
    	glShaderSource(lightingVertexShader, 1, &lightingVertexShaderSource, NULL);
    	glCompileShader(lightingVertexShader);
    
    	glGetShaderiv(lightingVertexShader, GL_COMPILE_STATUS, &success);
    	if (!success)
    	{
    		glGetShaderInfoLog(lightingVertexShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
    	}
    
    	int lightingFragmentShader;
    	lightingFragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    	glShaderSource(lightingFragmentShader, 1, &lightingFragmentShaderSource, NULL);
    	glCompileShader(lightingFragmentShader);
    
    	glGetShaderiv(lightingFragmentShader, GL_COMPILE_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetShaderInfoLog(lightingFragmentShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" << infoLog << std::endl;
    	}
    
    	unsigned int lightingShader;
    	lightingShader = glCreateProgram();
    
    	glAttachShader(lightingShader, lightingVertexShader);
    	glAttachShader(lightingShader, lightingFragmentShader);
    
    	glLinkProgram(lightingShader);
    
    	glGetProgramiv(lightingShader, GL_LINK_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetProgramInfoLog(lightingShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::PROGRAM::LINK_FAILED\n" << infoLog << std::endl;
    	}
    
    	glUseProgram(lightingShader);
    	glDeleteShader(lightingVertexShader);
    	glDeleteShader(lightingFragmentShader);
    
    	unsigned int lampVertexShader;
    	lampVertexShader = glCreateShader(GL_VERTEX_SHADER);
    	glShaderSource(lampVertexShader, 1, &lampVertexShaderSource, NULL);
    	glCompileShader(lampVertexShader);
    
    	glGetShaderiv(lampVertexShader, GL_COMPILE_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetShaderInfoLog(lampVertexShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
    	}
    
    	int lampFragmentShader;
    	lampFragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
    	glShaderSource(lampFragmentShader, 1, &lampFragmentShaderSource, NULL);
    	glCompileShader(lampFragmentShader);
    
    	glGetShaderiv(lampFragmentShader, GL_COMPILE_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetShaderInfoLog(lampFragmentShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::FRAGMENT::COMPILATION_FAILED\n" << infoLog << std::endl;
    	}
    
    	unsigned int lampShader;
    	lampShader = glCreateProgram();
    
    	glAttachShader(lampShader, lampVertexShader);
    	glAttachShader(lampShader, lampFragmentShader);
    	glLinkProgram(lampShader);
    
    	glGetProgramiv(lampShader, GL_LINK_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetProgramInfoLog(lampShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::PROGRAM::LINK_FAILED\n" << infoLog << std::endl;
    	}
    
    	glUseProgram(lampShader);
    	glDeleteShader(lampVertexShader);
    	glDeleteShader(lampFragmentShader);
    
    	// 启用深度测试
    	glEnable(GL_DEPTH_TEST);
    
    
    	// 创建立方体
    	float vertices[] = {
    		//     ---- 位置 ----  ----法线---
    		-0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    		0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    		0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    		0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    		-0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,
    
    		-0.5f, -0.5f,  0.5f,  0.0f,  0.0f, 1.0f,
    		0.5f, -0.5f,  0.5f,  0.0f,  0.0f, 1.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  0.0f, 1.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  0.0f, 1.0f,
    		-0.5f,  0.5f,  0.5f,  0.0f,  0.0f, 1.0f,
    		-0.5f, -0.5f,  0.5f,  0.0f,  0.0f, 1.0f,
    
    		-0.5f,  0.5f,  0.5f, -1.0f,  0.0f,  0.0f,
    		-0.5f,  0.5f, -0.5f, -1.0f,  0.0f,  0.0f,
    		-0.5f, -0.5f, -0.5f, -1.0f,  0.0f,  0.0f,
    		-0.5f, -0.5f, -0.5f, -1.0f,  0.0f,  0.0f,
    		-0.5f, -0.5f,  0.5f, -1.0f,  0.0f,  0.0f,
    		-0.5f,  0.5f,  0.5f, -1.0f,  0.0f,  0.0f,
    
    		0.5f,  0.5f,  0.5f,  1.0f,  0.0f,  0.0f,
    		0.5f,  0.5f, -0.5f,  1.0f,  0.0f,  0.0f,
    		0.5f, -0.5f, -0.5f,  1.0f,  0.0f,  0.0f,
    		0.5f, -0.5f, -0.5f,  1.0f,  0.0f,  0.0f,
    		0.5f, -0.5f,  0.5f,  1.0f,  0.0f,  0.0f,
    		0.5f,  0.5f,  0.5f,  1.0f,  0.0f,  0.0f,
    
    		-0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,
    		0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,
    		0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,
    		0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,
    		-0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,
    
    		-0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f,
    		0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,
    		-0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,
    		-0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f
    	};
    
    	unsigned int VBO;
    	unsigned int cubeVAO, lightVAO;
    
    	glGenBuffers(1, &VBO);
    
    	// 创建物体立方体的顶点数据
    	glGenVertexArrays(1, &cubeVAO);
    	glBindVertexArray(cubeVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, VBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(0);
    	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    	glEnableVertexAttribArray(1);
    
    	// 创建光源的顶点数据
    	glGenVertexArrays(1, &lightVAO);
    	glBindVertexArray(lightVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, VBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(0);
    
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
    		float currentFrame = glfwGetTime();
    		deltaTime = currentFrame - lastFrame;
    		lastFrame = currentFrame;
    
    		// 处理输入事件
    		processInput(window);
    
    		// 清空背景颜色，这次设置为黑色背景
    		glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    		// 由于我们使用了深度测试，所以需要再与上一个GL_DEPTH_BUFFER_BIT清楚深度缓冲
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    		// 绘制物体
    		glUseProgram(lightingShader);
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.position"), 1,
    			glm::value_ptr(lightPos));
    		glUniform3fv(glGetUniformLocation(lightingShader, "viewPos"), 1,
    			glm::value_ptr(cameraPos));
    
    		glUniform3fv(glGetUniformLocation(lightingShader, "material.ambient"), 1,
    			glm::value_ptr(glm::vec3(1.0f, 0.5f, 0.31f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "material.diffuse"), 1,
    			glm::value_ptr(glm::vec3(1.0f, 0.5f, 0.31f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "material.specular"), 1,
    			glm::value_ptr(glm::vec3(0.5f, 0.5f, 0.5f)));
    		glUniform1f(glGetUniformLocation(lightingShader, "material.shininess"), 32.0f);
    
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.ambient"), 1,
    			glm::value_ptr(glm::vec3(0.2f, 0.2f, 0.2f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.diffuse"), 1,
    			glm::value_ptr(glm::vec3(0.5f, 0.5f, 0.5f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.specular"), 1,
    			glm::value_ptr(glm::vec3(1.0f, 1.0f, 1.0f)));
    
    		glm::mat4 projection(1.0f);
    		projection = glm::perspective(glm::radians(fov), 800.0f / 600.0f, 0.1f, 100.0f);
    			
    		glm::mat4 view(1.0f);
    		view = glm::lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
    
    		glUniformMatrix4fv(glGetUniformLocation(lightingShader, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
    		glUniformMatrix4fv(glGetUniformLocation(lightingShader, "view"), 1, GL_FALSE, glm::value_ptr(view));
    
    		glm::mat4 model = glm::mat4(1.0f);
    		glUniformMatrix4fv(glGetUniformLocation(lightingShader, "model"), 1, GL_FALSE, glm::value_ptr(model));
    
    		glBindVertexArray(cubeVAO);
    		glDrawArrays(GL_TRIANGLES, 0, 36);
    
    
    
    		// 绘制光源
    		// 当我们想要绘制我们的物体的时候，我们需要使用刚刚定义的光照着色器来绘制箱子（或者可能是其它的物体）。
    		// 当我们想要绘制灯的时候，我们会使用灯的着色器。
    		// 在之后的教程里我们会逐步更新这个光照着色器，从而能够慢慢地实现更真实的效果。
    		// 使用这个灯立方体的主要目的是为了让我们知道光源在场景中的具体位置。
    		// 我们通常在场景中定义一个光源的位置，但这只是一个位置，它并没有视觉意义。
    		// 为了显示真正的灯，我们将表示光源的立方体绘制在与光源相同的位置。
    		// 我们将使用我们为它新建的片段着色器来绘制它，让它一直处于白色的状态，不受场景中的光照影响。
    		glUseProgram(lampShader);
    		glUniformMatrix4fv(glGetUniformLocation(lampShader, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
    		glUniformMatrix4fv(glGetUniformLocation(lampShader, "view"), 1, GL_FALSE, glm::value_ptr(view));
    
    		// 然后我们把灯位移到这里，然后将它缩小一点，让它不那么明显
    		model = glm::mat4(1.0f);
    		model = glm::translate(model, lightPos);
    		model = glm::scale(model, glm::vec3(0.2f)); // a smaller cube
    		glUniformMatrix4fv(glGetUniformLocation(lampShader, "model"), 1, GL_FALSE, glm::value_ptr(model));
    
    		glBindVertexArray(lightVAO);
    		glDrawArrays(GL_TRIANGLES, 0, 36);
    
    
    		glfwPollEvents();
    		glfwSwapBuffers(window);
    		Sleep(1);
    	}
    
    	glDeleteVertexArrays(1, &cubeVAO);
    	glDeleteVertexArrays(1, &lightVAO);
    	glDeleteBuffers(1, &VBO);
    
    	glfwTerminate();
    	glfwDestroyWindow(window);
    
    	return 0;
    }
    
    

