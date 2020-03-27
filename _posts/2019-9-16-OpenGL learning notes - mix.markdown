---
layout: post
title: OpenGL学习笔记：混合
date: 发布于2019-09-16 16:00:03 +0800
categories: OpenGL学习笔记
tag: 4
---

# 丢弃片段

* content
{:toc}


第一种混合的方法很简单，直接将alpha值为0的片段丢弃即可，这个可以在片段着色器中进行简单处理，需要注意的是，当采样纹理的边缘的时候，OpenGL会对边缘的值和纹理下一个重复的值进行插值（因为我们将它的环绕方式设置为了GL_REPEAT。这通常是没问题的，但是由于我们使用了透明值，纹理图像的顶部将会与底部边缘的纯色值进行插值。这样的结果是一个半透明的有色边框，你可能会看见它环绕着你的纹理四边形。要想避免这个，每当你alpha纹理的时候，请将纹理的环绕方式设置为GL_CLAMP_TO_EDGE  
<!-- more -->

完整代码

    
    
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
    //   FragColor = texture(texture1, TexCoords);
        vec4 texColor = texture(texture1, TexCoords);
        if(texColor.a < 0.1)
            discard;
        FragColor = texColor;
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
    
    	// build and compile shaders
    	// -------------------------
    	Shader shader(vertexShaderSource, fragmentShaderSource);
    
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
    
    	float transparentVertices[] = {
    		// positions         // texture Coords (swapped y coordinates because texture is flipped upside down)
    		0.0f,  0.5f,  0.0f,  0.0f,  0.0f,
    		0.0f, -0.5f,  0.0f,  0.0f,  1.0f,
    		1.0f, -0.5f,  0.0f,  1.0f,  1.0f,
    
    		0.0f,  0.5f,  0.0f,  0.0f,  0.0f,
    		1.0f, -0.5f,  0.0f,  1.0f,  1.0f,
    		1.0f,  0.5f,  0.0f,  1.0f,  0.0f
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
    
    	// transparent VAO
    	unsigned int transparentVAO, transparentVBO;
    	glGenVertexArrays(1, &transparentVAO);
    	glGenBuffers(1, &transparentVBO);
    	glBindVertexArray(transparentVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, transparentVBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(transparentVertices), transparentVertices, GL_STATIC_DRAW);
    	glEnableVertexAttribArray(0);
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(1);
    	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    	glBindVertexArray(0);
    
    	// load textures
    	// -------------
    	unsigned int cubeTexture = loadTexture("marble.jpg");
    	unsigned int floorTexture = loadTexture("metal.png");
    	unsigned int transparentTexture = loadTexture("grass.png");
    
    	std::vector<glm::vec3> vegetation
    	{
    		glm::vec3(-1.5f, 0.0f, -0.48f),
    		glm::vec3(1.5f, 0.0f, 0.51f),
    		glm::vec3(0.0f, 0.0f, 0.7f),
    		glm::vec3(-0.3f, 0.0f, -2.3f),
    		glm::vec3(0.5f, 0.0f, -0.6f)
    	};
    
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
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); // don't forget to clear the stencil buffer!
    
    
    		glm::mat4 model = glm::mat4(1.0f);
    		glm::mat4 view = camera.GetViewMatrix();
    		glm::mat4 projection = glm::perspective(glm::radians(camera.Zoom), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 100.0f);
    
    		shader.use();
    		shader.setMat4("view", view);
    		shader.setMat4("projection", projection);
    
    		// floor
    		glBindVertexArray(planeVAO);
    		glBindTexture(GL_TEXTURE_2D, floorTexture);
    		shader.setMat4("model", glm::mat4(1.0f));
    		glDrawArrays(GL_TRIANGLES, 0, 6);
    
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
    
    		// vegetation
    		glBindVertexArray(transparentVAO);
    		glBindTexture(GL_TEXTURE_2D, transparentTexture);
    		for (GLuint i = 0; i < vegetation.size(); i++)
    		{
    			model = glm::mat4(1.0f);
    			model = glm::translate(model, vegetation[i]);
    			shader.setMat4("model", model);
    			glDrawArrays(GL_TRIANGLES, 0, 6);
    		}
    
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
    

# 混合

混合的颜色计算公式也很好理解，这里需要注意的是颜色混合会和深度测试冲突，需要我们手动调整绘图顺出，防止某些片段别深度测试抛弃。当绘制一个有不透明和透明物体的场景的时候，大体的原则如下：

  1. 先绘制所有不透明的物体。
  2. 对所有透明的物体排序。
  3. 按顺序绘制所有透明的物体。

    
    
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
    
    	glEnable(GL_BLEND);
    	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    	// build and compile shaders
    	// -------------------------
    	Shader shader(vertexShaderSource, fragmentShaderSource);
    
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
    
    	float transparentVertices[] = {
    		// positions         // texture Coords (swapped y coordinates because texture is flipped upside down)
    		0.0f,  0.5f,  0.0f,  0.0f,  0.0f,
    		0.0f, -0.5f,  0.0f,  0.0f,  1.0f,
    		1.0f, -0.5f,  0.0f,  1.0f,  1.0f,
    
    		0.0f,  0.5f,  0.0f,  0.0f,  0.0f,
    		1.0f, -0.5f,  0.0f,  1.0f,  1.0f,
    		1.0f,  0.5f,  0.0f,  1.0f,  0.0f
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
    
    	// transparent VAO
    	unsigned int transparentVAO, transparentVBO;
    	glGenVertexArrays(1, &transparentVAO);
    	glGenBuffers(1, &transparentVBO);
    	glBindVertexArray(transparentVAO);
    	glBindBuffer(GL_ARRAY_BUFFER, transparentVBO);
    	glBufferData(GL_ARRAY_BUFFER, sizeof(transparentVertices), transparentVertices, GL_STATIC_DRAW);
    	glEnableVertexAttribArray(0);
    	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    	glEnableVertexAttribArray(1);
    	glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    	glBindVertexArray(0);
    
    	// load textures
    	// -------------
    	unsigned int cubeTexture = loadTexture("marble.jpg");
    	unsigned int floorTexture = loadTexture("metal.png");
    	unsigned int transparentTexture = loadTexture("window.png");
    
    	std::vector<glm::vec3> windows
    	{
    		glm::vec3(-1.5f, 0.0f, -0.48f),
    		glm::vec3(1.5f, 0.0f, 0.51f),
    		glm::vec3(0.0f, 0.0f, 0.7f),
    		glm::vec3(-0.3f, 0.0f, -2.3f),
    		glm::vec3(0.5f, 0.0f, -0.6f)
    	};
    
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
    
    		std::map<float, glm::vec3> sorted;
    		for (unsigned int i = 0; i < windows.size(); i++)
    		{
    			float distance = glm::length(camera.Position - windows[i]);
    			sorted[distance] = windows[i];
    		}
    
    
    		// input
    		// -----
    		processInput(window);
    
    		// render
    		// ------
    		glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); // don't forget to clear the stencil buffer!
    
    
    		glm::mat4 model = glm::mat4(1.0f);
    		glm::mat4 view = camera.GetViewMatrix();
    		glm::mat4 projection = glm::perspective(glm::radians(camera.Zoom), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 100.0f);
    
    		shader.use();
    		shader.setMat4("view", view);
    		shader.setMat4("projection", projection);
    
    		// floor
    		glBindVertexArray(planeVAO);
    		glBindTexture(GL_TEXTURE_2D, floorTexture);
    		shader.setMat4("model", glm::mat4(1.0f));
    		glDrawArrays(GL_TRIANGLES, 0, 6);
    
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
    
    		// vegetation
    		glBindVertexArray(transparentVAO);
    		glBindTexture(GL_TEXTURE_2D, transparentTexture);
    		for (std::map<float, glm::vec3>::reverse_iterator it = sorted.rbegin(); it != sorted.rend(); ++it)
    		{
    			model = glm::mat4(1.0f);
    			model = glm::translate(model, it->second);
    			shader.setMat4("model", model);
    			glDrawArrays(GL_TRIANGLES, 0, 6);
    		}
    
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
    

