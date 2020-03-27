---
layout: post
title: OpenGL学习笔记：几何着色器
date: 发布于2019-09-19 14:46:36 +0800
categories: OpenGL学习笔记
tag: 4
---

之前还有一节介绍高级数据处理的，和这节的几何着色器都很好理解，没啥可总结的，直接上例子代码

<!-- more -->

    
    
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
    layout (location = 2) in vec2 aTexCoords;
    
    out VS_OUT {
        vec2 texCoords;
    } vs_out;
    
    uniform mat4 projection;
    uniform mat4 view;
    uniform mat4 model;
    
    void main()
    {
        vs_out.texCoords = aTexCoords;
        gl_Position = projection * view * model * vec4(aPos, 1.0); 
    }
    )1234";
    
    const char *fragmentShaderSource = R"1234(#version 330 core
    out vec4 FragColor;
    
    in vec2 TexCoords;
    
    uniform sampler2D texture_diffuse1;
    
    void main()
    {
        FragColor = texture(texture_diffuse1, TexCoords);
    }
    
    )1234";
    
    const char *geometryShaderSource = R"1234(#version 330 core
    layout (triangles) in;
    layout (triangle_strip, max_vertices = 3) out;
    
    in VS_OUT {
        vec2 texCoords;
    } gs_in[];
    
    out vec2 TexCoords; 
    
    uniform float time;
    
    vec4 explode(vec4 position, vec3 normal)
    {
        float magnitude = 2.0;
        vec3 direction = normal * ((sin(time) + 1.0) / 2.0) * magnitude; 
        return position + vec4(direction, 0.0);
    }
    
    vec3 GetNormal()
    {
        vec3 a = vec3(gl_in[0].gl_Position) - vec3(gl_in[1].gl_Position);
        vec3 b = vec3(gl_in[2].gl_Position) - vec3(gl_in[1].gl_Position);
        return normalize(cross(a, b));
    }
    
    void main() {    
        vec3 normal = GetNormal();
    
        gl_Position = explode(gl_in[0].gl_Position, normal);
        TexCoords = gs_in[0].texCoords;
        EmitVertex();
        gl_Position = explode(gl_in[1].gl_Position, normal);
        TexCoords = gs_in[1].texCoords;
        EmitVertex();
        gl_Position = explode(gl_in[2].gl_Position, normal);
        TexCoords = gs_in[2].texCoords;
        EmitVertex();
        EndPrimitive();
    }
    )1234";
    
    
    void framebuffer_size_callback(GLFWwindow* window, int width, int height);
    void mouse_callback(GLFWwindow* window, double xpos, double ypos);
    void scroll_callback(GLFWwindow* window, double xoffset, double yoffset);
    void processInput(GLFWwindow *window);
    unsigned int loadTexture(const char *path);
    unsigned int loadCubemap(vector<std::string> faces);
    
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
    
    std::string strModelPath = "D:/OpenGL/nanosuit/nanosuit.obj";
    
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
    	
    	// build and compile shaders
    	// -------------------------
    	Shader shader(vertexShaderSource, fragmentShaderSource, geometryShaderSource);
    
    	Model nanosuit(strModelPath);
    
    
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
    
    		glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    		glm::mat4 projection = glm::perspective(glm::radians(45.0f), (float)SCR_WIDTH / (float)SCR_HEIGHT, 1.0f, 100.0f);
    		glm::mat4 view = camera.GetViewMatrix();;
    		glm::mat4 model = glm::mat4(1.0f);
    		shader.use();
    		shader.setMat4("projection", projection);
    		shader.setMat4("view", view);
    		shader.setMat4("model", model);
    
    		// add time component to geometry shader in the form of a uniform
    		shader.setFloat("time", glfwGetTime());
    
    		// draw model
    		nanosuit.Draw(shader);
    
    		// glfw: swap buffers and poll IO events (keys pressed/released, mouse moved etc.)
    		// -------------------------------------------------------------------------------
    		glfwSwapBuffers(window);
    		glfwPollEvents();
    		Sleep(100);
    	}
    
    
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
    
    unsigned int loadCubemap(vector<std::string> faces)
    {
    	unsigned int textureID;
    	glGenTextures(1, &textureID);
    	glBindTexture(GL_TEXTURE_CUBE_MAP, textureID);
    
    	int width, height, nrChannels;
    	for (unsigned int i = 0; i < faces.size(); i++)
    	{
    		unsigned char *data = stbi_load(faces[i].c_str(), &width, &height, &nrChannels, 0);
    		if (data)
    		{
    			glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
    				0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data
    			);
    			stbi_image_free(data);
    		}
    		else
    		{
    			std::cout << "Cubemap texture failed to load at path: " << faces[i] << std::endl;
    			stbi_image_free(data);
    		}
    	}
    	glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    	glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    	glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    	glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    	glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE);
    
    	return textureID;
    }
    
    

* content
{:toc}


