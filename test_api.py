# -*- coding: utf-8 -*-
"""端到端验证 /api/extract 与 /api/download"""
import json
import sys
import threading
from http.client import HTTPConnection

sys.path.insert(0, r'D:\桌面\asd2\format-forge')
from main import Handler  # noqa: E402
from http.server import ThreadingHTTPServer  # noqa: E402

httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
conn = HTTPConnection('127.0.0.1', port, timeout=60)


def get(path):
    conn.request('GET', path)
    r = conn.getresponse()
    return r.status, r.read().decode('utf-8', errors='replace')


def post(path):
    conn.request('POST', path)
    r = conn.getresponse()
    return r.status, r.read().decode('utf-8', errors='replace')


# 1) 直链提取
st, body = get('/api/extract?url=' + __import__('urllib.parse', fromlist=['quote']).quote(
    'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'))
print('直链提取:', st, body[:200])

# 2) 播客 RSS 提取
st, body = get('/api/extract?url=' + __import__('urllib.parse', fromlist=['quote']).quote(
    'https://www.npr.org/rss/podcast.php?id=510289'))
d = json.loads(body)
print('RSS 提取:', st, '标题:', d.get('title'), '候选数:', len(d.get('audios', [])))
if d.get('audios'):
    a = d['audios'][0]
    print('第一个候选:', a['name'], '| size:', a['size'], '| type:', a['type'])

# 3) 坏链接
st, body = get('/api/extract?url=' + __import__('urllib.parse', fromlist=['quote']).quote('https://example.com/'))
print('普通页面:', st, body[:120])

# 4) 下载到本地（直链小文件）
import tempfile, os
p = os.path.join(tempfile.gettempdir(), 'ff_test_dl.mp3')
st, body = post('/api/download?url=' + __import__('urllib.parse', fromlist=['quote']).quote(
    'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3') + '&path=' + __import__('urllib.parse', fromlist=['quote']).quote(p))
print('下载:', st, body, '| 文件大小:', os.path.getsize(p) if os.path.exists(p) else '无')
if os.path.exists(p):
    with open(p, 'rb') as f:
        print('文件头:', f.read(4))
    os.remove(p)

httpd.shutdown()
print('=== 端到端验证完成 ===')
