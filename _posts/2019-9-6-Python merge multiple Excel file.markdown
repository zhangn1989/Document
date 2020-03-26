---
layout: post
title: Python合并多个Excel文件
date: 发布于2019-09-06 12:06:41 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}


    import os
<!-- more -->

    import xlrd
    import xlwt
    
    # 文件所在目录
    rootdir = "."
    list = os.listdir(rootdir)
     # 创建输出文件
    book=xlwt.Workbook(encoding="utf-8",style_compression=0)
    sheet = book.add_sheet('test01')
    
    # 输出文件行索引
    outrow = 0
    
    # 遍历目录文件
    for i in range(0, len(list)):
        # 判断后缀名过滤文件
        path = os.path.join(rootdir, list[i])
        suffix = path.split(".")[-1]
        if suffix == "xls" or suffix == "xlsx" :
            # 打开文件，获取所有的表名
            workbook=xlrd.open_workbook(path)
            names=workbook.sheet_names()
            # 遍历所有的表
            for name in names:
                # 通过sheet名获得sheet对象
                worksheet=workbook.sheet_by_name(name)
                # 获取行列号
                nrows=worksheet.nrows
                ncols=worksheet.ncols
                # 循环读取每一行
                for nrow in range(nrows): 
                    # 循环读取当前行的所有列
                    for ncol in range(ncols):
                        # 获取当前行列号的单元数据，写入输出文件
                        data = worksheet.row_values(nrow)[ncol]
                        sheet.write(outrow,ncol,data)
                    # 输出文件行号累加
                    outrow += 1
    
    # 保存到硬盘上
    book.save('test1.xls') 
    

