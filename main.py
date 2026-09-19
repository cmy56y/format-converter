# -*- coding: utf-8 -*-
"""
格式工坊 FormatForge —— Windows 桌面版入口
以本地 HTTP 服务承载 index.html，用 pywebview(WebView2) 渲染，PyInstaller 打包为 exe。
"""
import html as html_lib
import json
import os
import re
import sys
import threading
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
AUDIO_EXT = ('.mp3', '.m4a', '.ogg', '.oga', '.flac', '.wav', '.opus', '.aac', '.wma', '.m4b', '.amr')
MEDIA_EXT = AUDIO_EXT + ('.mp4', '.webm', '.mov', '.m4v')
_AUDIO_RE = re.compile(
    r'(https?://[^\s"\'<>()]+?\.(?:' + '|'.join(e[1:] for e in AUDIO_EXT) + r')(?:\?[^\s"\'<>()]*)?)', re.I)
_MEDIA_JSON_RE = re.compile(
    r'"(?:audio|audioUrl|audio_url|mp3|file|src|url|mediaUrl|contentUrl)"\s*:\s*"(https?://[^"]+?\.(?:'
    + '|'.join(e[1:] for e in MEDIA_EXT) + r')(?:\?[^"]*)?)"', re.I)


def _http_open(url, method='GET', headers=None, timeout=15):
    req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})}, method=method)
    return urllib.request.urlopen(req, timeout=timeout)


def _safe_name(name):
    name = (name or '').strip().strip('"\'')
    return re.sub(r'[\\/:*?"<>|\r\n]+', '_', name)[:120]


def find_audio_urls(text, base_url):
    """从页面/JSON/RSS 文本中提取媒体直链，返回去重后的绝对 URL 列表。"""
    found = []
    for m in _AUDIO_RE.finditer(text):
        found.append(m.group(1))
    for m in _MEDIA_JSON_RE.finditer(text):
        found.append(m.group(1))
    for tag in ('audio', 'source', 'video', 'embed'):
        for m in re.finditer(r'<%s[^>]*?\bsrc\s*=\s*["\']?([^"\'>\s]+)' % tag, text, re.I):
            found.append(m.group(1))
        for m in re.finditer(r'<%s[^>]*?\bdata-src\s*=\s*["\']?([^"\'>\s]+)' % tag, text, re.I):
            found.append(m.group(1))
    for m in re.finditer(r'<meta[^>]+(?:property|name)=["\'](?:og:audio|twitter:audio)[^>]+content=["\']([^"\']+)',
                         text, re.I):
        found.append(m.group(1))
    for m in re.finditer(r'<enclosure[^>]*?url="([^"]+?\.(?:'
                         + '|'.join(e[1:] for e in AUDIO_EXT) + r')(?:[^"]*))"', text, re.I):
        found.append(m.group(1))
    out, seen = [], set()
    for u in found:
        u = html_lib.unescape(u.strip().strip('"\''))
        if u.startswith('//'):
            u = 'https:' + u
        elif not u.lower().startswith('http'):
            u = urllib.parse.urljoin(base_url, u)
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def _probe_size(url, timeout=5):
    """HEAD 探测候选文件大小，失败返回 None。"""
    try:
        r = _http_open(url, method='HEAD', timeout=timeout)
        cl = r.headers.get('Content-Length')
        return int(cl) if cl and cl.isdigit() else None
    except Exception:  # noqa: BLE001
        return None


def extract_audio_from_url(url):
    """核心：输入网址/直链，返回 {'title':…, 'audios':[{url,name,size,type}]} 或抛异常。"""
    if not (url.startswith('http://') or url.startswith('https://')):
        raise ValueError('仅支持 http/https 链接')
    # 1) 直链音频：HEAD 命中 audio/* 或扩展名即直接返回
    low = url.lower()
    try:
        r = _http_open(url, method='HEAD', timeout=10)
        ct = (r.headers.get('Content-Type') or '').lower()
    except Exception:  # noqa: BLE001
        ct = ''
    if ct.startswith('audio/') or any(low.rstrip('/').endswith(e) for e in AUDIO_EXT):
        cl = r.headers.get('Content-Length') if 'r' in dir() else None
        size = int(cl) if cl and cl.isdigit() else None
        name = _safe_name(urllib.parse.unquote(url.split('/')[-1].split('?')[0])) or 'audio'
        return {'title': name, 'audios': [{'url': url, 'name': name, 'size': size, 'type': 'audio'}]}
    # 2) 网页/RSS：抓取内容后解析
    resp = _http_open(url, timeout=20)
    raw = resp.read()
    base = resp.geturl() or url
    text = raw.decode('utf-8', errors='replace')
    # 标题
    mt = re.search(r'<title[^>]*>(.*?)</title>', text, re.I | re.S)
    title = _safe_name(mt.group(1).strip()) if mt else _safe_name(url)
    urls = find_audio_urls(text, base)
    if not urls:
        raise ValueError('页面中没有找到可下载的音频链接（可能是登录或动态加载页面）')
    audios, seen = [], set()
    for u in urls[:24]:
        key = u.split('?')[0]
        if key in seen:
            continue
        seen.add(key)
        kind = 'video' if any(key.lower().endswith(e) for e in ('.mp4', '.webm', '.mov', '.m4v')) else 'audio'
        fname = _safe_name(urllib.parse.unquote(key.split('/')[-1])) or 'media'
        audios.append({'url': u, 'name': fname, 'size': None, 'type': kind})
    # 3) 对前 6 个候选并发 HEAD 探测大小（短超时，失败不影响）
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=6) as pool:
        sizes = list(pool.map(_probe_size, [a['url'] for a in audios[:6]]))
    for a, s in zip(audios, sizes):
        a['size'] = s
    return {'title': title or '网页音频', 'audios': audios}


def resource_path(rel):
    """打包后资源位于 _MEIPASS（onefile 解压目录），源码运行时位于脚本目录。"""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=resource_path('.'), **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # 静默访问日志

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/extract':
            self._send_json(self._api_extract(parsed.query))
            return
        super().do_GET()

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        try:
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:  # noqa: BLE001
            pass

    def _api_extract(self, query):
        try:
            qs = urllib.parse.parse_qs(query)
            url = (qs.get('url') or [''])[0].strip()
            if not url:
                return {'error': '缺少 url 参数'}
            return extract_audio_from_url(url)
        except ValueError as e:
            return {'error': str(e)}
        except Exception as e:  # noqa: BLE001
            return {'error': '提取失败：%s' % e}

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/save':
            try:
                qs = urllib.parse.parse_qs(parsed.query)
                path = qs.get('path', [''])[0]
                if not path:
                    self.send_error(400, 'missing path')
                    return
                length = int(self.headers.get('Content-Length') or 0)
                with open(path, 'wb') as f:
                    remaining = length
                    while remaining > 0:
                        chunk = self.rfile.read(min(1 << 20, remaining))
                        if not chunk:
                            break
                        f.write(chunk)
                        remaining -= len(chunk)
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write('ok'.encode('utf-8'))
            except Exception as e:  # noqa: BLE001
                try:
                    self.send_error(500, str(e))
                except Exception:
                    pass
            return
        if parsed.path == '/api/download':
            self._api_download(parsed.query)
            return
        self.send_error(404)

    def _api_download(self, query):
        try:
            qs = urllib.parse.parse_qs(query)
            url = (qs.get('url') or [''])[0].strip()
            path = (qs.get('path') or [''])[0].strip()
            if not url or not path:
                self._send_json({'error': '缺少 url 或 path 参数'}, 400)
                return
            if not (url.startswith('http://') or url.startswith('https://')):
                self._send_json({'error': '仅支持 http/https 链接'}, 400)
                return
            resp = _http_open(url, timeout=120)
            total = 0
            with open(path, 'wb') as f:
                while True:
                    chunk = resp.read(1 << 16)
                    if not chunk:
                        break
                    f.write(chunk)
                    total += len(chunk)
            self._send_json({'ok': True, 'bytes': total})
        except Exception as e:  # noqa: BLE001
            self._send_json({'error': '下载失败：%s' % e}, 500)


class Api:
    """通过 window.pywebview.api 暴露给前端调用。"""

    def pick_save_path(self, filename):
        import webview
        try:
            w = webview.windows[0] if webview.windows else None
            if not w:
                return None
            safe = os.path.basename(str(filename) or 'output.bin')
            r = w.create_file_dialog(webview.SAVE_DIALOG, save_filename=safe)
            return r if isinstance(r, str) else None
        except Exception:  # noqa: BLE001
            return None

    def pick_folder(self):
        import webview
        try:
            w = webview.windows[0] if webview.windows else None
            if not w:
                return None
            r = w.create_file_dialog(webview.FOLDER_DIALOG)
            return r if isinstance(r, str) else None
        except Exception:  # noqa: BLE001
            return None


def selftest():
    """启动本地服务并验证资源完整，输出结果后退出（供打包后验证）。"""
    from http.client import HTTPConnection
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    results = []
    try:
        conn = HTTPConnection('127.0.0.1', port, timeout=10)
        for path in ('/index.html', '/vendor/ffmpeg.js', '/vendor/ffmpeg-core.wasm',
                     '/vendor/xlsx.full.min.js', '/vendor/pdf.min.js', '/vendor/pdf.worker.min.js',
                     '/vendor/pdf-lib.min.js', '/vendor/fflate.js', '/vendor/mammoth.browser.min.js'):
            conn.request('GET', path)
            resp = conn.getresponse()
            body = resp.read()
            results.append((path, resp.status, len(body)))
        conn.close()
    finally:
        httpd.shutdown()
    for path, status, size in results:
        print(f'{status} {size:>10} {path}')
    ok = all(s == 200 and z > 0 for _, s, z in results)
    print('SELFTEST', 'PASS' if ok else 'FAIL')
    return 0 if ok else 1


def guicheck():
    """启动窗口 → 页面加载后 evaluate_js 检查 DOM → 关闭，结果写入 guicheck.json（供打包后验证）。"""
    import json
    import webview
    result = {'ok': False, 'detail': ''}

    def on_loaded():
        try:
            w = webview.windows[0]
            r = w.evaluate_js(
                "JSON.stringify({"
                "title: document.title,"
                "nav: document.querySelectorAll('.nav-btn').length,"
                "drop: document.querySelectorAll('.dropzone').length,"
                "dd: document.querySelectorAll('.dd').length,"
                "ddEmpty: [...document.querySelectorAll('.dd-label')].filter(e => !e.textContent.trim()).length,"
                "selHidden: document.querySelectorAll('select[style*=\"display: none\"]').length,"
                "engine: (typeof FFmpegWASM !== 'undefined'),"
                "xlsx: (typeof XLSX !== 'undefined'),"
                "pdflib: (typeof PDFLib !== 'undefined'),"
                "pdfjs: (typeof pdfjsLib !== 'undefined'),"
                "fflate: (typeof fflate !== 'undefined'),"
                "mammoth: (typeof mammoth !== 'undefined'),"
                "pyapi: (!!(window.pywebview && window.pywebview.api)),"
                "htmlLen: document.body.innerHTML.length,"
                "filesDebug: (() => {"
                "  const f = document.querySelector('[data-files=image]');"
                "  const r = document.querySelector('[data-results=image]');"
                "  return {"
                "    filesChild: f ? f.children.length : -1,"
                "    filesH: f ? f.offsetHeight : -1,"
                "    filesDisp: f ? getComputedStyle(f).display : 'na',"
                "    filesHTML: f ? f.innerHTML.substring(0,100) : 'na',"
                "    resultsClass: r ? r.className : 'na',"
                "    resultsDisp: r ? getComputedStyle(r).display : 'na',"
                "    resultsChild: r ? r.children.length : -1"
                "  }"
                "})()"
                "})"
            )
            result['detail'] = str(r)
            result['ok'] = True
        except Exception as e:  # noqa: BLE001
            result['detail'] = 'ERR: %s' % e
        finally:
            try:
                w.destroy()
            except Exception:
                pass

    httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    webview.settings['ALLOW_DOWNLOADS'] = True
    w = webview.create_window(
        '格式转换器 GUI 自检',
        'http://127.0.0.1:%d/index.html' % port,
        js_api=Api(),
        width=1100,
        height=720,
    )
    w.events.loaded += on_loaded
    webview.start()
    httpd.shutdown()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guicheck.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print('GUICHECK', 'PASS' if result.get('ok') else 'FAIL', result.get('detail', ''))
    return 0 if result.get('ok') else 1


def screen_workarea():
    """获取屏幕工作区尺寸（不含任务栏），失败时回退默认值。"""
    try:
        import ctypes
        import ctypes.wintypes
        r = ctypes.wintypes.RECT()
        ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(r), 0)
        return max(r.right - r.left, 800), max(r.bottom - r.top, 600)
    except Exception:  # noqa: BLE001
        return 1920, 1080


def main():
    if '--selftest' in sys.argv:
        return selftest()
    if '--guicheck' in sys.argv:
        return guicheck()
    try:
        httpd = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    except OSError as e:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, '无法启动本地服务：%s' % e, '格式转换器', 0x10)
        return 1
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    import webview
    webview.settings['ALLOW_DOWNLOADS'] = True  # 兜底：浏览器式下载
    sw, sh = screen_workarea()
    win_w = min(1280, sw - 40)
    win_h = min(840, sh - 60)
    min_w = min(980, win_w)
    min_h = min(620, win_h)
    webview.create_window(
        '格式转换器 FormatConverter',
        'http://127.0.0.1:%d/index.html' % port,
        js_api=Api(),
        width=win_w,
        height=win_h,
        min_size=(min_w, min_h),
    )
    webview.start()
    return 0


if __name__ == '__main__':
    sys.exit(main())
