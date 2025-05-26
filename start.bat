@echo off
echo 正在安装所需的Python库...
pip install yt-dlp Flask
echo 安装完成。
echo 正在启动Bilibili视频下载Web服务...
start python bilidown.py
start http://127.0.0.1:5000
pause
