---
layout: post
title: OpenGL学习笔记：投光物
date: 发布于2019-09-04 15:32:15 +0800
categories: OpenGL学习笔记
tag: 4
---

# 平行光

* content
{:toc}


这部分好理解，只贴出着色器代码，注意：这里删除了灯源位置，添加了无限远光源的方向
<!-- more -->


    
    
    #version 330 core
    // 定义材质结构体
    struct Material {
    //    vec3 ambient;		// 移除了环境光材质颜色向量，因为环境光颜色在几乎所有情况下都等于漫反射颜色，所以我们不需要将它们分开储存
        sampler2D diffuse;	// 将之前定义的vec3漫反射颜色向量替换为漫反射贴图
        sampler2D specular;		// 设置的是镜面光照对物体的颜色影响（或者甚至可能反射一个物体特定的镜面高光颜色）
        float shininess;	// 影响镜面高光的散射/半径
    };
    uniform Material material;
    
    // 定义光的属性结构体用来对光照的三个属性进行控制
    struct Light {
    // vec3 position; // 使用定向光不需要关心位置
        vec3 direction;		// 但依然要关心方向
    
        vec3 ambient;
        vec3 diffuse;
        vec3 specular;
    };
    
    uniform Light light;
    
    out vec4 FragColor;
    in vec3 Normal;
    in vec3 FragPos;
    in vec2 TexCoords;
    uniform vec3 viewPos;
    void main()
    {
    	// 环境光
    // 下面注释掉这一句作为对比，使用纹理作为环境光颜色分量
    	vec3 ambient = light.ambient * texture(material.diffuse, TexCoords).rgb;
    //	vec3 ambient  = light.ambient * material.ambient;
    
    	// 漫反射 
        vec3 norm = normalize(Normal);
    // 我们目前使用的光照计算需求一个从片段至光源的光线方向，但人们更习惯定义定向光为一个从光源出发的全局方向
    	vec3 lightDir = normalize(-light.direction);
    //	vec3 lightDir = normalize(light.position - FragPos);
        float diff = max(dot(norm, lightDir), 0.0);
    // 下面注释掉这一句作为对比，使用纹理作为漫反射颜色分量
    	vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoords).rgb;
    //	vec3 diffuse  = light.diffuse * (diff * material.diffuse);
    
        // 镜面光
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, norm);  
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // 下面注释掉这一句作为对比，使用纹理作为镜面光颜色分量
    	vec3 specular = light.specular * spec * texture(material.specular, TexCoords).rgb;
    //	vec3 specular = light.specular * (spec * material.specular);
    
        vec3 result = ambient + diffuse + specular;
        FragColor = vec4(result, 1.0);
    }
    

# 点光源

这一节主要是光照衰减，衰减公式看起来很复杂，但很好理解，这里也只贴出着色器代码。注意：和上一节的平行光相比，将删除的位置恢复了，并且不需要专门的方向向量

    
    
    #version 330 core
    // 定义材质结构体
    struct Material {
    //    vec3 ambient;		// 移除了环境光材质颜色向量，因为环境光颜色在几乎所有情况下都等于漫反射颜色，所以我们不需要将它们分开储存
        sampler2D diffuse;	// 将之前定义的vec3漫反射颜色向量替换为漫反射贴图
        sampler2D specular;		// 设置的是镜面光照对物体的颜色影响（或者甚至可能反射一个物体特定的镜面高光颜色）
        float shininess;	// 影响镜面高光的散射/半径
    };
    uniform Material material;
    
    // 定义光的属性结构体用来对光照的三个属性进行控制
    struct Light {
    	vec3 position; 
    
        vec3 ambient;
        vec3 diffuse;
        vec3 specular;
    
    // 衰减公式：F=1.0/(Kc+Kl*d+Kq*d*d)
    // 衰减公式所用的三个常数项
    // 具体数据选择其实是个经验性的东西
        float constant;
        float linear;
        float quadratic;
    };
    
    uniform Light light;
    
    out vec4 FragColor;
    in vec3 Normal;
    in vec3 FragPos;
    in vec2 TexCoords;
    uniform vec3 viewPos;
    void main()
    {
    	// 环境光
    // 下面注释掉这一句作为对比，使用纹理作为环境光颜色分量
    	vec3 ambient = light.ambient * texture(material.diffuse, TexCoords).rgb;
    //	vec3 ambient  = light.ambient * material.ambient;
    
    	// 漫反射 
        vec3 norm = normalize(Normal);
    
    	vec3 lightDir = normalize(light.position - FragPos);
        float diff = max(dot(norm, lightDir), 0.0);
    // 下面注释掉这一句作为对比，使用纹理作为漫反射颜色分量
    	vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoords).rgb;
    //	vec3 diffuse  = light.diffuse * (diff * material.diffuse);
    
        // 镜面光
        vec3 viewDir = normalize(viewPos - FragPos);
        vec3 reflectDir = reflect(-lightDir, norm);  
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    // 下面注释掉这一句作为对比，使用纹理作为镜面光颜色分量
    	vec3 specular = light.specular * spec * texture(material.specular, TexCoords).rgb;
    //	vec3 specular = light.specular * (spec * material.specular);
    
    	// 根据衰减公式计算衰减
    	float distance = length(light.position - FragPos);
    	float attenuation = 1.0 / (light.constant + light.linear * distance + 
                    light.quadratic * (distance * distance));
    	// 将衰减计算进去
    	ambient  *= attenuation; 
    	diffuse  *= attenuation;
    	specular *= attenuation;
        vec3 result = ambient + diffuse + specular;
        FragColor = vec4(result, 1.0);
    }
    

# 聚光

这个也很好理解，根据两个角度的大小判断像素点是否落在光锥之内，在光锥内用点光源计算光照，光锥外用环境光计算光照

    
    
    #version 330 core
    // 定义材质结构体
    struct Material {
    //    vec3 ambient;		// 移除了环境光材质颜色向量，因为环境光颜色在几乎所有情况下都等于漫反射颜色，所以我们不需要将它们分开储存
        sampler2D diffuse;	// 将之前定义的vec3漫反射颜色向量替换为漫反射贴图
        sampler2D specular;		// 设置的是镜面光照对物体的颜色影响（或者甚至可能反射一个物体特定的镜面高光颜色）
        float shininess;	// 影响镜面高光的散射/半径
    };
    uniform Material material;
    
    // 定义光的属性结构体用来对光照的三个属性进行控制
    struct Light {
        vec3  position;		// 光源位置。由于本例要实现一个手电筒效果，所以这里不是以前的世界光源的位置，而是摄像机的位置
        vec3  direction;	// 同样，这里是摄像机的观察方向
        float cutOff;		// 切光角
    
        vec3 ambient;
        vec3 diffuse;
        vec3 specular;
    
    // 衰减公式：F=1.0/(Kc+Kl*d+Kq*d*d)
    // 衰减公式所用的三个常数项
    // 具体数据选择其实是个经验性的东西
        float constant;
        float linear;
        float quadratic;
    };
    
    uniform Light light;
    
    out vec4 FragColor;
    in vec3 Normal;
    in vec3 FragPos;
    in vec2 TexCoords;
    uniform vec3 viewPos;
    void main()
    {
    	vec3 lightDir = normalize(light.position - FragPos);
        // check if lighting is inside the spotlight cone
        float theta = dot(lightDir, normalize(-light.direction)); 
    	if(theta > light.cutOff) 
    	{       
    	  // 执行光照计算
    		// 环境光
    		vec3 ambient = light.ambient * texture(material.diffuse, TexCoords).rgb;
    
    		// 漫反射 
    		vec3 norm = normalize(Normal);
    		float diff = max(dot(norm, lightDir), 0.0);
    		vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoords).rgb;
    
    		// 镜面光
    		vec3 viewDir = normalize(viewPos - FragPos);
    		vec3 reflectDir = reflect(-lightDir, norm);  
    		float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    		vec3 specular = light.specular * spec * texture(material.specular, TexCoords).rgb;
    
    		// 根据衰减公式计算衰减
    		float distance = length(light.position - FragPos);
    		float attenuation = 1.0 / (light.constant + light.linear * distance + 
    					light.quadratic * (distance * distance));
    
    		// 将衰减计算进去
    		// ambient  *= attenuation; // 移除环境中的衰减，否则在远距离处，由于其他分支中的环境条件，内部的光线会比聚光灯外部更暗。
    		diffuse  *= attenuation;
    		specular *= attenuation;
    		vec3 result = ambient + diffuse + specular;
    		FragColor = vec4(result, 1.0);
    	}
    	else 
        {
    		// 使用环境光，使聚光灯外的场景不是完全黑暗。
            FragColor = vec4(light.ambient * texture(material.diffuse, TexCoords).rgb, 1.0);
        }
    
    }
    

# 软化边缘

这个的原理可以简单的理解为，在上一小节的聚光圆锥的外围再套上一个大一点的圆锥，并给定一个0到1的强度值。当像素点落在内圆锥中，强度值就是1，落在外圆锥外，强度值就是0，落在内圆锥之外，外圆锥之内，就根据距离内圆锥边缘的距离给定一个在0到1之间的强度值。由于有了这个强度值作为过度，就不需要上一小节的光锥内外的判断了。  
这个原理理解起来很容易，但看明白那个公式就比较复杂了，如果画张图会好理解，原作者没有画，我也懒得画，具体公式就不细说了，下面给出完整例子。

    
    
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
    layout (location = 2) in vec2 aTexCoords;	// 添加纹理的输入输出
    out vec3 Normal;
    out vec3 FragPos;
    out vec2 TexCoords;
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection; 
    void main()
    {
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
    	TexCoords = aTexCoords;
    	gl_Position = projection * view * vec4(FragPos, 1.0);
    })1234";
    
    // 这个是被光照射的物体的片段着色器，从uniform变量中接受物体的颜色和光源的颜色。
    // 将光照的颜色和物体自身的颜色作分量相乘，结果就是最终要显示出来的颜色向量
    const char *lightingFragmentShaderSource = R"1234(#version 330 core
    // 定义材质结构体
    struct Material {
    //    vec3 ambient;		// 移除了环境光材质颜色向量，因为环境光颜色在几乎所有情况下都等于漫反射颜色，所以我们不需要将它们分开储存
        sampler2D diffuse;	// 将之前定义的vec3漫反射颜色向量替换为漫反射贴图
        sampler2D specular;		// 设置的是镜面光照对物体的颜色影响（或者甚至可能反射一个物体特定的镜面高光颜色）
        float shininess;	// 影响镜面高光的散射/半径
    };
    uniform Material material;
    
    // 定义光的属性结构体用来对光照的三个属性进行控制
    struct Light {
        vec3  position;		// 光源位置。由于本例要实现一个手电筒效果，所以这里不是以前的世界光源的位置，而是摄像机的位置
        vec3  direction;	// 同样，这里是摄像机的观察方向
        float cutOff;		// 切光角
        float outerCutOff;
    
        vec3 ambient;
        vec3 diffuse;
        vec3 specular;
    
    // 衰减公式：F=1.0/(Kc+Kl*d+Kq*d*d)
    // 衰减公式所用的三个常数项
    // 具体数据选择其实是个经验性的东西
        float constant;
        float linear;
        float quadratic;
    };
    
    uniform Light light;
    
    out vec4 FragColor;
    in vec3 Normal;
    in vec3 FragPos;
    in vec2 TexCoords;
    uniform vec3 viewPos;
    void main()
    {      
    	// 环境光
    	vec3 ambient = light.ambient * texture(material.diffuse, TexCoords).rgb;
    
    	// 漫反射 
    	vec3 norm = normalize(Normal);
    	vec3 lightDir = normalize(light.position - FragPos);
    	float diff = max(dot(norm, lightDir), 0.0);
    	vec3 diffuse = light.diffuse * diff * texture(material.diffuse, TexCoords).rgb;
    
    	// 镜面光
    	vec3 viewDir = normalize(viewPos - FragPos);
    	vec3 reflectDir = reflect(-lightDir, norm);  
    	float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    	vec3 specular = light.specular * spec * texture(material.specular, TexCoords).rgb;
    
        // 聚光灯 (软化边缘)
        float theta = dot(lightDir, normalize(-light.direction)); 
        float epsilon = (light.cutOff - light.outerCutOff);
        float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
        diffuse  *= intensity;
        specular *= intensity;
    
    	// 根据衰减公式计算衰减
    	float distance = length(light.position - FragPos);
    	float attenuation = 1.0 / (light.constant + light.linear * distance + 
    				light.quadratic * (distance * distance));
    
    	// 将衰减计算进去
    	ambient  *= attenuation;
    	diffuse  *= attenuation;
    	specular *= attenuation;
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
    
    	glm::vec3 cubePositions[] = {
    		glm::vec3(0.0f,  0.0f,  0.0f),
    		glm::vec3(2.0f,  5.0f, -15.0f),
    		glm::vec3(-1.5f, -2.2f, -2.5f),
    		glm::vec3(-3.8f, -2.0f, -12.3f),
    		glm::vec3(2.4f, -0.4f, -3.5f),
    		glm::vec3(-1.7f,  3.0f, -7.5f),
    		glm::vec3(1.3f, -2.0f, -2.5f),
    		glm::vec3(1.5f,  2.0f, -2.5f),
    		glm::vec3(1.5f,  0.2f, -1.5f),
    		glm::vec3(-1.3f,  1.0f, -1.5f)
    	};
    
    	// 创建立方体
    	float vertices[] = {
    		// 位置				  // 法线				 // 纹理
    		-0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,  0.0f, 0.0f,
    		0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,  1.0f, 0.0f,
    		0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,  1.0f, 1.0f,
    		0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,  1.0f, 1.0f,
    		-0.5f,  0.5f, -0.5f,  0.0f,  0.0f, -1.0f,  0.0f, 1.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f,  0.0f, -1.0f,  0.0f, 0.0f,
    
    		-0.5f, -0.5f,  0.5f,  0.0f,  0.0f, 1.0f,   0.0f, 0.0f,
    		0.5f, -0.5f,  0.5f,  0.0f,  0.0f, 1.0f,   1.0f, 0.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  0.0f, 1.0f,   1.0f, 1.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  0.0f, 1.0f,   1.0f, 1.0f,
    		-0.5f,  0.5f,  0.5f,  0.0f,  0.0f, 1.0f,   0.0f, 1.0f,
    		-0.5f, -0.5f,  0.5f,  0.0f,  0.0f, 1.0f,   0.0f, 0.0f,
    
    		-0.5f,  0.5f,  0.5f, -1.0f,  0.0f,  0.0f,  1.0f, 0.0f,
    		-0.5f,  0.5f, -0.5f, -1.0f,  0.0f,  0.0f,  1.0f, 1.0f,
    		-0.5f, -0.5f, -0.5f, -1.0f,  0.0f,  0.0f,  0.0f, 1.0f,
    		-0.5f, -0.5f, -0.5f, -1.0f,  0.0f,  0.0f,  0.0f, 1.0f,
    		-0.5f, -0.5f,  0.5f, -1.0f,  0.0f,  0.0f,  0.0f, 0.0f,
    		-0.5f,  0.5f,  0.5f, -1.0f,  0.0f,  0.0f,  1.0f, 0.0f,
    
    		0.5f,  0.5f,  0.5f,  1.0f,  0.0f,  0.0f,  1.0f, 0.0f,
    		0.5f,  0.5f, -0.5f,  1.0f,  0.0f,  0.0f,  1.0f, 1.0f,
    		0.5f, -0.5f, -0.5f,  1.0f,  0.0f,  0.0f,  0.0f, 1.0f,
    		0.5f, -0.5f, -0.5f,  1.0f,  0.0f,  0.0f,  0.0f, 1.0f,
    		0.5f, -0.5f,  0.5f,  1.0f,  0.0f,  0.0f,  0.0f, 0.0f,
    		0.5f,  0.5f,  0.5f,  1.0f,  0.0f,  0.0f,  1.0f, 0.0f,
    
    		-0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,  0.0f, 1.0f,
    		0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,  1.0f, 1.0f,
    		0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,  1.0f, 0.0f,
    		0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,  1.0f, 0.0f,
    		-0.5f, -0.5f,  0.5f,  0.0f, -1.0f,  0.0f,  0.0f, 0.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f, -1.0f,  0.0f,  0.0f, 1.0f,
    
    		-0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f,  0.0f, 1.0f,
    		0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f,  1.0f, 1.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,  1.0f, 0.0f,
    		0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,  1.0f, 0.0f,
    		-0.5f,  0.5f,  0.5f,  0.0f,  1.0f,  0.0f,  0.0f, 0.0f,
    		-0.5f,  0.5f, -0.5f,  0.0f,  1.0f,  0.0f,  0.0f, 1.0f
    	};
    
    	unsigned int VBO;
    	unsigned int cubeVAO, lightVAO;
    
    	glGenBuffers(1, &VBO);
    
    	// 创建物体立方体的顶点数据
    	glGenVertexArrays(1, &cubeVAO);
    	glBindVertexArray(cubeVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, VBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    	// 位置属性
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(0);
    	// 法线属性
    	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(3 * sizeof(float)));
    	glEnableVertexAttribArray(1);
    	// 纹理属性
    	glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)(6 * sizeof(float)));
    	glEnableVertexAttribArray(2);
    
    	// 创建光源的顶点数据
    	glGenVertexArrays(1, &lightVAO);
    	glBindVertexArray(lightVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, VBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(0);
    
    	// 请注意，这是允许的，
    	// 对glVertexAttribPointer的调用将VBO注册为顶点属性的绑定顶点缓冲区对象，
    	// 因此我们可以安全地解除绑定
    	glBindBuffer(GL_ARRAY_BUFFER, 0);
    
    	// 您可以在之后取消绑定VAO，以便其他VAO调用不会意外地修改此VAO，但这种情况很少发生。
    	// 修改其他VAO需要调用glBindVertexArray，因此我们通常不会在不直接需要时取消绑定VAO（也不是VBO）。
    	glBindVertexArray(0);
    	
    	// 设置纹理环绕
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_MIRRORED_REPEAT);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_MIRRORED_REPEAT);
    
    	// 设置纹理过滤
    //	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    //	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    
    	// 读取纹理数据
    	int width, height, nrChannels;
    	unsigned char *data = stbi_load("container2.png", &width, &height, &nrChannels, 0);
    
    	// 创建纹理ID
    	unsigned int texture1;
    	glGenTextures(1, &texture1);
    
    	// 绑定纹理内存
    	glBindTexture(GL_TEXTURE_2D, texture1);
    
    	if (data)
    	{
    		GLenum format;
    		if (nrChannels == 1)
    			format = GL_RED;
    		else if (nrChannels == 3)
    			format = GL_RGB;
    		else if (nrChannels == 4)
    			format = GL_RGBA;
    
    		// 使用纹理数据生成纹理
    		glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data);
    		// 自动创建多级纹理
    		glGenerateMipmap(GL_TEXTURE_2D);
    	}
    	else
    	{
    		std::cout << "Failed to load texture1" << std::endl;
    	}
    
    	// 创建好纹理后可以将纹理数据释放
    	if(data)
    		stbi_image_free(data);
    
    	// 使用第二纹理
    	// 读取纹理数据
    	data = stbi_load("container2_specular.png", &width, &height, &nrChannels, 0);
    
    	// 创建纹理ID
    	unsigned int texture2;
    	glGenTextures(1, &texture2);
    
    	// 绑定纹理内存
    	glBindTexture(GL_TEXTURE_2D, texture2);
    
    	if (data)
    	{
    		GLenum format;
    		if (nrChannels == 1)
    			format = GL_RED;
    		else if (nrChannels == 3)
    			format = GL_RGB;
    		else if (nrChannels == 4)
    			format = GL_RGBA;
    
    		// 使用纹理数据生成纹理
    		glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data);
    		// 自动创建多级纹理
    		glGenerateMipmap(GL_TEXTURE_2D);
    	}
    	else
    	{
    		std::cout << "Failed to load texture2" << std::endl;
    	}
    
    	// 创建好纹理后可以将纹理数据释放
    	if (data)
    		stbi_image_free(data);
    
    
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
    			glm::value_ptr(cameraPos));
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.direction"), 1,
    			glm::value_ptr(cameraFront));
    		// 你可以看到，我们并没有给切光角设置一个角度值，反而是用角度值计算了一个余弦值，将余弦结果传递到片段着色器中。
    		// 这样做的原因是在片段着色器中，我们会计算LightDir和SpotDir向量的点积，
    		// 这个点积返回的将是一个余弦值而不是角度值，所以我们不能直接使用角度值和余弦值进行比较。
    		// 为了获取角度值我们需要计算点积结果的反余弦，这是一个开销很大的计算。
    		// 所以为了节约一点性能开销，我们将会计算切光角对应的余弦值，并将它的结果传入片段着色器中。
    		// 由于这两个角度现在都由余弦角来表示了，我们可以直接对它们进行比较而不用进行任何开销高昂的计算。
    		glUniform1f(glGetUniformLocation(lightingShader, "light.cutOff"), glm::cos(glm::radians(5.0f)));
    		glUniform1f(glGetUniformLocation(lightingShader, "light.outerCutOff"), glm::cos(glm::radians(7.5f)));
    
    		glUniform3fv(glGetUniformLocation(lightingShader, "viewPos"), 1,
    			glm::value_ptr(cameraPos));
    
    		glUniform1i(glGetUniformLocation(lightingShader, "material.diffuse"), 0);
    		glUniform1i(glGetUniformLocation(lightingShader, "material.specular"), 1);
    		glUniform1f(glGetUniformLocation(lightingShader, "material.shininess"), 32.0f);
    
    
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.ambient"), 1,
    			glm::value_ptr(glm::vec3(0.3f, 0.3f, 0.3f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.diffuse"), 1,
    			glm::value_ptr(glm::vec3(0.8f, 0.8f, 0.8f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "light.specular"), 1,
    			glm::value_ptr(glm::vec3(1.0f, 1.0f, 1.0f)));
    
    		glUniform1f(glGetUniformLocation(lightingShader, "light.constant"), 1.0f);
    		glUniform1f(glGetUniformLocation(lightingShader, "light.linear"), 0.09f);
    		glUniform1f(glGetUniformLocation(lightingShader, "light.quadratic"), 0.032f);
    
    		glm::mat4 projection(1.0f);
    		projection = glm::perspective(glm::radians(fov), 800.0f / 600.0f, 0.1f, 100.0f);
    
    		glm::mat4 view(1.0f);
    		view = glm::lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
    
    		glUniformMatrix4fv(glGetUniformLocation(lightingShader, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
    		glUniformMatrix4fv(glGetUniformLocation(lightingShader, "view"), 1, GL_FALSE, glm::value_ptr(view));
    
    		glm::mat4 model = glm::mat4(1.0f);
    		glUniformMatrix4fv(glGetUniformLocation(lightingShader, "model"), 1, GL_FALSE, glm::value_ptr(model));
    
    		glActiveTexture(GL_TEXTURE0);
    		glBindTexture(GL_TEXTURE_2D, texture1);
    		glActiveTexture(GL_TEXTURE1);
    		glBindTexture(GL_TEXTURE_2D, texture2);
    		glBindVertexArray(cubeVAO);
    		for (unsigned int i = 0; i < 10; i++)
    		{
    			// calculate the model matrix for each object and pass it to shader before drawing
    			glm::mat4 model = glm::mat4(1.0f);
    			model = glm::translate(model, cubePositions[i]);
    			float angle = 20.0f * i;
    			model = glm::rotate(model, glm::radians(angle), glm::vec3(1.0f, 0.3f, 0.5f));
    			glUniformMatrix4fv(glGetUniformLocation(lightingShader, "model"), 1, GL_FALSE, glm::value_ptr(model));
    
    			glDrawArrays(GL_TRIANGLES, 0, 36);
    		}
    	//	glDrawArrays(GL_TRIANGLES, 0, 36);
    
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
    
    
    

