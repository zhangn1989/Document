---
layout: post
title: OpenGL学习笔记：模版测试
date: 发布于2019-09-11 18:31:06 +0800
categories: OpenGL学习笔记
tag: 4
---

* content
{:toc}

模版测试的作用就是给我们提供一种可以控制片段绘制的方法，让我们的绘图更为灵活。本节中绘制边框的例子的设计思想也很容易理解，具体可以看下面代码的中文注释。  
<!-- more -->

原版教程中有这么一句话：“我们将模板函数设置为GL_NOTEQUAL，它会保证我们只绘制箱子上模板值不为1的部分，即只绘制箱子在之前绘制的箱子之外的部分。注意我们也禁用了深度测试，让放大的箱子，即边框，不会被地板所覆盖。”  
他的想法我理解，可为什么能达到这个效果呢？想了好久，又翻了翻以前的章节，总算是想明白了，顺便想明白了之前不明白的一些问题。  
原版教程在创建窗口章节介绍了渲染循环，每次绘图都会更新颜色缓冲，每次循环都要清除上一次绘图的痕迹，否则会一直在。三角形章节介绍了渲染管线，我们知道了光栅器会把集合着色器生成的图元光栅化，生成片段，每一个片段都是渲染一个像素的数据集合。同时介绍了glDrawArrays函数，每执行一次该函数就会画一次图。在坐标系章节中，我们知道了光栅器工作在视口变换(Viewport
Transform)之后的，也就是说在光栅器生成片段时，已经确定每个片段所渲染的是屏幕上的哪个点了。  
在深度测试章节，我们知道了每个片段中都有一个深度值，还知道了有一个深度缓冲记录着每个被绘制的片段的深度值。当图像绘制的时候，会用本次绘图的片段的深度值和该片段所对应的像素点的深度缓冲值对比，对比通过就用当前片段覆盖之前的片段，同时更新该像素的深度缓冲值。  
回顾深度缓冲的程序，在渲染循环中，我们首先要设置一个背景颜色，然后就是清空颜色缓存和深度缓存。在我们第一次使用glDrawArrays绘制箱子时，颜色缓存和深度缓存都是空的，一定会通过测试，当绘图结束时，箱子所在的像素所对应的颜色缓存和深度缓存被更新  
第二次使用glDrawArrays绘制第二个箱子时，由于我们没有清空颜色和深度缓存，也没有设置背景颜色，同时也没有和第一次绘制的箱子有像素重叠，因此第一个箱子所在的像素点的缓存信息没有变，只是更新了第二个箱子对应的像素点的缓存信息。  
第三次使用glDrawArrays绘制地板时，没有重叠的部分同第二个箱子一样，有重叠的部分会用地板的片段的深度值和缓存中的深度值进行比较，如果比较通过就绘制更新，不通过就会被抛弃  
这里要注意，片段的深度值是包含在片段信息内的，缓冲深度值是用来标识像素的，虽然说每个片段都是一个像素的数据集合，但是像素的数据是真的被绘制到屏幕上了，而片段的数据则不一定，所以不能把片段和像素完全等价看待  
模版测试略微不同，片段中并没有一个叫做模版值的数据，我们比较的时候也并没有从片段中取数据，而用我们设置的一个参考值。我们可以把模版缓冲理解成一个和屏幕对应的二维数组，这个二维数组就想是一个模版一样罩在屏幕上，每个像素就是缓冲数据，控制着本次绘图时要不要绘制其对应的像素  
在下面的代码中，我们首先打开了模版测试，然后设置所有比较都通过，并设置参考值为1。在渲染循环中，首先绘制了地板，并设置了模版掩码为0，原版教程的代码中虽然注释的内容是禁止更新缓冲，其实并不是不向缓冲中写数据，而是会将所有写入的数据在写入之前都会先和0与，再将结果写入，也就是说，当地板被绘制的时候，地板所对应的所有像素点的模版缓冲值都是0  
然后是绘制两个箱子，和深度测试一样，由于我们没有清空各种缓存数据，地板的信息只有与箱子覆盖的位置才会被更新，其他位置会被保留。也就是说，当绘制完箱子后，我们理解的那个二维数组中，箱子所对应的像素的模版缓冲值是1，其他像素的模版缓冲值是0  
接下来是绘制边框，我们首先设置测试条件是模版缓冲值不等于1，也就是说，本次绘图的时候，二维数组中的所有值为1的元素所对应的像素都不会被绘制，由于我们也没有清空缓存数据，所以之前绘制的箱子还在，并没有被覆盖掉。我们实际上并不是给箱子进行描边，而画了一个比箱子更大的立方体，只不过在渲染的时候，与箱子重合的部分被丢弃了，造成一种绘制边框的效果

    
    
    #include <glad/glad.h>
    #include <GLFW/glfw3.h>
    
    #include <stb_image.h>
    
    #include <glm/glm.hpp>
    #include <glm/gtc/matrix_transform.hpp>
    #include <glm/gtc/type_ptr.hpp>
    
    #include <shader.h>
    #include <camera.h>
    #include <model.h>
    
    #include <iostream>
    
    #include <windows.h>
    
    const char *vertexShaderSource = R"1234(#version 330 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec2 aTexCoords;
    
    out vec2 TexCoords;
    
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    
    void main()
    {
        TexCoords = aTexCoords;    
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }
    )1234";
    
    const char *fragmentShaderSource = R"1234(#version 330 core
    out vec4 FragColor;
    
    in vec2 TexCoords;
    
    uniform sampler2D texture1;
    
    void main()
    {    
    	 //FragColor = vec4(vec3(gl_FragCoord.z), 1.0);
       FragColor = texture(texture1, TexCoords);
    }
    )1234";
    
    const char *singleColorShaderSource = R"1234(#version 330 core
    out vec4 FragColor;
    void main()
    {
        FragColor = vec4(0.04, 0.28, 0.26, 1.0);
    }
    )1234";
    
    
    void framebuffer_size_callback(GLFWwindow* window, int width, int height);
    void mouse_callback(GLFWwindow* window, double xpos, double ypos);
    void scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
    void processInput(GLFWwindow *window);
    unsigned int loadTexture(const char *path);
    
    // settings
    const unsigned int SCR_WIDTH = 1280;
    const unsigned int SCR_HEIGHT = 720;
    
    // camera
    Camera camera(glm::vec3(0.0f, 0.0f, 3.0f));
    float lastX = (float)SCR_WIDTH / 2.0;
    float lastY = (float)SCR_HEIGHT / 2.0;
    bool firstMouse = true;
    
    // timing
    float deltaTime = 0.0f;
    float lastFrame = 0.0f;
    
    int main()
    {
    	// glfw: initialize and configure
    	// ------------------------------
    	glfwInit();
    	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    
    #ifdef __APPLE__
    	glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // uncomment this statement to fix compilation on OS X
    #endif
    
    														 // glfw window creation
    														 // --------------------
    	GLFWwindow* window = glfwCreateWindow(SCR_WIDTH, SCR_HEIGHT, "LearnOpenGL", NULL, NULL);
    	if (window == NULL)
    	{
    		std::cout << "Failed to create GLFW window" << std::endl;
    		glfwTerminate();
    		return -1;
    	}
    	glfwMakeContextCurrent(window);
    	glfwSetFramebufferSizeCallback(window, framebuffer_size_callback);
    	glfwSetCursorPosCallback(window, mouse_callback);
    	glfwSetScrollCallback(window, scroll_callback);
    
    	// tell GLFW to capture our mouse
    //	glfwSetInputMode(window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    
    	// glad: load all OpenGL function pointers
    	// ---------------------------------------
    	if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
    	{
    		std::cout << "Failed to initialize GLAD" << std::endl;
    		return -1;
    	}
    
    	// configure global opengl state
    	// -----------------------------
    	glEnable(GL_DEPTH_TEST);
    	glDepthFunc(GL_LESS); // always pass the depth test (same effect as glDisable(GL_DEPTH_TEST))
    
    	// 首先启用模版测试
    	// 将模版测试和深度测试都通过的片段的模版缓冲设置为1
    	glEnable(GL_STENCIL_TEST);
    	glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);
    	glStencilFunc(GL_ALWAYS, 1, 0xFF); 
    
    	// build and compile shaders
    	// -------------------------
    	Shader shader(vertexShaderSource, fragmentShaderSource);
    	Shader shaderSingleColor(vertexShaderSource, singleColorShaderSource);
    
    	shaderSingleColor.use();
    
    	// set up vertex data (and buffer(s)) and configure vertex attributes
    	// ------------------------------------------------------------------
    	float cubeVertices[] = {
    		// positions          // texture Coords
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
    	float planeVertices[] = {
    		// positions          // texture Coords (note we set these higher than 1 (together with GL_REPEAT as texture wrapping mode). this will cause the floor texture to repeat)
    		5.0f, -0.5f,  5.0f,  2.0f, 0.0f,
    		-5.0f, -0.5f,  5.0f,  0.0f, 0.0f,
    		-5.0f, -0.5f, -5.0f,  0.0f, 2.0f,
    
    		5.0f, -0.5f,  5.0f,  2.0f, 0.0f,
    		-5.0f, -0.5f, -5.0f,  0.0f, 2.0f,
    		5.0f, -0.5f, -5.0f,  2.0f, 2.0f
    	};
    	// cube VAO
    	unsigned int cubeVAO, cubeVBO;
    	glGenVertexArrays(1, &cubeVAO);
    	glGenBuffers(1, &cubeVBO);
    	glBindVertexArray(cubeVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, cubeVBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(cubeVertices), &cubeVertices, GL_STATIC_DRAW);
    	glEnableVertexAttribArray(0);
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(1);
    	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    	glBindVertexArray(0);
    	// plane VAO
    	unsigned int planeVAO, planeVBO;
    	glGenVertexArrays(1, &planeVAO);
    	glGenBuffers(1, &planeVBO);
    	glBindVertexArray(planeVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, planeVBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(planeVertices), &planeVertices, GL_STATIC_DRAW);
    	glEnableVertexAttribArray(0);
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(1);
    	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    	glBindVertexArray(0);
    
    	// load textures
    	// -------------
    	unsigned int cubeTexture = loadTexture("marble.jpg");
    	unsigned int floorTexture = loadTexture("metal.png");
    
    	// shader configuration
    	// --------------------
    	shader.use();
    	shader.setInt("texture1", 0);
    
    	// render loop
    	// -----------
    	while (!glfwWindowShouldClose(window))
    	{
    		// per-frame time logic
    		// --------------------
    		float currentFrame = glfwGetTime();
    		deltaTime = currentFrame - lastFrame;
    		lastFrame = currentFrame;
    
    		// input
    		// -----
    		processInput(window);
    
    		// render
    		// ------
    		glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT); // don't forget to clear the stencil buffer!
    
    																					// set uniforms
    		shaderSingleColor.use();
    		glm::mat4 model = glm::mat4(1.0f);
    		glm::mat4 view = camera.GetViewMatrix();
    		glm::mat4 projection = glm::perspective(glm::radians(camera.Zoom), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 100.0f);
    		shaderSingleColor.setMat4("view", view);
    		shaderSingleColor.setMat4("projection", projection);
    
    		shader.use();
    		shader.setMat4("view", view);
    		shader.setMat4("projection", projection);
    
    		// 本例中我们不对地板进行模版测试，这里先把地板画出来
    		// 在此之前，设置缓冲掩码为0，前面设置了永远通过测试
    		// 在绘图的时候，会用前面设置参考值1去更新缓冲值
    		// 但由于设置了缓冲掩码为0，所以实际上会将地板的所有缓冲值都置0
    		glStencilMask(0x00);
    		// floor
    		glBindVertexArray(planeVAO);
    		glBindTexture(GL_TEXTURE_2D, floorTexture);
    		shader.setMat4("model", glm::mat4(1.0f));
    		glDrawArrays(GL_TRIANGLES, 0, 6);
    		glBindVertexArray(0);
    
    		// 接下来是正常绘制需要进行模版测试的物体
    		// 在绘制之前，先配置模版测试为永远通过
    		// 然后打开刚刚禁用掉的模版缓冲写入
    		// 接着是正常绘制物体，在此过程中会重新向模版缓冲写入1
    		glStencilFunc(GL_ALWAYS, 1, 0xFF);
    		glStencilMask(0xFF);
    		// cubes
    		glBindVertexArray(cubeVAO);
    		glActiveTexture(GL_TEXTURE0);
    		glBindTexture(GL_TEXTURE_2D, cubeTexture);
    		model = glm::translate(model, glm::vec3(-1.0f, 0.0f, -1.0f));
    		shader.setMat4("model", model);
    		glDrawArrays(GL_TRIANGLES, 0, 36);
    		model = glm::mat4(1.0f);
    		model = glm::translate(model, glm::vec3(2.0f, 0.0f, 0.0f));
    		shader.setMat4("model", model);
    		glDrawArrays(GL_TRIANGLES, 0, 36);
    
    		// 下面是绘制边框
    		// 首先设置模版缓冲不等于1的时候通过测试
    		// 然后禁用写入模版缓冲，关闭模版测试
    		// 接下来将物体放大一点，再用纯色绘制一遍
    		// 绘制完就可以打开缓冲写入，启用模版测试
    		// 这里就有一个疑问了
    		// 根据程序的设计思想，应该是想做这么一件事
    		// 首先正常绘制物体，并将模版缓冲全部置1
    		// 然后再将物体放大一点，纹理设置为纯色
    		// 当绘制时，将原物体和这个放大后的纯色物体的片段进行比较
    		// 和原物体重叠的部分不绘制，不重叠的部分绘制
    		// 从而达到为原物体绘制边框的目的
    		// 经过之前的绘制，地板的缓冲值为0，箱子的缓冲值为1
    		// 在渲染边框时，由于设置的条件是不等于1的缓冲通过测试
    		// 而前面只有绘制箱子的像素点的缓冲是1，无法通过测试
    		// 所以边框与箱子重合的部分会被抛弃
    		// 而之前绘制的箱子又没有被清空，所以会产生边框效果
    		// 此次绘图之后，原来缓冲值为0能通过测试的部分的缓冲值会被更新
    		// 但由于我们设置的更新掩码是0，所以更新后的数据还是0
    		// 原来缓冲值为1的部分没有通过测试，不会被更新，所以还是1
    		// 也就是说，此次绘图结束后，测试用的模版并没有变化
    		glStencilFunc(GL_NOTEQUAL, 1, 0xFF);
    		glStencilMask(0x00);
    		glDisable(GL_DEPTH_TEST);
    		shaderSingleColor.use();
    		float scale = 1.1;
    		// cubes
    		glBindVertexArray(cubeVAO);
    		glBindTexture(GL_TEXTURE_2D, cubeTexture);
    		model = glm::mat4(1.0f);
    		model = glm::translate(model, glm::vec3(-1.0f, 0.0f, -1.0f));
    		model = glm::scale(model, glm::vec3(scale, scale, scale));
    		shaderSingleColor.setMat4("model", model);
    		glDrawArrays(GL_TRIANGLES, 0, 36);
    		model = glm::mat4(1.0f);
    		model = glm::translate(model, glm::vec3(2.0f, 0.0f, 0.0f));
    		model = glm::scale(model, glm::vec3(scale, scale, scale));
    		shaderSingleColor.setMat4("model", model);
    		glDrawArrays(GL_TRIANGLES, 0, 36);
    		glBindVertexArray(0);
    		glStencilMask(0xFF);
    		glEnable(GL_DEPTH_TEST);
    
    		// glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
    		// -------------------------------------------------------------------------------
    		glfwSwapBuffers(window);
    		glfwPollEvents();
    		Sleep(100);
    	}
    
    	// optional: de-allocate all resources once they've outlived their purpose:
    	// ------------------------------------------------------------------------
    	glDeleteVertexArrays(1, &cubeVAO);
    	glDeleteVertexArrays(1, &planeVAO);
    	glDeleteBuffers(1, &cubeVBO);
    	glDeleteBuffers(1, &planeVBO);
    
    	glfwTerminate();
    	return 0;
    }
    
    // process all input: query GLFW whether relevant keys are pressed/released this frame and react accordingly
    // ---------------------------------------------------------------------------------------------------------
    void processInput(GLFWwindow *window)
    {
    	if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS)
    		glfwSetWindowShouldClose(window, true);
    
    	if (glfwGetKey(window, GLFW_KEY_W) == GLFW_PRESS)
    		camera.ProcessKeyboard(FORWARD, deltaTime);
    	if (glfwGetKey(window, GLFW_KEY_S) == GLFW_PRESS)
    		camera.ProcessKeyboard(BACKWARD, deltaTime);
    	if (glfwGetKey(window, GLFW_KEY_A) == GLFW_PRESS)
    		camera.ProcessKeyboard(LEFT, deltaTime);
    	if (glfwGetKey(window, GLFW_KEY_D) == GLFW_PRESS)
    		camera.ProcessKeyboard(RIGHT, deltaTime);
    }
    
    // glfw: whenever the window size changed (by OS or user resize) this callback function executes
    // ---------------------------------------------------------------------------------------------
    void framebuffer_size_callback(GLFWwindow* window, int width, int height)
    {
    	// make sure the viewport matches the new window dimensions; note that width and 
    	// height will be significantly larger than specified on retina displays.
    	glViewport(0, 0, width, height);
    }
    
    // glfw: whenever the mouse moves, this callback is called
    // -------------------------------------------------------
    void mouse_callback(GLFWwindow* window, double xpos, double ypos)
    {
    	if (firstMouse)
    	{
    		lastX = xpos;
    		lastY = ypos;
    		firstMouse = false;
    	}
    
    	float xoffset = xpos - lastX;
    	float yoffset = lastY - ypos; // reversed since y-coordinates go from bottom to top
    
    	lastX = xpos;
    	lastY = ypos;
    
    	if (glfwGetMouseButton(window, GLFW_MOUSE_BUTTON_RIGHT) == GLFW_PRESS)
    		camera.ProcessMouseMovement(xoffset, yoffset);
    }
    
    // glfw: whenever the mouse scroll wheel scrolls, this callback is called
    // ----------------------------------------------------------------------
    void scroll_callback(GLFWwindow* window, double xoffset, double yoffset)
    {
    	camera.ProcessMouseScroll(yoffset);
    }
    
    // utility function for loading a 2D texture from file
    // ---------------------------------------------------
    unsigned int loadTexture(char const *path)
    {
    	unsigned int textureID;
    	glGenTextures(1, &textureID);
    
    	int width, height, nrComponents;
    	unsigned char *data = stbi_load(path, &width, &height, &nrComponents, 0);
    	if (data)
    	{
    		GLenum format;
    		if (nrComponents == 1)
    			format = GL_RED;
    		else if (nrComponents == 3)
    			format = GL_RGB;
    		else if (nrComponents == 4)
    			format = GL_RGBA;
    
    		glBindTexture(GL_TEXTURE_2D, textureID);
    		glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, data);
    		glGenerateMipmap(GL_TEXTURE_2D);
    
    		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
    		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    
    		stbi_image_free(data);
    	}
    	else
    	{
    		std::cout << "Texture failed to load at path: " << path << std::endl;
    		stbi_image_free(data);
    	}
    
    	return textureID;
    }
    

