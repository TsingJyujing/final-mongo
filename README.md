# Final Mongo —— MongoDB数据拯救者

**English documentation is preparing.**

## 简介
在日常工作中，MongoDB可能因为各种原因挂了，或者只剩下几个文件了，但是起不来，这个时候我们优先恢复能恢复的collection。

本项目仅能修复有线老虎（WiredTiger）引擎中、

通过WiredTiger提供的工具，我们可以尽可能的恢复数据，需要的准备如下：

1. 本地编译WT工具；
2. 本地有MongoDB可执行文件（含utilities）；
3. 本地需要能读取到已经挂掉的MongoDB的目录；
4. 有一个供恢复后数据回写的新库；
5. 安装好需要依赖的包。

需要说明的是，表结构最好定期备份，如果这个部分损坏了就没办法通过软件读取配置信息，这个时候恢复的数据含义只能靠推测。

**做好灾备，所谓灾备是灾难前备份，不是灾后重建。不是每一次崩溃，都可以恢复。**
这也是为什么这个项目叫FinalMongo的原因，这个项目应该视作最终手段，一个不一定奏效，用起来还贼麻烦的最终手段……

## 工作原理

如果你的MongoDB还能挣扎一下（还能起来，但是在做某些操作的时候崩溃之类的），请先用表结构备份工具备份表结构。如果已经挣扎不了了，请关闭MongoDB服务，尝试恢复配置信息。

通过WT工具尽可能的恢复出*.wt文件中的数据，随后将数据dump出来，导入到本地的MongoDB中去。

至于导入到哪个表中去，全靠配置信息的指引，如果没有配置文件，需要手动指定备份到哪个数据库中去。

## 环境准备

（最好准备一台单独的服务器/PC，备战备荒，什么？你们连一台计算机都搞不出来？那还恢复什么数据啊洗洗睡吧）

### 安装必需的Python包
```bash
sudo apt install python3-dev python3-setuptools
# 什么？你用的不是Debian的Linux所以不会了？啊……晚安
pip3 install pymongo pyyaml
```

### 编译WiredTiger工具
根据[Building and installing WiredTiger on POSIX](http://source.wiredtiger.com/3.0.0/build-posix.html)的指点安装。

MongoDB默认使用Snappy进行压缩的，所以需要注意的是，使用`./configure --enable-snappy`进行配置，否则不会编译snappy相关的so。

### 准备MongoDB的二进制文件
自己去[MongoDB官网](https://www.mongodb.com/)下载。

### 准备挂载备份文件
一般来说，建议将文件放在本地，并且设为只读属性。
如果在远程的服务器上，一时半会拷不下来，建议使用sshfs挂到本地：

例如：

```bash
mkdir -p /tmp/remote_mongo
sshfs user@address:/var/lib/mongo
```

### 配置`config.py`配置文件
文件中有丰富的注释