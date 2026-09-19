# -*- coding: utf-8 -*-
"""网页音频提取 - 解析器单元验证 + RSS 播客源测试"""
import re
import urllib.request
from test_extract import find_audio_urls, fetch

# 本地构造 HTML 验证解析器
SAMPLE_HTML = '''
<html><head>
<meta property="og:audio" content="https://cdn.example.com/song/123.mp3">
<meta property="og:audio:secure_url" content="https://cdn.example.com/song/123.mp3?token=abc">
</head><body>
<audio controls src="/media/voice.mp3"></audio>
<audio controls><source src="https://cdn2.example.com/track.m4a?x=1" type="audio/mp4"></audio>
<video src="https://v.example.com/clip.mp4"></video>
<script>window.__DATA = {"audioUrl": "https://api.example.com/audio/9.flac", "src": "https://x.example.com/a.ogg"};</script>
<a href="https://files.example.com/song.wav">song</a>
</body></html>
'''
urls = find_audio_urls(SAMPLE_HTML, 'https://page.example.com/listen/')
print('=== 解析器本地验证 ===')
for u in urls:
    print(' ', u)
assert any(u.endswith('.mp3') for u in urls), 'mp3 直链未解析'
assert any('media/voice.mp3' in u for u in urls), '相对路径未转绝对'
print('解析器验证通过\n')

# RSS 播客源测试（enclosure 里的 mp3）
try:
    rss = fetch('https://www.npr.org/rss/podcast.php?id=510289').read().decode('utf-8', errors='replace')
    enc = re.findall(r'<enclosure[^>]*?url="([^"]+\.(?:mp3|m4a|ogg)[^"]*)"', rss, re.I)
    print('=== NPR 播客 RSS 测试 ===')
    print('RSS 长度:', len(rss), 'enclosure 音频:', enc[:3] or '无')
except Exception as e:
    print('NPR RSS 测试失败:', e)
