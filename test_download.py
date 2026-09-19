# -*- coding: utf-8 -*-
"""本地大文件确定性验证 /api/download 流式下载"""
import os
import sys
import tempfile
import threading
import urllib.parse
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

sys.path.insert(0, r'D:\桌面\asd2\format-forge')
from main import Handler  # noqa: E402

# 准备 3MB 本地测试文件
src = os.path.join(tempfile.gettempdir(), 'ff_big_test.bin')
with open(src, 'wb') as f:
    f.write(os.urandom(3 * 1024 * 1024))

# 起一个提供静态文件的源服务
src_httpd = ThreadingHTTPServer(('127.0.0.1', 0), SimpleHTTPRequestHandler)
src_port = src_httpd.server_address[1]
os.chdir(tempfile.gettempdir())
threading.Thread(target=src_httpd.serve_forever, daemon=True).start()

# 被测服务
httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
conn = HTTPConnection('127.0.0.1', port, timeout=120)

dst = os.path.join(tempfile.gettempdir(), 'ff_big_dst.bin')
url = 'http://127.0.0.1:%d/ff_big_test.bin' % src_port
q = urllib.parse.quote
conn.request('POST', '/api/download?url=%s&path=%s' % (q(url), q(dst)))
r = conn.getresponse()
body = r.read().decode()
print('下载响应:', r.status, body)

ok = os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(src)
print('字节数一致:', ok, '| 源:', os.path.getsize(src), '目标:', os.path.getsize(dst) if os.path.exists(dst) else 0)

os.remove(src)
if os.path.exists(dst):
    os.remove(dst)
httpd.shutdown()
src_httpd.shutdown()
print('=== 下载逻辑验证', 'PASS' if ok else 'FAIL', '===')
