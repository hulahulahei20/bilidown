document.addEventListener('DOMContentLoaded', () => {
    const videoUrlInput = document.getElementById('videoUrl');
    const downloadBtn = document.getElementById('downloadBtn');
    const statusMessage = document.getElementById('statusMessage');
    const progressBar = document.getElementById('progressBar');

    downloadBtn.addEventListener('click', async () => {
        const url = videoUrlInput.value.trim();
        if (!url) {
            statusMessage.textContent = '请输入Bilibili视频URL！';
            statusMessage.style.color = 'red';
            return;
        }

        statusMessage.textContent = '正在发送下载请求...';
        statusMessage.style.color = 'orange';
        downloadBtn.disabled = true;
        progressBar.style.width = '0%'; // 重置进度条

        try {
            const response = await fetch('http://127.0.0.1:5000/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url: url })
            });

            const data = await response.json();

            if (response.ok && data.download_id) {
                statusMessage.textContent = data.message;
                statusMessage.style.color = 'green';
                
                const downloadId = data.download_id;
                const interval = setInterval(async () => {
                    const progressResponse = await fetch(`http://127.0.0.1:5000/progress/${downloadId}`);
                    const progressData = await progressResponse.json();

                    let displayMessage = progressData.status;
                    if (progressData.title && progressData.progress >= 100) {
                        displayMessage = `视频 '${progressData.title}' 下载完成！`;
                    }
                    statusMessage.textContent = displayMessage;
                    progressBar.style.width = `${progressData.progress}%`;

                    if (progressData.progress >= 100 || progressData.status.includes('完成') || progressData.status.includes('错误')) {
                        clearInterval(interval);
                        downloadBtn.disabled = false;
                        if (progressData.status.includes('错误')) {
                            statusMessage.style.color = 'red';
                        } else {
                            statusMessage.style.color = 'green';
                        }
                    }
                }, 1000); // 每秒更新一次进度
            } else {
                statusMessage.textContent = `下载失败: ${data.error || '未知错误'}`;
                statusMessage.style.color = 'red';
                downloadBtn.disabled = false;
            }
        } catch (error) {
            statusMessage.textContent = `请求失败: ${error.message}`;
            statusMessage.style.color = 'red';
            downloadBtn.disabled = false;
        }
    });
});
