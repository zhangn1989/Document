---
layout: post
title: OpenGL学习笔记：加载模型
date: 发布于2019-09-06 10:07:16 +0800
categories: OpenGL学习笔记
tag: 4
---

加载模型需要使用Assimp来屏蔽掉不同工具的模型文件，[Assimp的gayhub](https://github.com/assimp/assimp.git)  

<!-- more -->
简单说一下，不同的3D编辑工具生成的模型文件格式是不同的，Assimp的作用就是将不同的模型文件转换成相同的格式，然后OpenGL再将Assimp的格式转换成OpenGL的数据格式。Assimp是怎么转换其他模型格式的我们不需要关心，但是我们需要关心转换后的统一的数据格式，因为我们需要将这个格式转换到OpenGL中。关于Assimp的统一数据格式这里就不多介绍了，大家可以自行查看原版教程或者是Assimp的官方资料  
关于本例需要说明的是，原版教程中出于程序设计的角度对一些操作进行的面向对象的封装，但通常来说，封装的越好，对工作流程的理解也就越麻烦，这里为了方便理解Assimp的使用流程，尽量不去封装，只有一个必须写成函数的操作进行了函数封装。

    
    
    #include <iostream>
    #include <vector>
    #include <windows.h>
    
    #include <glad/glad.h>
    #include <GLFW/glfw3.h>
    
    #define STB_IMAGE_IMPLEMENTATION
    #include "stb_image.h"
    
    #include <glm/glm.hpp>
    #include <glm/gtc/matrix_transform.hpp>
    #include <glm/gtc/type_ptr.hpp>
    
    #include <assimp/Importer.hpp>
    #include <assimp/scene.h>
    #include <assimp/postprocess.h>
    
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
    
    // 本例需要两个着色器
    const char *vertexShaderSource = R"1234(#version 330 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aNormal;
    layout (location = 2) in vec2 aTexCoords;
    
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
    
    // 这个是被光照射的物体的片段着色器，从uniform变量中接受物体的颜色和光源的颜色。
    // 将光照的颜色和物体自身的颜色作分量相乘，结果就是最终要显示出来的颜色向量
    const char *fragmentShaderSource = R"1234(#version 330 core
    out vec4 FragColor;
    
    in vec2 TexCoords;
    
    uniform sampler2D texture_diffuse1;
    
    void main()
    {    
        FragColor = texture(texture_diffuse1, TexCoords);
    }
    )1234";
    
    
    struct Vertex {
    	glm::vec3 Position;
    	glm::vec3 Normal;
    	glm::vec2 TexCoords;
    };
    
    struct Texture {
    	unsigned int id;
    	std::string type;
    	aiString path;  // 我们储存纹理的路径用于与其它纹理进行比较
    };
    
    struct Mesh
    {
    	std::vector<Vertex> vertices;
    	std::vector<unsigned int> indices;
    	std::vector<Texture> textures;
    
    	unsigned int VAO, VBO, EBO;
    };
    
    std::vector<Mesh> meshs;
    std::string strModelPath = "D:/OpenGL/nanosuit/nanosuit.obj";
    std::string strModelDirectory = strModelPath.substr(0, strModelPath.find_last_of('/'));
    
    void processNode(aiNode *node, const aiScene *scene)
    {
    	// 处理节点所有的网格（如果有的话）
    	for (unsigned int i = 0; i < node->mNumMeshes; i++)
    	{
    		// 取出当前节点的网格
    		// Scene下的mMeshes数组储存了真正的Mesh对象
    		// 节点中的mMeshes数组保存的只是场景中网格数组的索引
    		aiMesh *aimesh = scene->mMeshes[node->mMeshes[i]];
    
    		// 取出网格后将网格的数据转换为OpenGL中的数据格式
    		Mesh mesh;
    
    		for (unsigned int j = 0; j < aimesh->mNumVertices; j++)
    		{
    			Vertex vertex;
    			// 处理顶点位置、法线和纹理坐标
    			glm::vec3 vector;
    			vector.x = aimesh->mVertices[j].x;
    			vector.y = aimesh->mVertices[j].y;
    			vector.z = aimesh->mVertices[j].z;
    			vertex.Position = vector;
    
    			vector.x = aimesh->mNormals[j].x;
    			vector.y = aimesh->mNormals[j].y;
    			vector.z = aimesh->mNormals[j].z;
    			vertex.Normal = vector;
    
    			// 网格是否有纹理坐标？
    			if (aimesh->mTextureCoords[0])
    			{
    				glm::vec2 vec;
    				vec.x = aimesh->mTextureCoords[0][j].x;
    				vec.y = aimesh->mTextureCoords[0][j].y;
    				vertex.TexCoords = vec;
    			}
    			else
    			{
    				vertex.TexCoords = glm::vec2(0.0f, 0.0f);
    			}
    
    			mesh.vertices.push_back(vertex);
    		}
    
    		// 处理索引
    		// 每个网格里都有一个face数组，每个元素都代表了一个图元，我们这里就是一个三角形
    		// 而每个图元又包含多个顶点索引，就是之前索引缓冲对象章节中的那个索引
    		// 有了顶点和索引就可以使用glDrawElements来绘图了，像之前章节中介绍的一样
    		for (unsigned int j = 0; j < aimesh->mNumFaces; j++)
    		{
    			aiFace face = aimesh->mFaces[j];
    			for (unsigned int k = 0; k < face.mNumIndices; k++)
    				mesh.indices.push_back(face.mIndices[k]);
    		}
    
    		// 处理材质
    		if (aimesh->mMaterialIndex >= 0)
    		{
    			// 取出材质
    			aiMaterial *material = scene->mMaterials[aimesh->mMaterialIndex];
    			// 加载漫反射
    			for (unsigned int j = 0; j < material->GetTextureCount(aiTextureType_DIFFUSE); j++)
    			{
    				// 获取纹理文件路径
    				aiString str;
    				material->GetTexture(aiTextureType_DIFFUSE, j, &str);
    
    				std::string filename = std::string(str.C_Str());
    				filename = strModelDirectory + '/' + filename;
    
    				// 读取纹理文件创建纹理
    				unsigned int textureID;
    				glGenTextures(1, &textureID);
    
    				int width, height, nrComponents;
    				unsigned char *data = stbi_load(filename.c_str(), &width, &height, &nrComponents, 0);
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
    					std::cout << "Texture failed to load at path: " << filename << std::endl;
    				}
    
    				Texture texture;
    				texture.id = textureID;
    				texture.type = "texture_diffuse";
    				texture.path = str;
    				mesh.textures.push_back(texture);
    			}
    
    			// 加载镜面反光
    			for (unsigned int j = 0; j < material->GetTextureCount(aiTextureType_SPECULAR); j++)
    			{
    				// 获取纹理文件路径
    				aiString str;
    				material->GetTexture(aiTextureType_SPECULAR, j, &str);
    
    				std::string filename = std::string(str.C_Str());
    				filename = strModelDirectory + '/' + filename;
    
    				// 读取纹理文件创建纹理
    				unsigned int textureID;
    				glGenTextures(1, &textureID);
    
    				int width, height, nrComponents;
    				unsigned char *data = stbi_load(filename.c_str(), &width, &height, &nrComponents, 0);
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
    					std::cout << "Texture failed to load at path: " << filename << std::endl;
    				}
    
    				Texture texture;
    				texture.id = textureID;
    				texture.type = "texture_specular";
    				texture.path = str;
    				mesh.textures.push_back(texture);
    			}
    		}
    
    		// 顶点法线索引纹理之类的出读出来了，像之前章节一样，绑定VA0之类的
    		glGenVertexArrays(1, &mesh.VAO);
    		glGenBuffers(1, &mesh.VBO);
    		glGenBuffers(1, &mesh.EBO);
    
    		glBindVertexArray(mesh.VAO);
    		glBindBuffer(GL_ARRAY_BUFFER, mesh.VBO);
    
    		glBufferData(GL_ARRAY_BUFFER, mesh.vertices.size() * sizeof(Vertex), &mesh.vertices[0], GL_STATIC_DRAW);
    
    		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, mesh.EBO);
    		glBufferData(GL_ELEMENT_ARRAY_BUFFER, mesh.indices.size() * sizeof(unsigned int),
    			&mesh.indices[0], GL_STATIC_DRAW);
    
    		// 顶点位置
    		glEnableVertexAttribArray(0);
    		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)0);
    		// 顶点法线
    		glEnableVertexAttribArray(1);
    		glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, Normal));
    		// 顶点纹理坐标
    		glEnableVertexAttribArray(2);
    		glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), (void*)offsetof(Vertex, TexCoords));
    
    		glBindVertexArray(0);
    
    		meshs.push_back(mesh);
    	}
    	// 接下来对它的子节点重复这一过程
    	for (unsigned int i = 0; i < node->mNumChildren; i++)
    	{
    		processNode(node->mChildren[i], scene);
    	}
    }
    
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
    
    	// 从模型文件中加载模型到OpenGL
    	Assimp::Importer import;
    	const aiScene *scene = import.ReadFile(strModelPath, aiProcess_Triangulate | aiProcess_FlipUVs);
    
    	if (!scene || scene->mFlags & AI_SCENE_FLAGS_INCOMPLETE || !scene->mRootNode)
    	{
    		std::cout << "ERROR::ASSIMP::" << import.GetErrorString() << std::endl;
    		return -1;
    	}
    
    	// 递归处理所有子节点
    	processNode(scene->mRootNode, scene);
    
    	// 本例对着色器的使用并不复杂，下面简单实现一下
    	int success;
    	char infoLog[512] = { 0 };
    
    	unsigned int vertexShader;
    	vertexShader = glCreateShader(GL_VERTEX_SHADER);
    	glShaderSource(vertexShader, 1, &vertexShaderSource, NULL);
    	glCompileShader(vertexShader);
    
    	glGetShaderiv(vertexShader, GL_COMPILE_STATUS, &success);
    	if (!success)
    	{
    		glGetShaderInfoLog(vertexShader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::VERTEX::COMPILATION_FAILED\n" << infoLog << std::endl;
    	}
    
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
    
    	unsigned int shader;
    	shader = glCreateProgram();
    
    	glAttachShader(shader, vertexShader);
    	glAttachShader(shader, fragmentShader);
    
    	glLinkProgram(shader);
    
    	glGetProgramiv(shader, GL_LINK_STATUS, &success);
    	if (!success)
    	{
    		memset(infoLog, 0, sizeof(infoLog));
    		glGetProgramInfoLog(shader, sizeof(infoLog), NULL, infoLog);
    		std::cout << "ERROR::SHADER::PROGRAM::LINK_FAILED\n" << infoLog << std::endl;
    	}
    
    	glUseProgram(shader);
    	glDeleteShader(vertexShader);
    	glDeleteShader(fragmentShader);
    
    	
    	// 启用深度测试
    	glEnable(GL_DEPTH_TEST);
    
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
    		glUseProgram(shader);
    
    	
    		glm::mat4 projection(1.0f);
    		projection = glm::perspective(glm::radians(fov), 800.0f / 600.0f, 0.1f, 100.0f);
    
    		glm::mat4 view(1.0f);
    		view = glm::lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
    		glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
    		glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm::value_ptr(view));
    
    
    		glm::mat4 model = glm::mat4(1.0f);
    		glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm::value_ptr(model));
    
    		for (unsigned int i = 0; i < meshs.size(); i++)
    		{
    			Mesh mesh = meshs[i];
    			unsigned int diffuseNr = 1;
    			unsigned int specularNr = 1;
    			for (unsigned int j = 0; j < meshs[i].textures.size(); j++)
    			{
    				glActiveTexture(GL_TEXTURE0 + j); // 在绑定之前激活相应的纹理单元
    												  // 获取纹理序号（diffuse_textureN 中的 N）
    				std::string number;
    				std::string name = meshs[i].textures[j].type;
    				if (name == "texture_diffuse")
    					number = std::to_string(diffuseNr++);
    				else if (name == "texture_specular")
    					number = std::to_string(specularNr++);
    
    				glUniform1f(glGetUniformLocation(shader, ("material." + name + number).c_str()), j);
    				glBindTexture(GL_TEXTURE_2D, meshs[i].textures[j].id);
    			}
    			glActiveTexture(GL_TEXTURE0);
    
    			// 绘制网格
    			glBindVertexArray(meshs[i].VAO);
    			glDrawElements(GL_TRIANGLES, meshs[i].indices.size(), GL_UNSIGNED_INT, 0);
    			glBindVertexArray(0);
    		}
    
    		glfwPollEvents();
    		glfwSwapBuffers(window);
    		Sleep(1);
    	}
    
    	// 测试代码，先允许存在内存泄露
    // 	glDeleteVertexArrays(1, &cubeVAO);
    // 	glDeleteVertexArrays(1, &lightVAO);
    // 	glDeleteBuffers(1, &VBO);
    
    	glfwTerminate();
    	glfwDestroyWindow(window);
    
    	return 0;
    }
    
    
    

* content
{:toc}


