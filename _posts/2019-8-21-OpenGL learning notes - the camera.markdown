---
layout: post
title: OpenGL学习笔记：摄像机
date: 发布于2019-08-21 14:52:56 +0800
categories: OpenGL学习笔记
tag: 4
---

OpenGL本身没有摄像机(Camera)的概念，但我们可以通过把场景中的所有物体往相反方向移动的方式来模拟出摄像机，产生一种我们在移动的感觉，而不是场景在移动。

<!-- more -->

# 摄像机/观察空间

当我们讨论摄像机/观察空间(Camera/View
Space)的时候，是在讨论以摄像机的视角作为场景原点时场景中所有的顶点坐标：观察矩阵把所有的世界坐标变换为相对于摄像机位置与方向的观察坐标。要定义一个摄像机，我们需要它在世界空间中的位置、观察的方向、一个指向它右测的向量以及一个指向它上方的向量。细心的读者可能已经注意到我们实际上创建了一个三个单位轴相互垂直的、以摄像机的位置为原点的坐标系。  
![摄像机观察坐标系](https://img-blog.csdnimg.cn/20190827151728369.png)

## 摄像机位置

其中，摄像机的位置最为简单，给它一个世界坐标即可，像这样

    
    
    glm::vec3 cameraPos = glm::vec3(0.0f, 0.0f, 3.0f);
    

## 摄像机方向

摄像机方向这里有点绕，在OpenGL中使用的是右手坐标系，z轴的正方向是从屏幕指向你的，如果我们希望摄像机向后移动，我们就沿着z轴的正方向移动。  
假设物体的正面朝向z轴正方向，我们想用摄像机观察这个物体的正面，需要将摄像机放在物体所在位置沿着z轴正方向平移一段距离，并让摄像机的朝向指向物体的正面。由于我们使用的是右手坐标系，所以摄像机的z轴的正方向应该在摄像机的后面。  
根据向量减法，如果我们要求摄像机指向目标的方向向量，需要用目标的位置向量减去摄像机的位置向量。但是这个指向向量的方向是与摄像机z轴的方向相反，我们需要的是一个与z轴方向相同的向量作为方向向量来构建摄像机的观察坐标系，因此，需要用摄像机位置减去目标位置（注意看上图摄像机的蓝色轴）。

    
    
    glm::vec3 cameraTarget = glm::vec3(0.0f, 0.0f, 0.0f);
    glm::vec3 cameraDirection = glm::normalize(cameraPos - cameraTarget);
    

## 右轴

我们需要的另一个向量是一个右向量(Right Vector)，它代表摄像机空间的x轴的正方向。为获取右向量我们需要先使用一个小技巧：先定义一个上向量(Up
Vector)。接下来把上向量和第二步得到的方向向量进行叉乘。两个向量叉乘的结果会同时垂直于两向量，因此我们会得到指向x轴正方向的那个向量（如果我们交换两个向量叉乘的顺序就会得到相反的指向x轴负方向的向量）：

    
    
    glm::vec3 up = glm::vec3(0.0f, 1.0f, 0.0f); 
    glm::vec3 cameraRight = glm::normalize(glm::cross(up, cameraDirection));
    

## 上轴

现在我们已经有了x轴向量和z轴向量，获取一个指向摄像机的正y轴向量就相对简单了：我们把右向量和方向向量进行叉乘

    
    
    glm::vec3 cameraUp = glm::cross(cameraDirection, cameraRight);
    

## Look At矩阵

前面我们为摄像机创建的空间坐标就是[OpenGL学习笔记：坐标系统](https://blog.csdn.net/mumufan05/article/details/99863218)章节中提到的观察空间的坐标系。  
现在观察空间有了，需要将世界空间坐标转换为观察空间坐标。  
具体该怎么做呢？OpenGL中使用Look At矩阵来做这件事，先来看一下Look At矩阵：  
LookAt=(RxRyRz0UxUyUz0DxDyDz00001)⋅(100−Px010−Py001−Pz0001) LookAt=\left(
\begin{array}{ccc} R_x &amp; R_y &amp; R_z &amp; 0\\\ U_x &amp; U_y &amp; U_z
&amp; 0\\\ D_x &amp; D_y &amp; D_z &amp; 0\\\ 0&amp; 0&amp; 0&amp; 1
\end{array} \right) \cdot \left( \begin{array}{ccc} 1&amp; 0&amp; 0&amp;
-P_x\\\ 0&amp; 1&amp; 0&amp; -P_y\\\ 0&amp; 0&amp; 1&amp; -P_z\\\ 0&amp;
0&amp; 0&amp; 1 \end{array} \right)
LookAt=⎝⎜⎜⎛​Rx​Ux​Dx​0​Ry​Uy​Dy​0​Rz​Uz​Dz​0​0001​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​1000​0100​0010​−Px​−Py​−Pz​1​⎠⎟⎟⎞​  
其中R是右向量，U是上向量，D是方向向量P是摄像机位置向量。注意，位置向量是相反的，因为我们最终希望把世界平移到与我们自身移动的相反方向（如果我们想要一个摄像机沿z轴正方向移动的效果，需要将观察目标沿z轴的负方向移动，因为OpenGL中是没有摄像机的，一切的摄像机效果都是通过往反方向移动目标的方式模拟的）。  
Look
At矩阵乘法右边的位移矩阵很好理解，这里不多说。左边的是坐标系转换矩阵，作用是将世界空间坐标转换为观察空间的坐标。这个转换是怎么进行的？为毛用这个矩阵一乘坐标就转换过去了？关于坐标系转换原理，请看[OpenGL学习笔记：坐标系统](https://blog.csdn.net/mumufan05/article/details/99863218)中的坐标系转换小节，这里只贴出该小节所计算出来的转换矩阵  
(RxUxDxRyUyDzRzUyDz) \left( \begin{array}{ccc}R_x&amp;U_x&amp;D_x\\\
R_y&amp;U_y&amp;D_z\\\ R_z&amp; U_y&amp; D_z\end{array} \right)
⎝⎛​Rx​Ry​Rz​​Ux​Uy​Uy​​Dx​Dz​Dz​​⎠⎞​  
细心的读者会发现，这个转换矩阵和Look
At矩阵中的转换矩阵不太一样，这是因为我们算出的转换矩阵是适用于OpenGL的坐标系转换矩阵，而不是严格的数学上的坐标系转换公式所用的转换矩阵。  
如果我们将转换矩阵的推导过程的所有向量全都横着写，那么推导的结果应该是这样的：  
(xyz)⋅(RxRyRzUxUyUzDxDyDz) \left( \begin{array}{ccc} x &amp; y&amp;z
\end{array} \right)\cdot \left( \begin{array}{ccc} R_x &amp; R_y &amp; R_z\\\
U_x &amp; U_y &amp; U_z\\\ D_x &amp; D_y &amp; D_z \end{array} \right)
(x​y​z​)⋅⎝⎛​Rx​Ux​Dx​​Ry​Uy​Dy​​Rz​Uz​Dz​​⎠⎞​  
这才是严格的数学上的坐标系转换公式，但该公式的向量是横着写的，而OpenGL中的向量是竖着写的，所以该公式需要利用矩阵转置的性质来将这个公式变形，回忆一下矩阵转置的公式：  
(AT)T=A(AB)T=BTAT (A^T)^T=A \\\ (AB)^T=B^TA^T (AT)T=A(AB)T=BTAT  
设向量A=(x,y,z)A=(x,y,z)A=(x,y,z)，矩阵M=(RxRyRzUxUyUzDxDyDz)M=\left(
\begin{array}{ccc}R_x &amp; R_y &amp; R_z\\\U_x &amp; U_y &amp; U_z\\\D_x
&amp; D_y &amp; D_z \end{array}
\right)M=⎝⎛​Rx​Ux​Dx​​Ry​Uy​Dy​​Rz​Uz​Dz​​⎠⎞​，则  
((AM)T)T=(MTAT)T=((RxUxDxRyUyDzRzUyDz)⋅(xyz))T=AM ((AM)^T)^T=(M^TA^T)^T=
\left( \begin{array}{ccc}\left( \begin{array}{ccc}R_x&amp;U_x&amp;D_x\\\
R_y&amp;U_y&amp;D_z\\\ R_z&amp; U_y&amp; D_z\end{array} \right)\cdot \left(
\begin{array}{ccc}x\\\ y\\\z\end{array} \right)\end{array} \right)^T=AM
((AM)T)T=(MTAT)T=⎝⎛​⎝⎛​Rx​Ry​Rz​​Ux​Uy​Uy​​Dx​Dz​Dz​​⎠⎞​⋅⎝⎛​xyz​⎠⎞​​⎠⎞​T=AM  
注意：AMAMAM的结果是一个横着写的向量，而OpenGL中需要的是竖着写的向量，因此还要将这个结果转置，即在OpenGL中需要的是MTATM^TA^TMTAT的结果，也就是我们自己所推导的旋转矩阵的格式。  
但glm在设计接口的时候为什么要的是数学公式中的旋转矩阵呢？我猜测应该是为了接口与数学公式的风格统一吧，这样的话，Look
At函数中必然会有一个将矩阵转置的过程，我们来看一下Look At函数的代码

    
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER mat<4, 4, T, Q> lookAtRH(vec<3, T, Q> const& eye, vec<3, T, Q> const& center, vec<3, T, Q> const& up)
    {
    	vec<3, T, Q> const f(normalize(center - eye));
    	vec<3, T, Q> const s(normalize(cross(f, up)));
    	vec<3, T, Q> const u(cross(s, f));
    
    	mat<4, 4, T, Q> Result(1);
    	Result[0][0] = s.x;
    	Result[1][0] = s.y;
    	Result[2][0] = s.z;
    	Result[0][1] = u.x;
    	Result[1][1] = u.y;
    	Result[2][1] = u.z;
    	Result[0][2] =-f.x;
    	Result[1][2] =-f.y;
    	Result[2][2] =-f.z;
    	Result[3][0] =-dot(s, eye);
    	Result[3][1] =-dot(u, eye);
    	Result[3][2] = dot(f, eye);
    	return Result;
    }
    

函数中的f变量就是前面的-D，s就是前面的R，u就是前面的U，Result里存放的就是旋转矩阵。从对Result的赋值上可以看出，将s变量的xyz赋值给Result的第一列，u变量的xyz赋值给Result的第二列，f取反后的xyz赋值给Result的第三列，逻辑内存如下表

| 0 | 1 | 2  
---|---|---|---  
**0** | s.x | u.x | -f.x  
**1** | s.y | u.y | -f.y  
**2** | s.z | u.z | -f.z  
  
矩阵在初始化的时候就直接转置了，倒是不用担心转置运算所造成的资源开销了。  
关于Look At矩阵在gml中的应用，请看下面的例子代码。

# 场景旋转

本例渲染循环以外的代码和之前章节一样，因此这里只给出渲染循环的代码

    
    
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
    	// 由于我们使用了深度测试，所以需要再与上一个GL_DEPTH_BUFFER_BIT清楚深度缓冲
    	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
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
    	
    	// 观察矩阵
    	float radius = 10.0f;
    	float camX = sin(glfwGetTime()) * radius;
    	float camZ = cos(glfwGetTime()) * radius;
    	glm::mat4 view(1.0f);
    	// 参数1：摄像机位置
    	// 参数2：摄像机观察的位置
    	// 参数3：上向量，上向量就是用一个向量表示摄像机顶部的朝向，就是摄像机是正着放还是倒着放或者是斜着放
    	// 上向量大小不重要，只要向量的xyz能够表示出你想要的方向就行
    	// 摄像机实际上还需要一个指向方向向量和一个右向量，目标的位置向量和摄像机位置向量做差就是指向方向向量
    	// 使用上向量和方向向量进行叉乘就能得出右向量，如果我们交换两个向量叉乘的顺序就会得到相反的指向x轴负方向的向量
    	// 方向向量和右向量都可以通过参数123计算获得，因此glm的外部并不需要这两个参数
    	view = glm::lookAt(glm::vec3(camX, 0.0f, camZ), glm::vec3(0.0, 0.0, 3.0), glm::vec3(0.0, 1.0, 0.0));
    
    	// 最后需要一个投影矩阵
    	glm::mat4 projection(1.0f);
    	projection = glm::perspective(glm::radians(45.0f), 800.0f / 600.0f, 0.1f, 100.0f);
    
    	glUseProgram(shaderProgram);
    	// 每个矩阵对应一个uniform，这里是将矩阵赋值给着色器的uniform
    	int modelView = glGetUniformLocation(shaderProgram, "view");
    	glUniformMatrix4fv(modelView, 1, GL_FALSE, glm::value_ptr(view));
    	int modelProj = glGetUniformLocation(shaderProgram, "projection");
    	glUniformMatrix4fv(modelProj, 1, GL_FALSE, glm::value_ptr(projection));
    
    	glBindVertexArray(VAO);
    	for (unsigned int i = 0; i < 10; i++)
    	{
    		// 创建模型矩阵，并使用位移向量数组的数据进行位移
    		glm::mat4 model(1.0f);
    		model = glm::translate(model, cubePositions[i]);
    		// 旋转
    		float angle = 20.0f * i;
    	//	model = glm::rotate(model, glm::radians(angle), glm::vec3(1.0f, 0.3f, 0.5f));
    		model = glm::rotate(model, (float)glfwGetTime() * glm::radians(angle), glm::vec3(1.0f, 0.3f, 0.5f));
    
    		// 将矩阵赋值给着色器的uniform
    		glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"), 1, GL_FALSE, glm::value_ptr(model));
    
    		glDrawArrays(GL_TRIANGLES, 0, 36);
    	}
    
    	glfwPollEvents();
    	glfwSwapBuffers(window);
    	Sleep(1);
    }
    

# 自由移动

    
    
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
    // 目前我们的移动速度是个常量。
    // 理论上没什么问题，但是实际情况下根据处理器的能力不同，
    // 有些人可能会比其他人每秒绘制更多帧，也就是以更高的频率调用processInput函数。
    // 结果就是，根据配置的不同，有些人可能移动很快，而有些人会移动很慢。
    // 当你发布你的程序的时候，你必须确保它在所有硬件上移动速度都一样。
    // 图形程序和游戏通常会跟踪一个时间差(Deltatime)变量，它储存了渲染上一帧所用的时间。
    // 我们把所有速度都去乘以deltaTime值。
    // 结果就是，如果我们的deltaTime很大，就意味着上一帧的渲染花费了更多时间，
    // 所以这一帧的速度需要变得更高来平衡渲染所花去的时间。
    // 使用这种方法时，无论你的电脑快还是慢，摄像机的速度都会相应平衡，这样每个用户的体验就都一样了。
    float deltaTime = 0.0f;	// 当前帧与上一帧的时间差
    float lastFrame = 0.0f; // 上一帧的时间
    
    // 上一次鼠标的位置，默认是屏幕中心
    float lastX = 400;
    float lastY = 300;
    
    float yaw = -90.0f;
    float pitch = 0.0f;
    float fov = 45.0f;
    
    bool firstMouse = true;
    
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
    	// 原教程是FPS风格的摄像机，不需要按鼠标右键，只要转动鼠标就能转换视角
    	// 程序运行时如果鼠标在窗体外面，再进入窗体时会有一个视角抖动
    	// firstMouse主要用来消除这个抖动
    	// 我们将FPS风格的摄像机改为RPG风格的摄像机
    	// 不存在鼠标进入窗体导致视角抖动的情况
    	// firstMouse是可以没有的
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
    
    	// 启用深度测试
    	glEnable(GL_DEPTH_TEST);
    
    	// 首先，让我们为每个立方体定义一个位移向量来指定它在世界空间的位置
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
    
    	// 使用纹理
    	// 首先定义包含纹理坐标的顶点数组
    	// 绘制立方体需要36个坐标点
    	float vertices[] = {
    		//     ---- 位置 ----     - 纹理坐标 -
    		-0.5f, -0.5f, -0.5f,  0.0f, 0.0f,
    		0.5f, -0.5f, -0.5f,  1.0f, 0.0f,
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f,
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f,
    		-0.5f,  0.5f, -0.5f,  0.0f, 1.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f, 0.0f,
    
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f,
    		0.5f, -0.5f,  0.5f,  1.0f, 0.0f,
    		0.5f,  0.5f,  0.5f,  1.0f, 1.0f,
    		0.5f,  0.5f,  0.5f,  1.0f, 1.0f,
    		-0.5f,  0.5f,  0.5f,  0.0f, 1.0f,
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f,
    
    		-0.5f,  0.5f,  0.5f,  1.0f, 0.0f,
    		-0.5f,  0.5f, -0.5f,  1.0f, 1.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f,
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f,
    		-0.5f,  0.5f,  0.5f,  1.0f, 0.0f,
    
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f,
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f,
    		0.5f, -0.5f, -0.5f,  0.0f, 1.0f,
    		0.5f, -0.5f, -0.5f,  0.0f, 1.0f,
    		0.5f, -0.5f,  0.5f,  0.0f, 0.0f,
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f,
    
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f,
    		0.5f, -0.5f, -0.5f,  1.0f, 1.0f,
    		0.5f, -0.5f,  0.5f,  1.0f, 0.0f,
    		0.5f, -0.5f,  0.5f,  1.0f, 0.0f,
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f,
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f,
    
    		-0.5f,  0.5f, -0.5f,  0.0f, 1.0f,
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f,
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f,
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f,
    		-0.5f,  0.5f,  0.5f,  0.0f, 0.0f,
    		-0.5f,  0.5f, -0.5f,  0.0f, 1.0f
    	};
    
    	unsigned int VBO;
    	unsigned int VAO;
    
    	// 创建一个内存缓冲对象
    	glGenBuffers(1, &VBO);
    	// 创建一个顶点数组对象
    	glGenVertexArrays(1, &VAO);
    
    	// 首先绑定顶点数组对象，，。
    	glBindVertexArray(VAO);
    
    	// 然后将内存对象绑定为顶点缓冲对象
    	glBindBuffer(GL_ARRAY_BUFFER, VBO);
    	// 向缓冲内存写入数据
    	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    
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
    
    	// 创建渲染循环
    	while (!glfwWindowShouldClose(window))
    	{
    		float currentFrame = glfwGetTime();
    		deltaTime = currentFrame - lastFrame;
    		lastFrame = currentFrame;
    
    		// 处理输入事件
    		processInput(window);
    
    		// 清空背景颜色
    		// 当调用glClear函数，清除颜色缓冲之后，
    		// 整个颜色缓冲都会被填充为glClearColor里所设置的颜色
    		// 在这里，我们将屏幕设置为了类似黑板的深蓝绿色
    		glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
    		// 由于我们使用了深度测试，所以需要再与上一个GL_DEPTH_BUFFER_BIT清楚深度缓冲
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
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
    
    		// 观察矩阵
    		glm::mat4 view(1.0f);
    		// 关于参数2，这里应该是观察位置
    		// 由于本例中的摄像机的位置是会变化的
    		// 如果向之前一样只设置位置
    		// 那么当摄像机移动后，摄像机会永远对着目标向量
    		// 而加上方向向量后，不管摄像机怎么移动，都会对着方向向量的方向，这样才会有平移的效果
    		view = glm::lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
    	//	view = glm::lookAt(glm::vec3(0.0, 0.0, 6.0), glm::vec3(1.0, 0.0, 3.0), glm::vec3(0.0, 1.0, 0.0));
    
    		// 最后需要一个投影矩阵
    		glm::mat4 projection(1.0f);
    		// 第一个参数定义了我们可以看到的视野范围
    		// 当视野变小时，场景投影出来的空间就会减小，产生放大(Zoom In)了的感觉
    		projection = glm::perspective(glm::radians(fov), 800.0f / 600.0f, 0.1f, 100.0f);
    	//	projection = glm::perspective(glm::radians(45.0f), 800.0f / 600.0f, 0.1f, 100.0f);
    
    		glUseProgram(shaderProgram);
    		// 每个矩阵对应一个uniform，这里是将矩阵赋值给着色器的uniform
    		int modelView = glGetUniformLocation(shaderProgram, "view");
    		glUniformMatrix4fv(modelView, 1, GL_FALSE, glm::value_ptr(view));
    		int modelProj = glGetUniformLocation(shaderProgram, "projection");
    		glUniformMatrix4fv(modelProj, 1, GL_FALSE, glm::value_ptr(projection));
    
    		glBindVertexArray(VAO);
    		for (unsigned int i = 0; i < 10; i++)
    		{
    			// 创建模型矩阵，并使用位移向量数组的数据进行位移
    			glm::mat4 model(1.0f);
    			model = glm::translate(model, cubePositions[i]);
    			// 旋转
    			float angle = 20.0f * i;
    		//	model = glm::rotate(model, glm::radians(angle), glm::vec3(1.0f, 0.3f, 0.5f));
    			model = glm::rotate(model, (float)glfwGetTime() * glm::radians(angle), glm::vec3(1.0f, 0.3f, 0.5f));
    
    			// 将矩阵赋值给着色器的uniform
    			glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "model"), 1, GL_FALSE, glm::value_ptr(model));
    
    			glDrawArrays(GL_TRIANGLES, 0, 36);
    		}
    
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
    

* content
{:toc}


