---
layout: post
title: Qt的拖放功能
date: 发布于2019-12-03 18:21:31 +0800
categories: Qt
tag: 4
---

* content
{:toc}

对于源控件，需要重写鼠标按下事件和鼠标移动事件

<!-- more -->

    
    
    class TweenMouldListWidget : public QListWidget
    {
    	Q_OBJECT
    
    public:
    	TweenMouldListWidget(QWidget *parent = Q_NULLPTR);
    	~TweenMouldListWidget();
    
    protected:
    	virtual void mousePressEvent(QMouseEvent *event) override;
    	virtual void mouseMoveEvent(QMouseEvent *event) override;
    
    private:
    	QPoint m_startPos;
    };
    
    void TweenMouldListWidget::mousePressEvent(QMouseEvent *event)
    {
    	// 左键按下，记录一个按下的位置
    	if (event->button() == Qt::LeftButton)
    		m_startPos = event->pos();
    
    	QListWidget::mousePressEvent(event);
    }
    
    void TweenMouldListWidget::mouseMoveEvent(QMouseEvent *event)
    {
    	if (event->buttons() & Qt::LeftButton)
    	{
    		// 计算一个移动距离，防止鼠标抖动
    		int distance = (event->pos() - m_startPos).manhattanLength();
    		if (distance >= QApplication::startDragDistance())
    		{
    			// 封装传递数据
    			QListWidgetItem *item = currentItem();
    			QVariant var = item->data(Qt::UserRole);
    		
    			QMimeData *mimeData = new QMimeData;
    			mimeData->setText(item->text());
    			mimeData->setImageData(var);
    		
    			QDrag *drag = new QDrag(this);
    			drag->setMimeData(mimeData);
    			drag->exec(Qt::MoveAction);
    		}
    	}
    	QListWidget::mouseMoveEvent(event);
    }
    

对于目的控件，首先需要设置启用拖放属性，一般在构造函数中添加下面这一句

    
    
    setAcceptDrops(true);
    

然后重写dragEnterEvent和dropEvent

    
    
    void TimeLine::dragEnterEvent(QDragEnterEvent *event)
    {
    	// 这个方法必须重写且必须调用下面这一句，否则控件不接收拖放
    	event->acceptProposedAction();
    }
    
    void TimeLine::dropEvent(QDropEvent *event)
    {
    	// 取出传递的数据，然后做其他事情
    	const QMimeData* pData = event->mimeData();
    	QVariant var = pData->imageData();
    	TweenMould tween = var.value<TweenMould>();
    }
    

