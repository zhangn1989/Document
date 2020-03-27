---
layout: post
title: OpenGL学习笔记：帧缓冲
date: 发布于2019-09-17 17:36:17 +0800
categories: OpenGL学习笔记
tag: 4
---

* content
{:toc}

这节课很好理解，需要注意的是，在向自定义的帧缓冲中写如像素数据的时候，数据会被写入到帧缓冲的纹理附件中。  

<!-- more -->
在本节课的示例程序中，先在自定义的帧缓冲上绘制地板箱子等图像，后在默认缓冲上画了一个覆盖全屏幕的矩形。正常的图形写入到帧缓冲，然后从纹理附件中读取数据，将原图像以纹理的形式贴在默认缓冲的矩形上，并且可以在这个过程中进行图像修改，默认缓冲的矩形就类似于滤镜的作用

    
    
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
        FragColor = texture(texture1, TexCoords);
    }
    )1234";
    
    const char *screenVertexShaderSource = R"1234(#version 330 core
    layout (location = 0) in vec2 aPos;
    layout (location = 1) in vec2 aTexCoords;
    
    out vec2 TexCoords;
    
    void main()
    {
        TexCoords = aTexCoords;
        gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0); 
    }  
    )1234";
    
    const char *screenFragmentShaderSource = R"1234(#version 330 core
    out vec4 FragColor;
    
    in vec2 TexCoords;
    
    uniform sampler2D screenTexture;
    
    void main()
    {
        vec3 col = texture(screenTexture, TexCoords).rgb;
        FragColor = vec4(col, 1.0);
    	FragColor = vec4(vec3(1.0 - texture(screenTexture, TexCoords)), 1.0);
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
    	glEnable(GL_CULL_FACE);
    	glFrontFace(GL_CCW);
    	// build and compile shaders
    	// -------------------------
    	Shader shader(vertexShaderSource, fragmentShaderSource);
    	Shader screenShader(screenVertexShaderSource, screenFragmentShaderSource);
    
    	// set up vertex data (and buffer(s)) and configure vertex attributes
    	// ------------------------------------------------------------------
    	float cubeVertices[] = {
    		// Back face
    		-0.5f, -0.5f, -0.5f,  0.0f, 0.0f, // Bottom-left
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f, // top-right
    		0.5f, -0.5f, -0.5f,  1.0f, 0.0f, // bottom-right         
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f, // top-right
    		-0.5f, -0.5f, -0.5f,  0.0f, 0.0f, // bottom-left
    		-0.5f,  0.5f, -0.5f,  0.0f, 1.0f, // top-left
    		// Front face
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f, // bottom-left
    		0.5f, -0.5f,  0.5f,  1.0f, 0.0f, // bottom-right
    		0.5f,  0.5f,  0.5f,  1.0f, 1.0f, // top-right
    		0.5f,  0.5f,  0.5f,  1.0f, 1.0f, // top-right
    		-0.5f,  0.5f,  0.5f,  0.0f, 1.0f, // top-left
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f, // bottom-left
    		// Left face
    		-0.5f,  0.5f,  0.5f,  1.0f, 0.0f, // top-right
    		-0.5f,  0.5f, -0.5f,  1.0f, 1.0f, // top-left
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f, // bottom-left
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f, // bottom-left
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f, // bottom-right
    		-0.5f,  0.5f,  0.5f,  1.0f, 0.0f, // top-right
    		// Right face
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f, // top-left
    		0.5f, -0.5f, -0.5f,  0.0f, 1.0f, // bottom-right
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f, // top-right         
    		0.5f, -0.5f, -0.5f,  0.0f, 1.0f, // bottom-right
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f, // top-left
    		0.5f, -0.5f,  0.5f,  0.0f, 0.0f, // bottom-left     
    		// Bottom face
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f, // top-right
    		0.5f, -0.5f, -0.5f,  1.0f, 1.0f, // top-left
    		0.5f, -0.5f,  0.5f,  1.0f, 0.0f, // bottom-left
    		0.5f, -0.5f,  0.5f,  1.0f, 0.0f, // bottom-left
    		-0.5f, -0.5f,  0.5f,  0.0f, 0.0f, // bottom-right
    		-0.5f, -0.5f, -0.5f,  0.0f, 1.0f, // top-right
    		// Top face
    		-0.5f,  0.5f, -0.5f,  0.0f, 1.0f, // top-left
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f, // bottom-right
    		0.5f,  0.5f, -0.5f,  1.0f, 1.0f, // top-right     
    		0.5f,  0.5f,  0.5f,  1.0f, 0.0f, // bottom-right
    		-0.5f,  0.5f, -0.5f,  0.0f, 1.0f, // top-left
    		-0.5f,  0.5f,  0.5f,  0.0f, 0.0f  // bottom-left        
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
    
    	float quadVertices[] = {
    		// positions   // texCoords
    		-1.0f,  1.0f,  0.0f, 1.0f,
    		-1.0f, -1.0f,  0.0f, 0.0f,
    		1.0f, -1.0f,  1.0f, 0.0f,
    
    		-1.0f,  1.0f,  0.0f, 1.0f,
    		1.0f, -1.0f,  1.0f, 0.0f,
    		1.0f,  1.0f,  1.0f, 1.0f
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
    
    	// screen quad VAO
    	unsigned int quadVAO, quadVBO;
    	glGenVertexArrays(1, &quadVAO);
    	glGenBuffers(1, &quadVBO);
    	glBindVertexArray(quadVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, quadVBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(quadVertices), &quadVertices, GL_STATIC_DRAW);
    	glEnableVertexAttribArray(0);
    	glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(1);
    	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 4 * sizeof(float), (void*)(2 * sizeof(float)));
    
    	// load textures
    	// -------------
    	unsigned int cubeTexture = loadTexture("container.jpg");
    	unsigned int floorTexture = loadTexture("metal.png");
    
    	// shader configuration
    	// --------------------
    	shader.use();
    	shader.setInt("texture1", 0);
    
    	screenShader.use();
    	screenShader.setInt("screenTexture", 0);
    
    
    	unsigned int framebuffer;
    	glGenFramebuffers(1, &framebuffer);
    	glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    
    	// 生成纹理
    	unsigned int textureColorbuffer;
    	glGenTextures(1, &textureColorbuffer);
    	glBindTexture(GL_TEXTURE_2D, textureColorbuffer);
    	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 800, 600, 0, GL_RGB, GL_UNSIGNED_BYTE, NULL);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    	glBindTexture(GL_TEXTURE_2D, 0);
    
    	// 将它附加到当前绑定的帧缓冲对象
    	glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, textureColorbuffer, 0);
    
    	unsigned int rbo;
    	glGenRenderbuffers(1, &rbo);
    	glBindRenderbuffer(GL_RENDERBUFFER, rbo);
    	glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 800, 600);
    	glBindRenderbuffer(GL_RENDERBUFFER, 0);
    
    	glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);
    
    	if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
    		std::cout << "ERROR::FRAMEBUFFER:: Framebuffer is not complete!" << std::endl;
    	glBindFramebuffer(GL_FRAMEBUFFER, 0);
    
    
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
    		// 第一处理阶段(Pass)
    		glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    		glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); // 我们现在不使用模板缓冲
    		glEnable(GL_DEPTH_TEST);
    
    		glm::mat4 model = glm::mat4(1.0f);
    		glm::mat4 view = camera.GetViewMatrix();
    		glm::mat4 projection = glm::perspective(glm::radians(camera.Zoom), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 100.0f);
    
    		shader.use();
    		shader.setMat4("view", view);
    		shader.setMat4("projection", projection);
    
    		// floor
    		glCullFace(GL_FRONT);
    		glBindVertexArray(planeVAO);
    		glBindTexture(GL_TEXTURE_2D, floorTexture);
    		shader.setMat4("model", glm::mat4(1.0f));
    		glDrawArrays(GL_TRIANGLES, 0, 6);
    
    		// cubes
    		glCullFace(GL_BACK);
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
    
    		// 第二处理阶段
    		glBindFramebuffer(GL_FRAMEBUFFER, 0); // 返回默认
    		glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
    		glClear(GL_COLOR_BUFFER_BIT);
    
    		screenShader.use();
    		glBindVertexArray(quadVAO);
    		glDisable(GL_DEPTH_TEST);
    		glBindTexture(GL_TEXTURE_2D, textureColorbuffer);
    		glDrawArrays(GL_TRIANGLES, 0, 6);
    
    		// glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
    		// -------------------------------------------------------------------------------
    		glfwSwapBuffers(window);
    		glfwPollEvents();
    		Sleep(100);
    	}
    
    	// optional: de-allocate all resources once they've outlived their purpose:
    	// ------------------------------------------------------------------------
    	glDeleteFramebuffers(1, &framebuffer);
    	glDeleteVertexArrays(1, &cubeVAO);
    	glDeleteVertexArrays(1, &planeVAO);
    	glDeleteVertexArrays(1, &quadVAO);
    	glDeleteBuffers(1, &cubeVBO);
    	glDeleteBuffers(1, &planeVBO);
    	glDeleteBuffers(1, &quadVBO);
    
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
    
    		// 消除小草的边框
    		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, format == GL_RGBA ? GL_CLAMP_TO_EDGE : GL_REPEAT); // for this tutorial: use GL_CLAMP_TO_EDGE to prevent semi-transparent borders. Due to interpolation it takes texels from next repeat 
    		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, format == GL_RGBA ? GL_CLAMP_TO_EDGE : GL_REPEAT);
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
    
    

