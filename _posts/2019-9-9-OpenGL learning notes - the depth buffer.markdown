---
layout: post
title: OpenGL学习笔记：深度缓冲
date: 发布于2019-09-09 17:24:11 +0800
categories: OpenGL学习笔记
tag: 4
---

* content
{:toc}

之前为了方便理解，代码尽量不封装。这节以后，凡是涉及到新东西的尽量不去封装，而不涉及新东西的，为了代码的简洁，尽量去封装了
<!-- more -->


# 深度缓冲

我们观察空间中的两个物体，后面的物体被前面的物体挡住，我们是看不到被挡住的部分的，而深度缓冲可以简单理解为就是标识这个“前后”的值。

# 缓冲测试

OpenGL是一个3D世界，但显示设备通常是2D的。前面介绍过，要将一个3D图像转换为屏幕的2D图像，需要经过裁剪。在裁剪的过程中，被覆盖的片段就会被抛弃，而缓冲测试就是决定哪个片段被抛弃，哪个片段被绘制。比如最常见的物体遮挡问题，当我们调整观察角度，OpenGL将观察空间向裁剪空间进行转换的时候，会判断两个片段的深度值，大的会被遮挡，所以就抛弃，小的留下来被绘制。此外，OpenGL允许我们自己决定这个测试原则，如果想的话，可以让被遮挡的显示，前面的被抛弃。

# 深度精度

既然涉及到两个值的比较，自然会涉及到精度问题，我们可以用下面的公式将所有的精度值映射到0到1之间  
Fdepth=z−nearfar−near F_{depth}=\dfrac{z−near}{far−near}
Fdepth​=far−nearz−near​  
还记得坐标转换中介绍的平截头体(Frustum)吗？z可以是平截头体内部的任意值，near 和far值是我们之前提供给投影矩阵设置可视平截头体的那个
near 和 far 值。当z=near时，该公式的结果是0，当z=far时，该公式的结果是1，其间的任意值都可以通过这个公式映射到0到1之间。  
然而，现实中我们不会用到这样的线性精度的函数，我们需要一个近处精度高以提高图像质量，远处精度低以降低资源使用的公式来控制精度，就是用下面的函数  
Fdepth=1/z−1/near1/far−1/near F_{depth}=\dfrac{1/z−1/near}{1/far−1/near}
Fdepth​=1/far−1/near1/z−1/near​

# 深度可视化

原版教程的这个小节就是用一个例子去演示上面的精度公式，例子很好理解，这里就不多说了，看下原版教程就行

# 深度冲突

如果两个片段的深度相同，那么该抛弃谁该显示谁呢？OpenGL中会将两个片段交替显示，就会产生奇怪的花纹。可见，在共面的情况下，很容易发生深度冲突。根据上面的精度公式，越远的物体，其精度就越低，也就越容易发生冲突，冲突效果也就越明显。深度冲突不能够被完全避免，但一般会有一些技巧有助于在你的场景中减轻或者完全避免深度冲突，原版教程给出了下面三种解决冲突的办法：

  * 第一个也是最重要的技巧是永远不要把多个物体摆得太靠近，以至于它们的一些三角形会重叠。通过在两个物体之间设置一个用户无法注意到的偏移值，你可以完全避免这两个物体之间的深度冲突。在箱子和地板的例子中，我们可以将箱子沿着正y轴稍微移动一点。箱子位置的这点微小改变将不太可能被注意到，但它能够完全减少深度冲突的发生。然而，这需要对每个物体都手动调整，并且需要进行彻底的测试来保证场景中没有物体会产生深度冲突。
  * 第二个技巧是尽可能将近平面设置远一些。在前面我们提到了精度在靠近近平面时是非常高的，所以如果我们将近平面远离观察者，我们将会对整个平截头体有着更大的精度。然而，将近平面设置太远将会导致近处的物体被裁剪掉，所以这通常需要实验和微调来决定最适合你的场景的近平面距离。
  * 另外一个很好的技巧是牺牲一些性能，使用更高精度的深度缓冲。大部分深度缓冲的精度都是24位的，但现在大部分的显卡都支持32位的深度缓冲，这将会极大地提高精度。所以，牺牲掉一些性能，你就能获得更高精度的深度测试，减少深度冲突。

我用第一个办法测试过，将cubeVertices数组的顶点坐标的所有Z轴是-0.5的数据全部改成-0.4，确实能消除冲突，但箱子也变成悬空状态了，想既能消除冲突，又看不出悬空的完美效果，需要慢慢调试。

# 完整代码

本节代码层次上没有新东西，基本完全照搬的原版教程，主要看下中文注释就好

    
    
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
    		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    
    		shader.use();
    		glm::mat4 model = glm::mat4(1.0f);
    		glm::mat4 view = camera.GetViewMatrix();
    		glm::mat4 projection = glm::perspective(glm::radians(camera.Zoom), (float)SCR_WIDTH / (float)SCR_HEIGHT, 0.1f, 100.0f);
    		shader.setMat4("view", view);
    		shader.setMat4("projection", projection);
    
    		// 如果不启用深度缓冲区
    		// 把floor代码段放在前面，得到的图像是cubes挡住了floor
    		// 把cubes代码段放在前面，得到的图像是floor挡住了cubes
    		// 可以推测OpenGL的绘画顺序
    		// 首先上面的先绘画，然后绘画下面的
    		// 由于后画的会覆盖先画的，所以表现出来的效果就是后画的挡住了先画的
    		// 一旦启用深度缓冲区
    		// 我们可以利用缓冲测试来决定谁挡住谁，而不是由绘画的先后去决定
    		// 通过缓冲测试的片段被绘画，没有通过的被丢弃
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
    		// floor
    		glBindVertexArray(planeVAO);
    		glBindTexture(GL_TEXTURE_2D, floorTexture);
    		shader.setMat4("model", glm::mat4(1.0f));
    		glDrawArrays(GL_TRIANGLES, 0, 6);
    		glBindVertexArray(0);
    
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
    

