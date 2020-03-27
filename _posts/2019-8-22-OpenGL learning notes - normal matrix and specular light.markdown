---
layout: post
title: OpenGL学习笔记：法线矩阵和镜面光照
date: 发布于2019-08-22 16:04:08 +0800
categories: OpenGL学习笔记
tag: 4
---

# 法线矩阵

## 为什么需要法线矩阵

* content
{:toc}


之前我们计算的坐标都是世界坐标，但法线向量却是局部空间的，应该把法线向量也转换到世界空间才对。但把法线向量转换到世界空间，不能简单的乘以模型矩阵，模型矩阵中可能会有位移、缩放、旋转等变换。  
<!-- more -->

首先，法线向量只有方向意义，没有位置意义，因此不能对法线进行位移操作。  
其次，法线向量虽然不能位移，但可以跟随平面做旋转和缩放操作。如果是旋转，法线向量直接跟随旋转即可，但如果是缩放，等比例缩放还算简单，再标准化一次就行，非等比例缩放就麻烦了，因为非等比例缩放会导致向量的各个分量缩放比例不同，从而影响向量的方向，导致法向量不再垂直于平面。  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190830112649793.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
为了解决这个问题，将法向量从局部空间向世界空间转换时需要专门的转换矩阵，我们称之为法线矩阵。

## 法线矩阵推导

根据法线性质可知，平面上任一向量都与法线向量垂直， 即它们的数量积为0。  
设平面上任一向量为v⃗\vec{v}v，法线向量为n⃗\vec{n}n，转换矩阵为MMM，法线矩阵为SSS，转换后的平面向量为v′⃗\vec{v&#x27;}v′，转换后的法线向量为n′⃗\vec{n&#x27;}n′，则有  
v′⃗=Mv⃗n′⃗=Sn⃗n⃗⋅v⃗=(nxnynz)⋅(vxvyvz)=nxvx+nyvy+nzvz=(nxnynz)⋅(vxvyvz)=(n⃗)T⋅v⃗=0
\vec{v&#x27;}=M\vec{v}\\\ \vec{n&#x27;}=S\vec{n}\\\ \vec{n}\cdot
\vec{v}=\left( \begin{array}{ccc}n_x \\\ n_y \\\ n_z \end{array} \right)\cdot
\left( \begin{array}{ccc}v_x \\\ v_y \\\ v_z \end{array}
\right)=n_xv_x+n_yv_y+n_zv_z= \left( \begin{array}{ccc}n_x &amp; n_y &amp; n_z
\end{array} \right)\cdot \left( \begin{array}{ccc}v_x \\\ v_y \\\ v_z
\end{array} \right)=(\vec{n})^T\cdot \vec{v}=0\\\
v′=Mvn′=Snn⋅v=⎝⎛​nx​ny​nz​​⎠⎞​⋅⎝⎛​vx​vy​vz​​⎠⎞​=nx​vx​+ny​vy​+nz​vz​=(nx​​ny​​nz​​)⋅⎝⎛​vx​vy​vz​​⎠⎞​=(n)T⋅v=0  
若要使转换后的n′⃗\vec{n&#x27;}n′依然是v′⃗\vec{v&#x27;}v′的法向量，则有  
n′⃗⋅v′⃗=(n′⃗)T⋅v′⃗=(Sn⃗)T⋅Mv⃗=(n⃗)TSTMv⃗=(n⃗)T⋅v⃗=0
\vec{n&#x27;}\cdot\vec{v&#x27;}=(\vec{n&#x27;})^T\cdot
\vec{v&#x27;}=(S\vec{n})^T\cdot M\vec{v}
=(\vec{n})^TS^TM\vec{v}=(\vec{n})^T\cdot \vec{v}=0
n′⋅v′=(n′)T⋅v′=(Sn)T⋅Mv=(n)TSTMv=(n)T⋅v=0  
若要等式成立，ST⋅MS^T\cdot MST⋅M的结果必须是单位矩阵，根据逆矩阵的性质，STS^TST和MMM必为互逆矩阵，则  
S=(ST)T=(M−1)T S=(S^T)^T=(M^{-1})^T S=(ST)T=(M−1)T

### 使用法线矩阵

在顶点着色器中，我们可以使用inverse和transpose函数自己生成这个法线矩阵，这两个函数对所有类型矩阵都有效。注意我们还要把被处理过的矩阵强制转换为3×3矩阵，来保证它失去了位移属性以及能够乘以vec3的法向量。

    
    
    Normal = mat3(transpose(inverse(model))) * aNormal;
    

在漫反射光照部分，光照表现并没有问题，这是因为我们没有对物体本身执行任何缩放操作，所以并不是必须要使用一个法线矩阵，仅仅让模型矩阵乘以法线也可以。可是，如果你进行了不等比缩放，使用法线矩阵去乘以法向量就是必不可少的了。  
**即使是对于着色器来说，逆矩阵也是一个开销比较大的运算，因此，只要可能就应该避免在着色器中进行逆矩阵运算，它们必须为你场景中的每个顶点都进行这样的处理。用作学习目这样做是可以的，但是对于一个对效率有要求的应用来说，在绘制之前你最好用CPU计算出法线矩阵，然后通过uniform把值传递给着色器（像模型矩阵一样）。**

# 镜面光照

前面的章节中已经把光照强度和光照角度对颜色的影响计算进去了，但对比现实世界还少点东西。在现实世界中，如果我们用一面镜子去观察一盏灯，随着我们的移动，灯在镜子中的位置也会跟随移动，接下来我们就要把现实世界中的这个现象模拟到OpenGL中。由于这个现象和观察者有关系，所以需要计算观察向量和反射向量的角度差。  
我们通过反射法向量周围光的方向来计算反射向量。然后我们计算反射向量和视线方向的角度差，如果夹角越小，那么镜面光的影响就会越大。它的作用效果就是，当我们去看光被物体所反射的那个方向的时候，我们会看到一个高光。  
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190830114332279.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
观察向量是镜面光照附加的一个变量，可以用观察者（摄像机）的世界空间位置与被观察者的世界空间位置做差求得。

# 完整例子

    
    
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
    const char *lightingVertexShaderSource = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "layout(location = 1) in vec3 aNormal;\n"  // 添加法线向量
    "out vec3 Normal;\n"
    "out vec3 FragPos;\n"
    "uniform mat4 model;\n"
    "uniform mat4 view;\n"
    "uniform mat4 projection; \n"
    "void main()\n"
    "{\n"
    "   gl_Position = projection * view * model * vec4(aPos, 1.0);\n"
    // 我们会在世界空间中进行所有的光照计算，因此我们需要一个在世界空间中的顶点位置。
    // 我们可以通过把顶点位置属性乘以模型矩阵（不是观察和投影矩阵）来把它变换到世界空间坐标。
    "	FragPos = vec3(model * vec4(aPos, 1.0));\n"
    // 生成法线矩阵，防止不等比缩放导致法线向量方向错误
    // 注意我们还要把被处理过的矩阵强制转换为3×3矩阵，来保证它失去了位移属性以及能够乘以vec3的法向量。
    // 即使是对于着色器来说，逆矩阵也是一个开销比较大的运算，
    // 因此，只要可能就应该避免在着色器中进行逆矩阵运算，它们必须为你场景中的每个顶点都进行这样的处理。
    // 用作学习目这样做是可以的，但是对于一个对效率有要求的应用来说，
    // 在绘制之前你最好用CPU计算出法线矩阵，然后通过uniform把值传递给着色器（像模型矩阵一样）
    "	Normal = mat3(transpose(inverse(model))) * aNormal;\n"
    "}\0";
    
    // 这个是被光照射的物体的片段着色器，从uniform变量中接受物体的颜色和光源的颜色。
    // 将光照的颜色和物体自身的颜色作分量相乘，结果就是最终要显示出来的颜色向量
    const char *lightingFragmentShaderSource = "#version 330 core\n"
    "out vec4 FragColor;\n"
    "in vec3 Normal;\n"
    "in vec3 FragPos;\n"
    "uniform vec3 viewPos;\n"
    "uniform vec3 objectColor;\n"
    "uniform vec3 lightColor;\n"
    "uniform vec3 lightPos;\n"
    "void main()\n"
    "{\n"
    "	float ambientStrength = 0.1;\n"
    "	vec3 ambient = ambientStrength * lightColor;\n"
    // 标准化法线向量，向量标准化就是不关心长度只关心方向的时候使向量的模为1
    "	vec3 norm = normalize(Normal);\n"
    // 标准化光照方向向量，光源位置减去片段位置就是光源指向片段的方向向量
    // 这里应该是FragPos-lightPos才是光源指向片段的方向
    // 虽然这里只是计算夹角余弦，不会对结果产生影响
    // 但是后面在计算镜面反射的时候还要对这个结果进行取反修正，不知道原教程为毛这么搞
    "	vec3 lightDir = normalize(lightPos - FragPos);\n"
    // 对norm和lightDir向量进行点乘，计算光源对当前片段实际的漫发射影响。
    // 结果值再乘以光的颜色，得到漫反射分量。两个向量之间的角度越大，漫反射分量就会越小
    // 如果两个向量之间的角度大于90度，点乘的结果就会变成负数，这样会导致漫反射分量变为负数。
    // 为此，我们使用max函数返回两个参数之间较大的参数，从而保证漫反射分量不会变成负数。
    // 负数颜色的光照是没有定义的，所以最好避免它，除非你是那种古怪的艺术家。
    "	float diff = max(dot(norm, lightDir), 0.0);\n"
    "	vec3 diffuse = diff * lightColor;\n"
    
    // 镜面强度(Specular Intensity)变量，给镜面高光一个中等亮度颜色，让它不要产生过度的影响
    "	float specularStrength = 0.5;\n"
    // 计算视线方向向量
    // 需要注意的是我们对lightDir向量进行了取反。
    // reflect函数要求第一个向量是从光源指向片段位置的向量，
    // 但是lightDir当前正好相反，是从片段指向光源（由先前我们计算lightDir向量时，减法的顺序决定）。
    // 为了保证我们得到正确的reflect向量，我们通过对lightDir向量取反来获得相反的方向。
    // 第二个参数要求是一个法向量，所以我们提供的是已标准化的norm向量。
    "	vec3 viewDir = normalize(viewPos - FragPos);\n"
    "	vec3 reflectDir = reflect(-lightDir, norm); \n"
    // 计算镜面分量
    // 我们先计算视线方向与反射方向的点乘（并确保它不是负值），然后取它的32次幂。
    // 这个32是高光的反光度(Shininess)。
    // 一个物体的反光度越高，反射光的能力越强，散射得越少，高光点就会越小
    "	float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);\n"
    "	vec3 specular = specularStrength * spec * lightColor;\n"
    // 它镜面分量加到环境光分量和漫反射分量里，再用结果乘以物体的颜色：
    "	vec3 result = (ambient + diffuse + specular) * objectColor;\n"
    "	FragColor = vec4(result, 1.0);\n"
    "}\n\0";
    
    
    // 当我们修改顶点或者片段着色器后，灯的位置或颜色也会随之改变，这并不是我们想要的效果。
    // 我们不希望灯的颜色在接下来的教程中因光照计算的结果而受到影响，而是希望它能够与其它的计算分离。
    // 我们希望灯一直保持明亮，不受其它颜色变化的影响（这样它才更像是一个真实的光源）。
    // 为了实现这个目标，我们需要为灯的绘制创建另外的一套着色器，
    // 从而能保证它能够在其它光照着色器发生改变的时候不受影响。
    // 顶点着色器与我们当前的顶点着色器是一样的，所以你可以直接把现在的顶点着色器用在灯上。
    // 灯的片段着色器给灯定义了一个不变的常量白色，保证了灯的颜色一直是亮的：
    const char *lampVertexShaderSource = "#version 330 core\n"
    "layout (location = 0) in vec3 aPos;\n"
    "uniform mat4 model;\n"
    "uniform mat4 view;\n"
    "uniform mat4 projection; \n"
    "void main()\n"
    "{\n"
    "   gl_Position = projection * view * model * vec4(aPos, 1.0);\n"
    "}\0";
    
    const char *lampFragmentShaderSource = "#version 330 core\n"
    "out vec4 FragColor;\n"
    "void main()\n"
    "{\n"
    "	FragColor = vec4(1.0);\n"
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
    		// 我们把物体的颜色设置为珊瑚红色，并把光源设置为白色。
    		glUniform3fv(glGetUniformLocation(lightingShader, "objectColor"), 1, 
    			glm::value_ptr(glm::vec3(1.0f, 0.5f, 0.31f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "lightColor"), 1, 
    			glm::value_ptr(glm::vec3(1.0f, 1.0f, 1.0f)));
    		glUniform3fv(glGetUniformLocation(lightingShader, "lightPos"), 1,
    			glm::value_ptr(lightPos));
    		glUniform3fv(glGetUniformLocation(lightingShader, "viewPos"), 1,
    			glm::value_ptr(cameraPos));
    
    		glm::mat4 projection(1.0f);
    		projection = glm::perspective(glm::radians(45.0f), 800.0f / 600.0f, 0.1f, 100.0f);
    			
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
    
    

