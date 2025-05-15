<h1 align="center">RobotAnchor直播机器人</h1>
<p align="center">
  一个基于PyQt5开发的的智能化直播运营工具
  <br>
    <a href="https://www.python.org/downloads/release/python-362/">
    <img src="https://img.shields.io/badge/python-3.8.0-blue.svg?style=flat-square" alt="Python 3.8.0" />
  </a>
  <a href="https://pypi.org/project/PyQt5/">
    <img src="https://img.shields.io/badge/pyqt5-5.15.11-blue.svg?style=flat-square" alt="pyqt5 5.15.11" />
  </a>
  <a href="https://github.com/harmfl/RobotAnchor/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-BSD-green" alt="BSD-3 License" />
  </a>
  <br>
  <a href="https://github.com/ayangweb/BongoCat/releases">
      <img
        alt="Windows"
        src="https://img.shields.io/badge/-Windows-blue?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB0PSIxNzI2MzA1OTcxMDA2IiBjbGFzcz0iaWNvbiIgdmlld0JveD0iMCAwIDEwMjQgMTAyNCIgdmVyc2lvbj0iMS4xIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHAtaWQ9IjE1NDgiIHdpZHRoPSIxMjgiIGhlaWdodD0iMTI4Ij48cGF0aCBkPSJNNTI3LjI3NTU1MTYxIDk2Ljk3MTAzMDEzdjM3My45OTIxMDY2N2g0OTQuNTEzNjE5NzVWMTUuMDI2NzU3NTN6TTUyNy4yNzU1NTE2MSA5MjguMzIzNTA4MTVsNDk0LjUxMzYxOTc1IDgwLjUyMDI4MDQ5di00NTUuNjc3NDcxNjFoLTQ5NC41MTM2MTk3NXpNNC42NzA0NTEzNiA0NzAuODMzNjgyOTdINDIyLjY3Njg1OTI1VjExMC41NjM2ODE5N2wtNDE4LjAwNjQwNzg5IDY5LjI1Nzc5NzUzek00LjY3MDQ1MTM2IDg0Ni43Njc1OTcwM0w0MjIuNjc2ODU5MjUgOTE0Ljg2MDMxMDEzVjU1My4xNjYzMTcwM0g0LjY3MDQ1MTM2eiIgcC1pZD0iMTU0OSIgZmlsbD0iI2ZmZmZmZiI+PC9wYXRoPjwvc3ZnPg=="
      />
    </a >
    </a >
    <a href="https://github.com/ayangweb/BongoCat/releases">
      <img src="https://img.shields.io/badge/version-v0.4.0-orange" alt="version-3" />
    </a >
  <br>
  <br />



 ## 目录

- [概览](#概览)
- [python环境配置](#python环境配置)
- [运行截图](#运行截图)

<br>

## 概览

这是一个针对抖音平台的自动直播机器人，其包括直播弹幕抓取弹幕，TTS 语音生成回复弹幕问题，感谢粉丝礼物，声卡切换等核心功能。技术栈包括PyQt5信号槽机制和、QThread 多线程优化、Py爬虫、TTS等等。

这里支持两种配置，一种是[Python环境配置](#python环境配置)，需要自己下载环境，通过IDE运行，可以通过代码详细查看各个部分的结构；另一种则是用包装好的EXE，不用配置环境，直接使用就可。

系统的核心功能使用指引：
- **弹幕爬取**：请在直播间号码下方输入直播房间号，然后点击开始抓取弹幕就可以了，启动后会开启一个新的浏览器，这是正常的。

- **弹幕回复**：问题回复是通过主播的账号往直播间发送弹幕实现的。先开启主播登录，再在弹幕回复配置进行配置，每个问题有三个属性：问题关键词，答案和权重；当检测到多个问题时，会根据权重来安排回复的优先级；关于问题的添加这里支持直接输入以加入问题列表或者从txt导入，txt的格式可以参考测试问题集；之后可以点击查看列表，最后点击锁定当前配置即可保存。

- **新用户欢迎**：新用户欢迎会对新进入直播间的用户进行语音欢迎。要开启新用户欢迎请先选择声音模型，这里支持14种EDGE接口的TTS模型，然后点击开启语音欢迎就行了。用户欢迎的优先级比语音场控高，假如先前执行语音场控，新用户进入后会优先进行用户欢迎。

- **感谢礼物**：感谢礼物会对发送礼物的用户进行自定义感谢语感谢（这里并没有做针对某个礼物的区分，因为抖音礼物类型太多了）。要开启礼物感谢请先打开感谢礼物配置，然后选择声音模型，之后可以直接输入导入也可以txt导入，生成后可以点击查看当前感谢语列表，最后点击锁定当前配置即可保。感谢礼物任务的优先级是最高的，假如同时有用户欢迎和语音场控的任务，会优先进行感谢礼物。

- **语音场控**：语音场控会在没有礼物感谢和语音欢迎任务时不断播放列表中的语音。其配置流程和感谢礼物类似，这里不再赘述。

<br>

## python环境配置

### 部署前准备：
建议使用Anaconda配置Py虚拟环境，Pycharm或VScode等主流IDE运行，Anaconda和IDE的配置流程网上资源很多，这里就不再重复了。

### 开始部署：
（1）打开Anaconda Prompt运行下面的指令
```sh
conda create -n 你的环境名 python==3.8
```
（2）激活环境
```sh
conda activate 你的环境名
```
（3）到下载项目对应的地址上
```sh
cd 你的项目地址
```
（4）下载所需要的包
```sh
pip install -r requirement.txt
```
（5）在Pycharm或VScode运行即可

<br>

## 运行截图

![主页](https://github.com/user-attachments/assets/b964fcd5-07a6-4baa-8152-0d0c2a6e51aa)
![问题管理](https://github.com/user-attachments/assets/5d86a92c-397f-4428-bbf5-1c7e79d312fb)
![礼物配置](https://github.com/user-attachments/assets/1e02cc58-5821-4551-9499-aca942b6917a)
![场控配置](https://github.com/user-attachments/assets/3fb6da38-749b-44bd-bbb2-2671467cd317)
![声卡切换](https://github.com/user-attachments/assets/cbd29219-fcab-4562-ac28-de08ecc870ef)