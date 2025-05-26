# -*- coding: utf-8 -*-
import yt_dlp
import os
from flask import Flask, request, jsonify, send_from_directory
import threading
import time

app = Flask(__name__)

# 用于存储下载进度的全局字典
# key: 视频URL (或一个唯一的下载ID), value: { 'status': '...', 'progress': 0 }
download_status = {}

def download_bilibili_video_backend(url, download_id):
    """
    下载Bilibili视频到本地，并更新全局下载状态。
    """
    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '')
            try:
                progress_val = float(p)
            except ValueError:
                progress_val = 0.0
            download_status[download_id] = {'status': f"下载进度: {d['_percent_str']} {d['_eta_str']}", 'progress': progress_val}
        elif d['status'] == 'finished':
            download_status[download_id] = {'status': f"视频 '{d.get('title', '未知视频')}' 下载完成！", 'progress': 100.0, 'title': d.get('title', '未知视频')}
        else:
            download_status[download_id] = {'status': d['status'], 'progress': 0.0, 'title': None}

    ydl_opts = {
        'format': 'bestvideo[ext=mp4],bestaudio[ext=m4a]',
        'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),
        'noplaylist': True,
        'retries': 10,
        'fragment_retries': 10,
        'concurrent_fragments': 5,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'verbose': False,
        'progress_hooks': [progress_hook],
    }

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            # 确保在下载成功时也更新最终状态和标题
            download_status[download_id] = {'status': f"视频 '{info_dict.get('title', '未知视频')}' 和音频已下载完成！", 'progress': 100.0, 'title': info_dict.get('title', '未知视频')}
            return True, f"视频 '{info_dict.get('title', '未知视频')}' 和音频已下载完成！"
    except Exception as e:
        download_status[download_id] = {'status': f"下载视频时发生错误: {e}", 'progress': 0.0, 'title': None}
        return False, f"下载视频时发生错误: {e}"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "URL不能为空"}), 400

    # 为每个下载任务生成一个唯一的ID
    download_id = str(time.time()) # 简单地使用时间戳作为ID
    download_status[download_id] = {'status': '开始下载...', 'progress': 0.0}

    # 在新线程中运行下载
    thread = threading.Thread(target=lambda: download_bilibili_video_backend(video_url, download_id))
    thread.start()

    return jsonify({"message": "下载请求已发送，请稍候...", "download_id": download_id}), 202 # 返回202表示请求已接受

@app.route('/progress/<download_id>', methods=['GET'])
def get_progress(download_id):
    status = download_status.get(download_id, {'status': '等待中...', 'progress': 0.0})
    return jsonify(status), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
