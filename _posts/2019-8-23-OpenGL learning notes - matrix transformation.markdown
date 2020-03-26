---
layout: post
title: OpenGL学习笔记：矩阵变换
date: 发布于2019-08-23 20:42:31 +0800
categories: OpenGL学习笔记
tag: 4
---

* content
{:toc}

### 文章目录

  * 缩放
<!-- more -->

    * glm矩阵表示
    * glm缩放矩阵实现
  * 位移
    * 齐次坐标
    * glm位移矩阵实现
  * 旋转
    * 沿x轴旋转
    * 沿y轴旋转
    * 沿z轴旋转
    * 沿任意轴旋转
    * glm旋转矩阵实现
  * 矩阵的组合
    * glm矩阵组合使用

  
接上篇[OpenGL学习笔记：数学基础和常用矩阵总结（一）](https://blog.csdn.net/mumufan05/article/details/100041164)

# 缩放

前面说了一大堆的理论，现在终于可以来点实际应用了  
对一个向量进行缩放(Scaling)就是对向量的长度进行缩放，而保持它的方向不变。  
我们先来尝试缩放向量v⃗=(3,2)\vec{v}
=(3,2)v=(3,2)。我们可以把向量沿着x轴缩放0.5，使它的宽度缩小为原来的二分之一；我们将沿着y轴把向量的高度缩放为原来的两倍。我们看看把向量缩放(0.5,
2)倍所获得的s⃗\vec{s}s是什么样的  
![向量缩放](https://img-blog.csdnimg.cn/20190823192356228.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
这是我们想要的结果，但我们怎么计算出这个结果呢？如果是这种简单的缩放，我们可以把v⃗\vec{v}v的x分量乘以0.5，y分量乘以2来得到这个结果。但这种方法不适合用在计算机的计算中，为了加快运算速度，简化计算，往往使用矩阵。因此我们需要用构建一个缩放矩阵来实现缩放功能  
回顾刚才单位矩阵的计算，第一个结果元素是矩阵的第一行的每个元素乘以向量的每个对应元素。因为每行的元素除了第一个都是0，可得：1⋅1+0⋅2+0⋅3+0⋅4=11\cdot
1+0\cdot 2+0\cdot 3+0\cdot 4=11⋅1+0⋅2+0⋅3+0⋅4=1，向量的其他3个元素同理。  
如果我们把对角线上的1改变一下呢？比如说第一行的对角线是0.5，第二行的对角线是2构建一个矩阵，再和v⃗\vec{v}v相乘，得到下面的计算过程  
(0.5002)×(32)=(0.5×3+0×20×3+2×2)=(0.5×32×2)=(1.54) \left( \begin{array}{ccc}
0.5 &amp; 0 \\\ 0 &amp; 2 \end{array} \right) \times \left( \begin{array}{ccc}
3 \\\ 2 \end{array} \right) = \left( \begin{array}{ccc} 0.5\times3+0\times2
\\\ 0\times3+2\times2 \end{array} \right)= \left( \begin{array}{ccc}
0.5\times3 \\\ 2\times2 \end{array} \right) = \left( \begin{array}{ccc} 1.5
\\\ 4 \end{array} \right)
(0.50​02​)×(32​)=(0.5×3+0×20×3+2×2​)=(0.5×32×2​)=(1.54​)  
这样，我们就得到了我们想要的结果，(0.5002)\left( \begin{array}{ccc}0.5 &amp; 0 \\\0 &amp; 2
\end{array}
\right)(0.50​02​)就是我们的变换矩阵，下面，我们把这个变换矩阵推广一下，如果我们把缩放变量表示为(S1,S2,S3)(S_1,S_2,S_3)(S1​,S2​,S3​)我们可以为任意向量(x,y,z)(x,y,z)(x,y,z)定义一个缩放矩阵：  
(S10000S20000S300001)⋅(xyz1)=(S1⋅xS2⋅yS3⋅z1) \left( \begin{array}{ccc} S_1
&amp; 0 &amp;0 &amp;0 \\\ 0 &amp; S_2 &amp;0 &amp;0 \\\ 0 &amp; 0 &amp;S_3
&amp;0 \\\ 0 &amp; 0 &amp; 0 &amp;1 \end{array} \right) \cdot \left(
\begin{array}{ccc} x \\\ y \\\ z \\\ 1 \end{array} \right) = \left(
\begin{array}{ccc} S_1\cdot x \\\ S_2\cdot y \\\ S_3\cdot z \\\ 1 \end{array}
\right)
⎝⎜⎜⎛​S1​000​0S2​00​00S3​0​0001​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​xyz1​⎠⎟⎟⎞​=⎝⎜⎜⎛​S1​⋅xS2​⋅yS3​⋅z1​⎠⎟⎟⎞​  
注意，第四个缩放向量仍然是1，因为在3D空间中缩放w分量是无意义的。w分量另有其他用途，在后面我们会看到。

## glm矩阵表示

好，所有的理论知识都已经准备好了，下面我们来看一下程序中是怎么应用的，还记得[OpenGL学习笔记：矩阵变换](https://blog.csdn.net/mumufan05/article/details/99743170)中我们用来做矩阵缩放的代码吗？  
首先是创建缩放矩阵

    
    
    glm::mat4 trans(1.0f);
    trans = glm::scale(trans, glm::vec3(0.5, 0.5, 0.5));
    

然后是将缩放矩阵传递给着色器

    
    
    unsigned int transformLoc = glGetUniformLocation(shaderProgram, "transform");
    glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm::value_ptr(trans));
    

最后是在着色器中对顶点向量进行缩放

    
    
    gl_Position = transform * vec4(aPos, 1.0f);
    

接下来我们来扒一下这些代码都干了什么  
首先是glm::mat4 trans(1.0f);创建一个单位矩阵，怎么创建的呢？我们来看看glm::mat4的构造函数

    
    
    	template<typename T, qualifier Q>
    	GLM_FUNC_QUALIFIER GLM_CONSTEXPR mat<4, 4, T, Q>::mat(T const& s)
    	{
    		// 每个元素都是矩阵的第一列，不是第一行
    		this->value[0] = col_type(s, 0, 0, 0);	
    		this->value[1] = col_type(0, s, 0, 0);
    		this->value[2] = col_type(0, 0, s, 0);
    		this->value[3] = col_type(0, 0, 0, s);
    	}
    

简单目测一下，this->value应该是用来表示矩阵的，数组的每个元素都是一组向量（ _
**注意：这个数组的每一个元素是一个向量，这个向量对应的是矩阵中的一列，不是一行**_
），并用变量s初始化，我们再来看一下this->value和col_type都是什么鬼

    
    
    	template<typename T, qualifier Q>
    	struct mat<4, 4, T, Q>
    	{
    		typedef vec<4, T, Q> col_type;
    		typedef vec<4, T, Q> row_type;
    		typedef mat<4, 4, T, Q> type;
    		typedef mat<4, 4, T, Q> transpose_type;
    		typedef T value_type;
    
    	private:
    		col_type value[4];
    		// 下面代码省略
    	}
    

确定了，value就是一个具有四个元素的col_type类型的数组，而col_type又是一个vec<4, T,
Q>类型，从名字上猜测应该是一个向量类型，我们看一下vec的数据定义

    
    
    // 删除无关代码
    template<typename T, qualifier Q>
    	struct vec<4, T, Q>
    	{
    		// -- Data --
    		union { T x, r,s; };
    		union { T y, g, t; };
    		union { T z, b, p; };
    		union { T w, a, q; };
    	}
    

可以看到vec中存放了四个联合体，每个联合体就是一个向量分量，而模版T就是数据类型。  
到这里我们就清楚glm中是怎么表示一个矩阵的了  
我们给glm::mat4的构造函数传进来一个参数1，然后glm用这个参数1分别构造了四个向量，其中第一个向量的第一个分量是1，其他分量是0，而第二个向量的第二个分量是1，其他分量是0，第三、四个向量同样构造，然后在把这四个向量存放在一个具有四个元素的四维向量数组中，这个数组就是我们所构建的4×44\times44×4的单位矩阵了。

## glm缩放矩阵实现

接下来我们再来看一下trans = glm::scale(trans, glm::vec3(0.5, 0.5, 0.5));都干了些什么事

    
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER mat<4, 4, T, Q> scale(mat<4, 4, T, Q> const& m, vec<3, T, Q> const& v)
    {
    	mat<4, 4, T, Q> Result;
    	Result[0] = m[0] * v[0];
    	Result[1] = m[1] * v[1];
    	Result[2] = m[2] * v[2];
    	Result[3] = m[3];
    	return Result;
    }
    

在scale函数中，形参m是我们传进来的单位矩阵，v是我们传进来的缩放倍数的向量。  
v[0]很好理解，就是取出v的第一个分量，这里是0.5，m[0]也很好理解，就是取出m的第一个向量，前面我们已经分析过了，m是一个具有四个元素的四维向量数组，本例中应该是(1,0,0,0)(1,0,0,0)(1,0,0,0)，m[0]
*
v[0]就是用向量(1,0,0,0)(1,0,0,0)(1,0,0,0)乘以0.5，结果应该是(0.5,0,0,0)(0.5,0,0,0)(0.5,0,0,0)。虽然我们看懂了这句代码，但还是想看一看glm是怎么计算的。下面这段代码是vec<3,
T, Q>重载的[]运算符，根据下标取出响应的xyz，对应的是scale函数中的v[0]。

    
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR T const& vec<3, T, Q>::operator[](typename vec<3, T, Q>::length_type i) const
    {
    	assert(i >= 0 && i < this->length());
    	switch(i)
    	{
    	default:
    	case 0:
    		return x;
    	case 1:
    		return y;
    	case 2:
    		return z;
    	}
    }
    

下面这段代码是mat<4, 4, T, Q>重载的[]，取出value中的第i个向量，对应的是scale函数中的m[0]。

    
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR typename mat<4, 4, T, Q>::col_type const& mat<4, 4, T, Q>::operator[](typename mat<4, 4, T, Q>::length_type i) const
    {
    	assert(i < this->length());
    	return this->value[i];
    }
    

下面的三个函数是glm对运算符 _的重载堆栈，第一层是mat <4, 4, T, Q>重载的_，在这层重载中，用v重新构造了一个vec<4, T,
Q>型的向量，再用这个向量乘以缩放比例，就是scale函数中的v[0]。然后再继续调用vec<4, T,
Q>型的*重载，在这一层中先是用v[0]构造了一个四维向量，看下面的第四个函数，vec<4, T, Q>::vec(T
scalar)构造方式是用scale给四维向量的四个分量赋值，得到了一个(scale,scale,scale,scale)(scale,scale,scale,scale)(scale,scale,scale,scale)的四维向量，然后再调用了call函数，我们继续来到call函数中。在call函数中我们看到，对两个四维变量的四个分量依次相乘，再用四个结果构造了一个新的四维变量，最后返回到我们调用的scale函数中，将结果拷贝给Result[0]。

    
    
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR vec<4, T, Q> operator*(vec<4, T, Q> const& v, T const & scalar)
    {
    	return vec<4, T, Q>(v) *= scalar;
    }
    
    template<typename U>
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR vec<4, T, Q> & vec<4, T, Q>::operator*=(U scalar)
    {
    	return (*this = detail::compute_vec4_mul<T, Q, detail::is_aligned<Q>::value>::call(*this, vec<4, T, Q>(scalar)));
    }
    
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR static vec<4, T, Q> call(vec<4, T, Q> const& a, vec<4, T, Q> const& b)
    {
    	return vec<4, T, Q>(a.x * b.x, a.y * b.y, a.z * b.z, a.w * b.w);
    }
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR vec<4, T, Q>::vec(T scalar)
    	: x(scalar), y(scalar), z(scalar), w(scalar)
    {}
    

我们再来理一下这个过程  
首先是我们代码中，我们以一个单位矩阵和一个缩放向量为参数调用glm的scale函数，scale函数首先取出单位矩阵的第一行的数据和缩放向量的第一个分量做乘法，结果得到一个缩放后的向量。  
而glm计算向量数乘的方法是，首先用这个标量构建一个所有分量都是该标量的向量，再用这个向量和要计算的向量的分量依次相乘，将得到的结果构造一个结果向量。  
而我们传进去的是一个四阶单位向量和一个三维的缩放比例，我们想要的结果是单位的第一二三行进行缩放，第四行还是1，所以scale函数只计算了前三行的比例缩放，第四行原样输出，至此，我们得到了一个这样的矩阵  
(0.500000.500000.500001) \left( \begin{array}{ccc} 0.5 &amp; 0 &amp;0 &amp;0
\\\ 0 &amp; 0.5 &amp;0 &amp;0 \\\ 0 &amp; 0 &amp;0.5 &amp;0 \\\ 0 &amp; 0
&amp; 0 &amp;1 \end{array} \right) ⎝⎜⎜⎛​0.5000​00.500​000.50​0001​⎠⎟⎟⎞​  
这就是我们的缩放矩阵了，再将这个缩放矩阵传到着色器中，与顶点数据相乘，就得到了缩放后的顶点向量。这一过程是在GPU中进行的，因此，我们无法看到矩阵乘法是怎么做的。  
不过不用担心，glm应该会有矩阵乘法的代码，本次没有用到，就先不研究了，等以后用到了在研究一下矩阵乘法在计算机中是怎么实现的。

# 位移

位移(Translation)是在原始向量的基础上加上另一个向量从而获得一个在不同位置的新向量的过程，从而在位移向量基础上移动了原始向量。我们已经讨论了向量加法，所以这应该不会太陌生。  
我们先来尝试位移向量v⃗=(3,2)\vec{v}
=(3,2)v=(3,2)。我们可以把向量沿着x轴向左平移1个单位，沿着y轴向右平移两个单位，下面是平移后所获得的s⃗\vec{s}s。  
![向量位移](https://img-blog.csdnimg.cn/2019082612180934.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
我们可以通过将向量v⃗\vec{v}v的x分量减1，y分量加2得到结果向量s⃗\vec{s}s。和缩放矩阵类似，我们需要一个位移矩阵。如果我们把位移向量表示为(Tx,Ty,Tz)(T_x,T_y,T_z)(Tx​,Ty​,Tz​)，我们就能把位移矩阵定义为：  
(100Tx010Ty001Tz0001)⋅(xyz1)=(x+Txy+Tyz+Tz1) \left( \begin{array}{ccc} 1&amp;
0 &amp;0 &amp;T_x \\\ 0 &amp; 1&amp;0 &amp;T_y \\\ 0 &amp; 0 &amp;1&amp;T_z
\\\ 0 &amp; 0 &amp; 0 &amp;1 \end{array} \right) \cdot \left(
\begin{array}{ccc} x \\\ y \\\ z \\\ 1 \end{array} \right) = \left(
\begin{array}{ccc} x+T_x \\\ y+T_y \\\ z+T_z \\\ 1 \end{array} \right)
⎝⎜⎜⎛​1000​0100​0010​Tx​Ty​Tz​1​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​xyz1​⎠⎟⎟⎞​=⎝⎜⎜⎛​x+Tx​y+Ty​z+Tz​1​⎠⎟⎟⎞​

## 齐次坐标

这里有必要介绍一下齐次坐标。很多新手朋友一定会感到奇怪，为什么这个位移矩阵和上面的缩放矩阵都使用四维向量而不是三维向量？让我们用三维的来计算一下看会怎么样：  
(10Tx01Ty00Tz)⋅(xyz)=(1⋅x+0⋅y+Tx⋅z0⋅x+1⋅y+Ty⋅z0⋅x+0⋅y+Tz⋅z)=(z⋅Txz⋅TyTz)
\left( \begin{array}{ccc} 1&amp; 0 &amp;T_x \\\ 0 &amp; 1&amp;T_y \\\ 0 &amp;
0 &amp;T_z \end{array} \right) \cdot \left( \begin{array}{ccc} x \\\ y \\\ z
\end{array} \right) = \left( \begin{array}{ccc} 1\cdot x+ 0\cdot y + T_x\cdot
z \\\ 0\cdot x+ 1\cdot y + T_y\cdot z \\\ 0\cdot x+ 0\cdot y + T_z\cdot z
\end{array} \right)= \left( \begin{array}{ccc} z\cdot T_x \\\ z\cdot T_y \\\
T_z \end{array} \right)
⎝⎛​100​010​Tx​Ty​Tz​​⎠⎞​⋅⎝⎛​xyz​⎠⎞​=⎝⎛​1⋅x+0⋅y+Tx​⋅z0⋅x+1⋅y+Ty​⋅z0⋅x+0⋅y+Tz​⋅z​⎠⎞​=⎝⎛​z⋅Tx​z⋅Ty​Tz​​⎠⎞​  
可以看到，这完全不是我们想要的结果。这还只是小问题，在使用矩阵计算变换时，矩阵的乘积只能表示旋转和缩放，不能表示平移。为统一计算，引入了第四个分量w，这使得原本二维坐标变成三维，三维坐标变为四维，w称为比例因子，一个三维坐标的三个分量x，y，z用齐次坐标表示为变为x，y，z，w的四维空间，变换成三维坐标的方式是x/w,y/w,z/w。当w为0时，在数学上代表无穷远点，即并非一个具体的坐标位置，而是一个具有大小和方向的向量。从而，通过w我们就可以用同一系统表示两种不同的量。  
在OpenGL中，作为坐标点时，w参数为1，否则为0，如此一来，所有的几何变换和向量运算都可以用相同的矩阵乘积进行运算和变换，当一个向量和一个矩阵相乘时所得的结果也是向量。  
这里只是简单介绍一点齐次坐标的皮毛，想要深入了解的朋友可以自行去找相关的资料。

## glm位移矩阵实现

和缩放一样，我们先找找之前章节中用到的位移功能

    
    
    trans = glm::translate(trans, glm::vec3(0.5f, -0.5f, 0.0f));
    

关于glm中矩阵的创建和表示这里不在赘述，需要注意的是，在glm::mat4类中的向量数组， _ **每个元素都是矩阵中的一列，不是一行**_
，这一点在本小节中尤为重要，如果不清楚这点，本小节会看的很蒙逼。  
我们来看下translate的函数实现

    
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER mat<4, 4, T, Q> translate(mat<4, 4, T, Q> const& m, vec<3, T, Q> const& v)
    {
    	mat<4, 4, T, Q> Result(m);
    	Result[3] = m[0] * v[0] + m[1] * v[1] + m[2] * v[2] + m[3];
    	return Result;
    }
    

关于[]和*的重载在缩放小节中就说过了，这里不再多说。在translate中，首先用我们传进去的单位矩阵m拷贝构造了一个结果矩阵Result，然后取出m的第一列向量，与位移向量的x分量相乘，本例中得到的结果是(0.5,0,0,0)(0.5,0,0,0)(0.5,0,0,0)。接着是取出第二、三列向量分别与位移向量y,z分量相乘，本例中得到的结果是(0,−0.5,0,0)(0,-0.5,0,0)(0,−0.5,0,0)和(0,0,0,0)(0,0,0,0)(0,0,0,0)，最后将这三个向量和m的第四列向量(0,0,0,1)(0,0,0,1)(0,0,0,1)加到一起，得到一个结果向量(0.5,−0.5,0,1)(0.5,-0.5,0,1)(0.5,−0.5,0,1)。最后再将这个结果向量赋值给Result的第四列，得到下面这个位移矩阵：  
(1000.5010−0.500100001)\left( \begin{array}{ccc} 1&amp; 0 &amp; 0&amp;0.5 \\\
0 &amp; 1&amp; 0&amp;-0.5\\\ 0 &amp; 0&amp; 1&amp;0 \\\ 0 &amp; 0 &amp;
0&amp;1 \end{array} \right)⎝⎜⎜⎛​1000​0100​0010​0.5−0.501​⎠⎟⎟⎞​  
结果得到了，我们再来看一下+的重载是怎么实现的

    
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR vec<4, T, Q> operator+(vec<4, T, Q> const& v1, vec<4, T, Q> const& v2)
    {
    	return vec<4, T, Q>(v1) += v2;
    }
    
    template<typename U>
    GLM_FUNC_QUALIFIER GLM_CONSTEXPR vec<4, T, Q> & vec<4, T, Q>::operator+=(vec<4, U, Q> const& v)
    {
    	return (*this = detail::compute_vec4_add<T, Q, detail::is_aligned<Q>::value>::call(*this, vec<4, T, Q>(v)));
    }
    
    template<typename T, qualifier Q, bool Aligned>
    struct compute_vec4_add
    {
    	GLM_FUNC_QUALIFIER GLM_CONSTEXPR static vec<4, T, Q> call(vec<4, T, Q> const& a, vec<4, T, Q> const& b)
    	{
    		return vec<4, T, Q>(a.x + b.x, a.y + b.y, a.z + b.z, a.w + b.w);
    	}
    };
    

过程和缩放类似，这里就不跟着分析了。  
位移矩阵有了，接下来就是把位移矩阵传递个着色器，由GPU去和顶点数据计算了，和缩放类似，不在多说。

# 旋转

旋转是非常麻烦的一个操作，让我们先来一个最简单的绕原点旋转的二维旋转矩阵，先看下图  
![向量旋转](https://img-blog.csdnimg.cn/20190826165818757.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
首先，我们需要复习一下两角和公式  
sin⁡(α+β)=sin⁡α⋅cos⁡β+cos⁡α⋅sin⁡βcos⁡(α+β)=cos⁡α⋅cos⁡β−sin⁡α⋅sin⁡β
\sin(\alpha+\beta)=\sin\alpha\cdot\cos\beta+\cos\alpha\cdot\sin\beta \\\
\cos(\alpha+\beta)=\cos\alpha\cdot\cos\beta-\sin\alpha\cdot\sin\beta
sin(α+β)=sinα⋅cosβ+cosα⋅sinβcos(α+β)=cosα⋅cosβ−sinα⋅sinβ  
设点A坐标为(x,y)(x,y)(x,y)，点B坐标为(x′,y′)(x&#x27;,y&#x27;)(x′,y′),|u⃗\vec{u}u|=r  
cos⁡(α+β)=x′rsin⁡(α+β)=y′r⇓x′=r⋅cos⁡(α+β)y′=r⋅sin⁡(α+β)
\cos(\alpha+\beta)=\frac{x&#x27;}{r} \\\ \sin(\alpha+\beta)=\frac{y&#x27;}{r}
\\\ \Downarrow{} \\\ x&#x27;=r\cdot\cos(\alpha+\beta) \\\
y&#x27;=r\cdot\sin(\alpha+\beta) \\\
cos(α+β)=rx′​sin(α+β)=ry′​⇓x′=r⋅cos(α+β)y′=r⋅sin(α+β)  
再将x′y′x&#x27;y&#x27;x′y′带入到两角和公式  
x′=r⋅cos⁡α⋅cos⁡β−r⋅sin⁡α⋅sin⁡βy′=r⋅sin⁡α⋅cos⁡β+r⋅sin⁡α⋅sin⁡β
x&#x27;=r\cdot\cos\alpha\cdot\cos\beta-r\cdot\sin\alpha\cdot\sin\beta \\\
y&#x27;=r\cdot\sin\alpha\cdot\cos\beta+r\cdot\sin\alpha\cdot\sin\beta \\\
x′=r⋅cosα⋅cosβ−r⋅sinα⋅sinβy′=r⋅sinα⋅cosβ+r⋅sinα⋅sinβ  
同x′y′x&#x27;y&#x27;x′y′一样，xxx和yyy可以写成下面这种形式  
x=r⋅cos⁡αy=r⋅sin⁡α x=r\cdot\cos\alpha \\\ y=r\cdot\sin\alpha \\\
x=r⋅cosαy=r⋅sinα  
最后将xyxyxy带入到x′y′x&#x27;y&#x27;x′y′中  
x′=x⋅cos⁡β−y⋅sin⁡βy′=x⋅sin⁡β+y⋅cos⁡β x&#x27;=x\cdot\cos\beta-y\cdot\sin\beta
\\\ y&#x27;=x\cdot\sin\beta+y\cdot\cos\beta x′=x⋅cosβ−y⋅sinβy′=x⋅sinβ+y⋅cosβ  
整理成矩阵格式就是  
(x′y′)=(cos⁡β−sin⁡βsin⁡βcos⁡β)⋅(xy) \left( \begin{array}{ccc} x&#x27; \\\
y&#x27; \end{array} \right) = \left( \begin{array}{ccc} \cos\beta&amp;
-\sin\beta \\\ \sin\beta &amp; \cos\beta \end{array} \right) \cdot \left(
\begin{array}{ccc} x\\\ y \end{array} \right)
(x′y′​)=(cosβsinβ​−sinβcosβ​)⋅(xy​)  
至此，最简单的一个向量旋转公式推导完成。  
其他复杂的旋转矩阵就不再推导了，实在太麻烦，下面只给出结果

## 沿x轴旋转

(10000cos⁡θ−sin⁡θ00sin⁡θcos⁡θ00001)⋅(xyz1)=(xcos⁡θ⋅y−sin⁡θ⋅zsin⁡θ⋅y+cos⁡θ⋅z1)
\left( \begin{array}{ccc} 1 &amp; 0 &amp; 0 &amp; 0 \\\ 0 &amp; \cos\theta
&amp; -\sin\theta &amp; 0 \\\ 0 &amp; \sin\theta &amp; \cos\theta &amp; 0 \\\
0 &amp; 0 &amp; 0 &amp; 1 \end{array} \right) \cdot \left( \begin{array}{ccc}
x \\\ y \\\ z \\\ 1 \end{array} \right)= \left( \begin{array}{ccc} x \\\
\cos\theta\cdot y-\sin\theta\cdot z \\\ \sin\theta\cdot y+\cos\theta\cdot z
\\\ 1 \end{array} \right)
⎝⎜⎜⎛​1000​0cosθsinθ0​0−sinθcosθ0​0001​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​xyz1​⎠⎟⎟⎞​=⎝⎜⎜⎛​xcosθ⋅y−sinθ⋅zsinθ⋅y+cosθ⋅z1​⎠⎟⎟⎞​

## 沿y轴旋转

(cos⁡θ0sin⁡θ00100−sin⁡θ0cos⁡θ00001)⋅(xyz1)=(cos⁡θ⋅x+sin⁡θ⋅zy−sin⁡θ⋅x+cos⁡θ⋅z1)
\left( \begin{array}{ccc} \cos\theta &amp; 0 &amp; \sin\theta &amp; 0 \\\ 0
&amp; 1 &amp; 0 &amp; 0 \\\ -\sin\theta &amp; 0 &amp; \cos\theta &amp; 0 \\\ 0
&amp; 0 &amp; 0 &amp; 1 \end{array} \right) \cdot \left( \begin{array}{ccc} x
\\\ y \\\ z \\\ 1 \end{array} \right)= \left( \begin{array}{ccc}
\cos\theta\cdot x+\sin\theta\cdot z \\\ y \\\ -\sin\theta\cdot
x+\cos\theta\cdot z \\\ 1 \end{array} \right)
⎝⎜⎜⎛​cosθ0−sinθ0​0100​sinθ0cosθ0​0001​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​xyz1​⎠⎟⎟⎞​=⎝⎜⎜⎛​cosθ⋅x+sinθ⋅zy−sinθ⋅x+cosθ⋅z1​⎠⎟⎟⎞​

## 沿z轴旋转

(cos⁡θ−sin⁡θ00sin⁡θcos⁡θ0000100001)⋅(xyz1)=(cos⁡θ⋅x−sin⁡θ⋅ysin⁡θ⋅x+cos⁡θ⋅yz1)
\left( \begin{array}{ccc} \cos\theta &amp; -\sin\theta &amp; 0 &amp; 0 \\\
\sin\theta &amp; \cos\theta &amp; 0 &amp; 0 \\\ 0 &amp; 0 &amp; 1 &amp; 0 \\\
0 &amp; 0 &amp; 0 &amp; 1 \end{array} \right) \cdot \left( \begin{array}{ccc}
x \\\ y \\\ z \\\ 1 \end{array} \right)= \left( \begin{array}{ccc}
\cos\theta\cdot x-\sin\theta\cdot y \\\ \sin\theta\cdot x+\cos\theta\cdot y
\\\ z \\\ 1 \end{array} \right)
⎝⎜⎜⎛​cosθsinθ00​−sinθcosθ00​0010​0001​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​xyz1​⎠⎟⎟⎞​=⎝⎜⎜⎛​cosθ⋅x−sinθ⋅ysinθ⋅x+cosθ⋅yz1​⎠⎟⎟⎞​

## 沿任意轴旋转

对于任意轴旋转，一个简单的办法是拆分成xyzxyzxyz三轴分解旋转，即先沿xxx轴旋转，再沿yyy轴旋转，最后沿zzz轴旋转。但是，将一个旋转分解成三次，很容易出现万向节死锁。万向节死锁简单说就是当子旋转转到特定角度后转动，一旦转动父旋转，就会使子旋转丢失旋转角度，从而使某些角度永远也不能旋转到。关于万向节死锁的动画演示可以看这个视频[欧拉旋转](https://v.youku.com/v_show/id_XNzkyOTIyMTI=.html)。  
一个比较好的方法是有一个旋转矩阵可以对任意轴进行旋转，而不是将一个旋转分解成xyzxyzxyz三轴。这样的矩阵是存在的，但却非常麻烦，关于这个矩阵的推导，有兴趣的同学可以自行查找相关资料。具体公式见下面，其中(Rx,Ry,Rz)(R_x,R_y,R_z)(Rx​,Ry​,Rz​)就是这个任意轴向量  
(cos⁡θ+Rx2(1−cos⁡θ)RxRy(1−cos⁡θ)−Rzsin⁡θRxRz(1−cos⁡θ)+Rysin⁡θ0RyRx(1−cos⁡θ)+Rzsin⁡θcos⁡θ+Ry2(1−cos⁡θ)RyRz(1−cos⁡θ)−Rxsin⁡θ0RzRx(1−cos⁡θ)−Rysin⁡θRzRy(1−cos⁡θ)+Rxsin⁡θcos⁡θ+Rz2(1−cos⁡θ)00001)
\left( \begin{array}{ccc} \cos\theta+R_x^2(1-\cos\theta) &amp;
R_xR_y(1-\cos\theta)-R_z\sin\theta &amp; R_xR_z(1-\cos\theta)+R_y\sin\theta
&amp; 0 \\\ R_yR_x(1-\cos\theta)+R_z\sin\theta &amp;
\cos\theta+R_y^2(1-\cos\theta) &amp; R_yR_z(1-\cos\theta)-R_x\sin\theta &amp;
0 \\\ R_zR_x(1-\cos\theta)-R_y\sin\theta &amp;
R_zR_y(1-\cos\theta)+R_x\sin\theta &amp; \cos\theta+R_z^2(1-\cos\theta) &amp;
0 \\\ 0 &amp; 0 &amp; 0 &amp; 1 \end{array} \right)
⎝⎜⎜⎛​cosθ+Rx2​(1−cosθ)Ry​Rx​(1−cosθ)+Rz​sinθRz​Rx​(1−cosθ)−Ry​sinθ0​Rx​Ry​(1−cosθ)−Rz​sinθcosθ+Ry2​(1−cosθ)Rz​Ry​(1−cosθ)+Rx​sinθ0​Rx​Rz​(1−cosθ)+Ry​sinθRy​Rz​(1−cosθ)−Rx​sinθcosθ+Rz2​(1−cosθ)0​0001​⎠⎟⎟⎞​  
需要注意的是，这个旋转矩阵虽然能够极大的避免万向节死锁的出现， _ **但并不能完全避免**_
。想要彻底避免万向节死锁问题，真正的解决方案是使用四元数(Quaternion)，它不仅更安全，而且计算会更有效率。由于我目前的学习进度还没有遇到四元数，暂时不多说，等以后遇到了再回来填坑。

## glm旋转矩阵实现

前面的缩放和位移已经把glm的基础问题扒的差不多了，关于具体的计算机实现部分暂时没有值得深扒的，主要看一下数学上的算法实现即可，下面是旋转函数实现

    
    
    template<typename T, qualifier Q>
    GLM_FUNC_QUALIFIER mat<4, 4, T, Q> rotate(mat<4, 4, T, Q> const& m, T angle, vec<3, T, Q> const& v)
    {
    	T const a = angle;
    	T const c = cos(a);
    	T const s = sin(a);
    
    	vec<3, T, Q> axis(normalize(v));
    	vec<3, T, Q> temp((T(1) - c) * axis);
    
    	mat<4, 4, T, Q> Rotate;
    	Rotate[0][0] = c + temp[0] * axis[0];
    	Rotate[0][1] = temp[0] * axis[1] + s * axis[2];
    	Rotate[0][2] = temp[0] * axis[2] - s * axis[1];
    
    	Rotate[1][0] = temp[1] * axis[0] - s * axis[2];
    	Rotate[1][1] = c + temp[1] * axis[1];
    	Rotate[1][2] = temp[1] * axis[2] + s * axis[0];
    
    	Rotate[2][0] = temp[2] * axis[0] + s * axis[1];
    	Rotate[2][1] = temp[2] * axis[1] - s * axis[0];
    	Rotate[2][2] = c + temp[2] * axis[2];
    
    	mat<4, 4, T, Q> Result;
    	Result[0] = m[0] * Rotate[0][0] + m[1] * Rotate[0][1] + m[2] * Rotate[0][2];
    	Result[1] = m[0] * Rotate[1][0] + m[1] * Rotate[1][1] + m[2] * Rotate[1][2];
    	Result[2] = m[0] * Rotate[2][0] + m[1] * Rotate[2][1] + m[2] * Rotate[2][2];
    	Result[3] = m[3];
    	return Result;
    }
    

这个函数也没啥可说的，就是对上面的旋转矩阵的实现。

# 矩阵的组合

使用矩阵进行变换的真正力量在于，根据矩阵之间的乘法，我们可以把多个变换组合到一个矩阵中。让我们看看我们是否能生成一个变换矩阵，让它组合多个变换。假设我们有一个顶点(x,y,z)(x,
y, z)(x,y,z)，我们希望将其缩放2倍，然后位移(1,2,3)(1, 2,
3)(1,2,3)个单位。我们需要一个位移和缩放矩阵来完成这些变换。结果的变换矩阵看起来像这样：  
Trans⋅Scale=(1001010200130001)⋅(2000020000200001)=(2001020200230001)
Trans\cdot Scale=\left( \begin{array}{ccc} 1 &amp; 0 &amp; 0 &amp; 1 \\\ 0
&amp;1 &amp; 0 &amp; 2 \\\ 0 &amp; 0 &amp; 1 &amp; 3 \\\ 0 &amp; 0 &amp; 0
&amp; 1 \end{array} \right) \cdot \left( \begin{array}{ccc} 2 &amp; 0 &amp; 0
&amp; 0 \\\ 0 &amp;2 &amp; 0 &amp; 0 \\\ 0 &amp; 0 &amp; 2 &amp; 0 \\\ 0 &amp;
0 &amp; 0 &amp; 1 \end{array} \right)= \left( \begin{array}{ccc} 2 &amp; 0
&amp; 0 &amp; 1 \\\ 0 &amp;2 &amp; 0 &amp; 2 \\\ 0 &amp; 0 &amp; 2 &amp; 3 \\\
0 &amp; 0 &amp; 0 &amp; 1 \end{array} \right)
Trans⋅Scale=⎝⎜⎜⎛​1000​0100​0010​1231​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​2000​0200​0020​0001​⎠⎟⎟⎞​=⎝⎜⎜⎛​2000​0200​0020​1231​⎠⎟⎟⎞​  
注意，当矩阵相乘时我们先写位移再写缩放变换的。矩阵乘法是不遵守交换律的，这意味着它们的顺序很重要。当矩阵相乘时，在最右边的矩阵是第一个与向量相乘的，所以你应该从右向左读这个乘法。建议您在组合矩阵时，先进行缩放操作，然后是旋转，最后才是位移，否则它们会（消极地）互相影响。比如，如果你先位移再缩放，位移的向量也会同样被缩放，比如向某方向移动2米，2米也许会被缩放成1米！  
用最终的变换矩阵左乘我们的向量会得到以下结果：  
Trans⋅Scale=(2001020200230001)⋅(xyz1)=(2x+12y+22y+31) Trans\cdot Scale=\left(
\begin{array}{ccc} 2 &amp; 0 &amp; 0 &amp; 1 \\\ 0 &amp;2 &amp; 0 &amp; 2 \\\
0 &amp; 0 &amp; 2 &amp; 3 \\\ 0 &amp; 0 &amp; 0 &amp; 1 \end{array} \right)
\cdot \left( \begin{array}{ccc} x \\\ y \\\ z \\\ 1 \end{array} \right)=
\left( \begin{array}{ccc} 2x+1 \\\ 2y+2 \\\ 2y+3 \\\ 1 \end{array} \right)
Trans⋅Scale=⎝⎜⎜⎛​2000​0200​0020​1231​⎠⎟⎟⎞​⋅⎝⎜⎜⎛​xyz1​⎠⎟⎟⎞​=⎝⎜⎜⎛​2x+12y+22y+31​⎠⎟⎟⎞​  
一定要注意，先执行的操作要在乘法的右边，否则结果是错误的，我们看下图  
![矩阵计算](https://img-blog.csdnimg.cn/20190826191428132.png?x-oss-
process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L211bXVmYW4wNQ==,size_16,color_FFFFFF,t_70)  
懒得手动去算了，我们找个矩阵计算器来算一下。上图中l1是缩放矩阵，m1是位移矩阵，m2是缩放在左位移在右，m3是位移在左，缩放在右。虽然先做的在右边有些反直觉，但由于矩阵乘法性质决定，先做的一定要放在右边，否则结果就是错误的，这是因为最右边的矩阵最先与待变换的向量相乘。  
设位移矩阵为A，缩放矩阵为B，被操作向量为C，完整的计算过程为A⋅B⋅CA\cdot B\cdot
CA⋅B⋅C，由于矩阵乘法满足结合律，所以有(A⋅B)⋅C=A⋅(B⋅C)(A\cdot B)\cdot C=A\cdot (B\cdot
C)(A⋅B)⋅C=A⋅(B⋅C)。因此，我们可以把这一复合变换过程理解为是从右向左依次做乘法，而根据这个顺序，右边的矩阵先和待变换矩阵进行计算。但又因为矩阵乘法不满足交换律，因此，必须把先做的事放在右边，顺序一定不能错。

## glm矩阵组合使用

上面的先缩放，后位移怎么用glm去实现呢？看下面代码

    
    
    // 首先创建一个四阶单位矩阵
    glm::mat4 trans(1.0f);
    // 由于位移是最后做的，所以位移矩阵应该放在左边，体现在代码中就是先将单位矩阵位移
    trans = glm::translate(trans, glm::vec3(1f, 2f,3f));
    trans = glm::scale(trans, glm::vec3(2, 2, 2));
    // 创建好变换矩阵后将变换矩阵传递个顶点着色器
    unsigned int transformLoc = glGetUniformLocation(shaderProgram, "transform");
    glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm::value_ptr(trans));
    

由矩阵乘法的性质决定，在代码中，后做的事要放在前面，先做的事要放在后面，我们来简单分析一下原因。  
首先创建了一个单位矩阵、一个位移向量和一个缩放向量。glm::translate函数和glm::scale函数在前面的章节中都分析过，如果想要在代码中达到位移在左，缩放在右的目的，我们首先要把单位矩阵变成位移矩阵，然后再把缩放矩阵拿到位移变换后的单位矩阵中进行缩放变换。

