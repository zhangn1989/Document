---
layout: post
title: 康威生命游戏
date: 发布于2020-01-18 15:28:11 +0800
categories: 测试结果杂记
tag: 4
---

简介看[这里](https://zh.wikipedia.org/wiki/%E5%BA%B7%E5%A8%81%E7%94%9F%E5%91%BD%E6%B8%B8%E6%88%8F)  

<!-- more -->
为保证通用性，逻辑层使用C语言的标准库去做

    
    
    #ifndef __H__CELLULAR_AUTOMATA__
    #define __H__CELLULAR_AUTOMATA__
    #ifdef __cplusplus
    extern "C" {
    #endif // __cplusplus
    	int startGame(int grid, unsigned int seed, int initCount, int initSize, double initDensity);
    	void stopGame();
    	void evolution();
    	int getValue(int i, int j);
    #ifdef __cplusplus
    }
    #endif // __cplusplus
    #endif // __H__CELLULAR_AUTOMATA__
    
    #include "CellularAutomata.h"
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    
    static int *g_world;
    static int *g_mirror;
    static int g_grid;
    
    #define setValue(i, j, value)	(*(g_world + g_grid * (i) + (j)) = (value))
    
    int getValue(int i, int j)
    {
    	return *(g_world + g_grid * i + j);
    }
    
    static int surroundingLivingCells(int i, int j)
    {
    	int ii, jj;
    	int sum = 0;
    
    	ii = i - 1; 
    	jj = j - 1;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	ii = i - 1;
    	jj = j;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	ii = i - 1;
    	jj = j + 1;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	ii = i;
    	jj = j - 1;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	ii = i;
    	jj = j + 1;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	ii = i + 1;
    	jj = j - 1;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	ii = i + 1;
    	jj = j;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	ii = i + 1;
    	jj = j + 1;
    	if (ii > 0 && jj > 0)
    		if (getValue(ii, jj) == 1)
    			++sum;
    
    	return sum;
    }
    
    int startGame(int grid, unsigned int seed, int initCount, int initSize, double initDensity)
    {
    	int i, j, k, value;
    	g_grid = grid;
    	g_world = (int *)malloc(grid * grid * sizeof(int));
    	if (!g_world)
    		return -1;
    	g_mirror = (int *)malloc(grid * grid * sizeof(int));
    	if (!g_mirror)
    	{
    		delete g_world;
    		g_world = NULL;
    		return -1;
    	}
    
    	memset(g_world, 0, grid * grid * sizeof(int));
    	memset(g_mirror, 0, grid * grid * sizeof(int));
    
    	srand(seed);
    
    	for (k = 0; k < initCount; ++k)
    	{
    		int startx = rand() % grid - initSize;
    		int endx = startx + initSize;
    		int starty = rand() % grid - initSize;
    		int endy = starty + initSize;
    
    		for (i = startx; i < endx; ++i)
    		{
    			for (j = starty; j < endy; ++j)
    			{
    				int density = 100 / (initDensity * 100);
    				value = rand() % density;
    				if (value == 0)
    					setValue(i, j, 1);
    			}
    		}
    	}
    
    	memcpy(g_mirror, g_world, grid * grid * sizeof(int));
    
    	return 0;
    }
    
    void stopGame()
    {
    	g_grid = 0;
    	free(g_world);
    	free(g_mirror);
    	g_world = NULL;
    	g_mirror = NULL;
    }
    
    void evolution()
    {
    	int i, j;
    	for (i = 0; i < g_grid; ++i)
    	{
    		for (j = 0; j < g_grid; ++j)
    		{
    			int count = surroundingLivingCells(i, j);
    			if (getValue(i, j) > 0)
    			{
    				if (count == 2 || count == 3)
    					continue;
    
    				if (count < 2 || count > 3)
    				{
    					*(g_mirror + g_grid * i + j) = 0;
    				}
    			}
    			else
    			{
    				if (count == 3)
    				{
    					*(g_mirror + g_grid * i + j) = 1;
    				}
    			}
    		}
    	}
    
    	memcpy(g_world, g_mirror, g_grid * g_grid * sizeof(int));
    }
    
    

接下来是界面，这部分就随意了，把逻辑层的数据用界面表现出来就行，这里随便用qt来画一画

    
    
    #pragma once
    
    #include <QtWidgets/QMainWindow>
    #include "ui_GameOfLife.h"
    
    class QColorDialog;
    class GameOfLife : public QMainWindow
    {
    	Q_OBJECT
    
    public:
    	GameOfLife(QWidget *parent = Q_NULLPTR);
    
    protected:
    	void paintEvent(QPaintEvent *event) override;
    
    
    private:
    	Ui::GameOfLifeClass ui;
    	int m_grid;
    	bool m_isStart;
    	QTimer *m_timer;
    	QColor m_colorGrid;
    	QColor m_colorLife;
    	QColor m_colorDeath;
    
    private slots:
    	void onTimerTimeout();
    	void onPushButtonClicked(bool checked = false);
    	void onPushButtonGridClicked(bool checked = false);
    	void onPushButtonLifeClicked(bool checked = false);
    	void onPushButtonDeathClicked(bool checked = false);
    };
    
    
    #include "GameOfLife.h"
    #include "CellularAutomata.h"
    #include <QTimer>
    #include <QDateTime>
    #include <QPainter>
    #include <QResizeEvent>
    #include <QColorDialog>
    
    GameOfLife::GameOfLife(QWidget *parent)
    	: QMainWindow(parent)
    {
    	ui.setupUi(this);
    	m_grid = 0;
    	m_isStart = false;
    	m_colorGrid = Qt::red;
    	m_colorLife = Qt::black;
    	m_colorDeath = Qt::white;
    	m_timer = new QTimer(this);
    	ui.pushButton->setText("start");
    	connect(m_timer, &QTimer::timeout, this, &GameOfLife::onTimerTimeout);
    	connect(ui.pushButton, &QPushButton::clicked, this, &GameOfLife::onPushButtonClicked);
    	connect(ui.pushButton_grid, &QPushButton::clicked, this, &GameOfLife::onPushButtonGridClicked);
    	connect(ui.pushButton_life, &QPushButton::clicked, this, &GameOfLife::onPushButtonLifeClicked);
    	connect(ui.pushButton_death, &QPushButton::clicked, this, &GameOfLife::onPushButtonDeathClicked);
    }
    
    void GameOfLife::onTimerTimeout()
    {
    	if (!m_isStart)
    		return;
    	evolution();
    	update();
    }
    
    void GameOfLife::onPushButtonClicked(bool checked)
    {
    	if (m_isStart)
    	{
    		m_isStart = false;
    		m_timer->stop();
    		m_grid = 0;
    		stopGame();
    		ui.pushButton->setText("start");
    	}
    	else
    	{
    		m_grid = ui.spinBox->value();
    		if (startGame(m_grid, QDateTime::currentDateTime().toTime_t(), 
    			ui.spinBox_2->value(), ui.spinBox_3->value(), 
    			ui.doubleSpinBox_2->value()) < 0)
    			return;
    		m_isStart = true;
    		m_timer->setInterval(ui.doubleSpinBox->value() * 1000);
    		m_timer->start();
    		ui.pushButton->setText("stop");
    	}
    }
    
    void GameOfLife::onPushButtonGridClicked(bool checked)
    {
    	QColor c = QColorDialog::getColor(m_colorGrid, this);
    	if (c.isValid())
    		m_colorGrid = c;
    }
    
    void GameOfLife::onPushButtonLifeClicked(bool checked)
    {
    	QColor c = QColorDialog::getColor(m_colorLife, this);
    	if (c.isValid())
    		m_colorLife = c;
    }
    
    void GameOfLife::onPushButtonDeathClicked(bool checked)
    {
    	QColor c = QColorDialog::getColor(m_colorDeath, this);
    	if (c.isValid())
    		m_colorDeath = c;
    }
    
    void GameOfLife::paintEvent(QPaintEvent *event)
    {
    	int i, j, value;
    	QPainter painter(this);
    	QVector<int>::iterator it;
    	int w = width();
    	int h = height();
    	painter.setPen(m_colorGrid);
    
    	if (m_grid > 0)
    	{
    		w = w / m_grid;
    		h = h / m_grid;
    		for (i = 0; i < m_grid; ++i)
    		{
    			for (j = 0; j < m_grid; ++j)
    			{
    				value = getValue(i, j);
    				if (value)
    					painter.setBrush(m_colorLife);
    				else
    					painter.setBrush(m_colorDeath);
    
    				painter.drawRect(i * w, j * h, w, h);
    			}
    		}
    	}
    	QMainWindow::paintEvent(event);
    }
    
    
    

* content
{:toc}


