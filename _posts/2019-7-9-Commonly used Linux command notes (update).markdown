---
layout: post
title: 常用Linux命令笔记（随时更新）
date: 发布于2019-07-09 17:54:36 +0800
categories: 测试结果杂记
tag: 4
---

* content
{:toc}

### 文章目录

  * 系统命令

<!-- more -->
    * 网络相关
    * 进程相关
    * 压缩解压
    * 系统服务
    * 挂载
    * rpm操作
    * awk
    * 文件相关
  * svn命令
  * 查找命令
  * vim命令
  * git命令
  * gdb命令
  * 奇怪的乱入？就是想找个地方记录几条命令而已

# 系统命令

## 网络相关

    
    
    查看端口进程：lsof -i:9527
    查看进程的线程：ps -T -p <pid>
    查看网络连接状况：netstat -atunvl
    查看进程的端口号：netstat -anop | grep server
    查看端口号的进程的线程：lsof -i:9527 | awk '{print $2}' | sed -n '2p' | xargs ps -Tp
    抓包：tcpdump -i eth0 tcp port 12303 -w 1.pcap
    

## 进程相关

    
    
    杀死指定进程：ps aux | grep a.out | awk '{print $2}' | sed -n 1p | xargs kill -9
    ps aux | grep a.out | sed -n 1p | awk '{print $2}' |xargs top -b -H -p
    

## 压缩解压

    
    
    解压tar.xz：tar xvJf xxx.tar.xz
    查看不解压：tar tvf vsftpd.tar.gz
    

## 系统服务

    
    
    启动系统服务：service crond start
                            /etc/init.d/cron start
    停止系统服务：stop
    查看服务状态：service crond status
    

## 挂载

    
    
    挂载远程samba：sudo mount -t cifs //47.94.162.207/share aliCloud -o username=root,password=password,port=1314
    mount -t cifs -o username=user,password=password//192.168.180.128/work /media/
    

## rpm操作

    
    
    rpm安装：rpm -ivh file.rpm
    rpm安装查询：rpm -qa | grep file
    rpm安装路径查询：rpm -ql | grep file
    rpm卸载：rpm -e
    不安装但是获取rpm包中的文件 
    使用工具rpm2cpio和cpio 
    rpm2cpio xxx.rpm | cpio -vi 
    rpm2cpio xxx.rpm | cpio -idmv 
    rpm2cpio xxx.rpm | cpio --extract --make-directories 
    参数i和extract相同，表示提取文件。v表示指示执行进程 
    d和make-directory相同，表示根据包中文件原来的路径建立目录 
    m表示保持文件的更新时间。 
    

## awk

    
    
    统计文件空字符率：cat *.txt | awk -F"|" 'BEGIN{a = 0}{if($5!=""){a++}}END{printf("%d/%d=%f\n", a, NR, a*1.0/NR)}'
    多个文件每行的指定列相加
    awk -F"|" '{a[1,FNR]=$1;a[2,FNR]=$2;a[3,FNR]=$3;a[6,FNR]=$6; \
    {if(4==NF)a[4,FNR]=0;a[4,FNR]+=strtonum($4)} \
    {if(5==NF)a[5,FNR]=0;a[5,FNR]+=strtonum($5)}} \
    END{for(i=1;i<=FNR;i++) \
    printf("%d|%d|%d|%d|%d|%d\r\n",a[1,FNR],a[2,FNR],a[3,FNR],a[4,i],a[5,i],a[6,FNR]) \
    }' *.txt 
    
    使用awk处理一条命令不同参数多次执行的情况
    首先将待使用的参数写入一个文件，然后执行下面命令
     awk '{a="date -d @"$1" \"+%Y/%m/%d %k:%M:%S\"";system(a)}' time.txt 
    

## 文件相关

    
    
    文件按时间逆序排序：ls -tl |more
    递归转码所有文件：du | awk '{print $2}' | xargs dos2unix
    查看第一行的列数：sed -n 1p a.txt | awk -F "|" '{print NF}'
    查看当前目录大小：du -hs
    查看硬盘使用情况：df -h
    清空当前目录下所有子目录内容，但保留当前目录的文件和子目录本身：rm -rf `ls -F | grep '/$' | awk '{print $1 "*"}'`
    查看文件行列数：awk -F '| '{print NF}' filename|sort|uniq -c
    

# svn命令

    
    
    svn批量添加文件：svn st | grep '^\?' | tr '^\?' ' ' | sed 's/^[ \t]*//' | sed 's/[ ]/\\ /g' | xargs svn add
    

# 查找命令

    
    
    查找含有某字符串的所有文件：grep -rn "sf_base64encode" *
    * : 表示当前目录所有文件，也可以是某个文件名
    -r 是递归查找
    -n 是显示行号
    -R 查找所有文件包含子目录
    -i 忽略大小写
    
    下面是一些有意思的命令行参数：
    grep -i pattern files ：不区分大小写地搜索。默认情况区分大小写， 
    grep -l pattern files ：只列出匹配的文件名， 
    grep -L pattern files ：列出不匹配的文件名， 
    grep -w pattern files ：只匹配整个单词，而不是字符串的一部分（如匹配‘magic’，而不是‘magical’）， 
    grep -C number pattern files ：匹配的上下文分别显示[number]行， 
    grep pattern1 | pattern2 files ：显示匹配 pattern1 或 pattern2 的行， 
    grep pattern1 files | grep pattern2 ：显示既匹配 pattern1 又匹配 pattern2 的行。 
    
    这里还有些用于搜索的特殊符号：
    \< 和 \> 分别标注单词的开始与结尾。
    例如： 
    grep man * 会匹配 ‘Batman’、‘manic’、‘man’等， 
    grep '\<man' * 匹配‘manic’和‘man’，但不是‘Batman’， 
    grep '\<man\>' 只匹配‘man’，而不是‘Batman’或‘manic’等其他的字符串。 
    '^'：指匹配的字符串在行首， 
    '$'：指匹配的字符串在行尾，
    
    xargs配合grep查找
    find -type f -name '*.php'|xargs grep 'GroupRecord'
    
    批量替换
    find -name '要查找的文件名' | xargs perl -pi -e 's|被替换的字符串|替换后的字符串|g'
    

# vim命令

    
    
    :s/str1/str2/ 替换当前行第一个 str1 为 str2 
    :s/str1/str2/g 替换当前行中所有 str1 为 str2 
    :m,ns/str1/str2/ 替换第 n 行开始到最后一行中每一行的第一个 str1 为 str2 
    :m,ns/str1/str2/g 替换第 n 行开始到最后一行中所有的 str1 为 str2 
    :%s/str1/str2/g（等同于 :g/str1/s//str2/g 和 :1,$ s/str1/str2/g ） 替换文中所有 str1 为 str2 
    :g/something/d 删除包含something的整行
    从替换命令可以看到，g 放在命令末尾，表示对搜索字符串的每次出现进行替换；不加 g，表示只对搜索
    

# git命令

    
    
    本地库添加文件：git add Makefile
    本地库提交文件：git commit Makefile -m "add makefile"
    本地库推送至远程库：git push -u origin master
    查看本地分支：git branch
    查看远程分支：git branch -r
    查看远程和本地的所有分支：git branch -a
    删除本地分支：git branch -d unblock_io
    删除远程分支：git branch -r -d origin/unblock_io
    推送本地分支到远程：git push origin cluster:cluster
    切换分支：git checkout master
    合并分支到当前分支：git merge prefork_epoll
    获取远程所有分支：git branch -r | grep -v '\->' | while read remote; do git branch --track "${remote#origin/}" "$remote"; done
    更新远程所有分支：git branch | awk 'BEGIN{print "echo ****Update all local branch...@daimon***"}{if($1=="*"){current=substr($0,3)};print a"git checkout "substr($0,3);print "git pull --all";}END{print "git checkout " current}' |sh
    
    删除readme1.txt的跟踪，并保留在本地：git rm --cached readme1.txt
    删除readme1.txt的跟踪，并且删除本地文件：git rm --f readme1.txt
    删除 untracked files：git clean -f
    连 untracked 的目录也一起删掉：git clean -fd
    连 gitignore 的untrack 文件/目录也一起删掉 （慎用，一般这个是用来删掉编译出来的 .o之类的文件用的）：git clean -xfd
    在用上述 git clean 前，墙裂建议加上 -n 参数来先看看会删掉哪些文件，防止重要文件被误删：git clean -nxfd；git clean -nf；git clean -nfd
    
    查看标签：git tag
    添加标签：git tag <name>
    补打标签：git log --pretty=oneline --abbrev-commit      git tag <name> commit id  如：git tag v0.9 6224937
    查看标签信息：git show <tagname>>
    还可以创建带有说明的标签，用-a指定标签名，-m指定说明文字：git tag -a v0.1 -m "version 0.1 released" 3628164
    查看远程所有标签和分支：git ls-remote
    删除标签：git tag -d v0.1
    推送标签到远程：git push origin <tagname>
    推送所有标签到远程：git push origin --tags
    删除远程标签：先删本地，再删远程：git tag -d v0.9    git push origin :refs/tags/v0.9
    切换标签：git checkout v0.1.5
    
    导出干净代码：
    git archive --format=zip --output=bitcoin.zip v0.6.0
    git archive 1.0 | bzip2 > v1.0.tar.bz2
    git archive --format=tar 1.0 | gzip > v1.0.tar.gz
    git archive --format zip --output "./output.zip" master -0
    
    本地恢复commit
    git log 找到commit哈希
    git branch 分支名 commit哈希
    git checkout 分支名
    
    强制恢复commit
    git reset --hard commit哈希
    
    恢复本地修改：git status | grep modified | awk '{print $2}' | xargs git checkout
    恢复本地删除：git status | grep deleted | awk '{print $2}' | xargs.exe  git checkout 
    
    分支改名
    先修改本地分支名：git branch -m old_branch new_branch
    然后推送到远程分支：git push origin new_branch
    接下来设置新的分支追踪：git push -u origin new_branch
    最后删除远程旧分支：git branch -r -d origin/old_branch 
    

# gdb命令

    
    
    条件断点：b 13 if i == 8
    查看断点信息：info b
    堆栈操作： up n 向上回退n个栈帧（更外层），n默认为1. 
              down n 向下前进n个栈帧（更内层），n默认为1.
    set scheduler-locking [off|on|step]
    
    值得注意的是，在使用step或者continue命令调试当前被调试线程的时候，其他线程也是同时执行的，怎么只让被调试程序执行呢？通过这个命令就可以实现这个需求。
    
    off：不锁定任何线程，也就是所有线程都执行，这是默认值。
    
    on：只有当前被调试程序会执行。?
    
    step：在单步的时候，除了next过一个函数的情况(熟悉情况的人可能知道，这其实是一个设置断点然后continue的行为)以外，只有当前线程会执行。
    
    打印结构体：set print pretty on
    字符串显示不全：set print elements 0
    

# 奇怪的乱入？就是想找个地方记录几条命令而已

    
    
    查看Windows激活期限：在运行中执行slmgr.vbs -xpr
    

