# -*- coding: utf-8 -*-
"""网页音频提取 - 可行性测试脚本"""
import re
import urllib.request
from urllib.parse import urljoin

AUDIO_EXT = ('.mp3', '.m4a', '.ogg', '.oga', '.flac', '.wav', '.opus', '.aac', '.wma', '.m4b', '.amr')
AUDIO_RE = re.compile(r'(https?://[^\s"\'<>()]+?\.(?:' + '|'.join(e[1:] for e in AUDIO_EXT) + r')(?:\?[^\s"\'<>()]*)?)', re.I)


def find_audio_urls(html, base_url):
    found = []
    for m in AUDIO_RE.finditer(html):
        found.append(m.group(1))
    for tag in ('audio', 'source', 'video', 'embed'):
        for m in re.finditer(r'<%s[^>]*?\bsrc\s*=\s*["\']?([^"\'>\s]+)' % tag, html, re.I):
            found.append(m.group(1))
        for m in re.finditer(r'<%s[^>]*?\bdata-src\s*=\s*["\']?([^"\'>\s]+)' % tag, html, re.I):
            found.append(m.group(1))
    for m in re.finditer(r'<meta[^>]+(?:property|name)=["\'](?:og:audio|twitter:audio)[^>]+content=["\']([^"\']+)', html, re.I):
        found.append(m.group(1))
    for m in re.finditer(r'"(?:audio|audioUrl|audio_url|mp3|file|src|url)"\s*:\s*"(https?://[^"]+?\.(?:mp3|m4a|ogg|flac|wav|opus|aac)(?:\?[^"]*)?)"', html, re.I):
        found.append(m.group(1))
    out, seen = [], set()
    for u in found:
        u = u.strip().strip('"\'')
        if u.startswith('//'):
            u = 'https:' + u
        elif not u.lower().startswith('http'):
            u = urljoin(base_url, u)
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out


def fetch(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return urllib.request.urlopen(req, timeout=timeout)


if __name__ == '__main__':
    # 测试1：抓取含音频的公开页面并解析
    try:
        resp = fetch('https://www.soundhelix.com/')
        html = resp.read().decode('utf-8', errors='replace')
        print('页面抓取 OK, 长度:', len(html))
        urls = find_audio_urls(html, 'https://www.soundhelix.com/')
        print('解析到音频候选:', urls[:6])
    except Exception as e:
        print('页面抓取失败:', e)

    # 测试2：音频直链可下载
    try:
        resp = fetch('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
                     headers={'User-Agent': 'Mozilla/5.0', 'Range': 'bytes=0-1023'})
        data = resp.read(1024)
        print('直链下载 OK, 状态:', resp.status, '头字节:', list(data[:4]), 'Content-Type:', resp.headers.get('Content-Type'))
    except Exception as e:
        print('直链下载失败:', e)

    # 测试3：任意页面抓取（观察限制）
    try:
        resp = fetch('https://example.com/')
        html = resp.read().decode('utf-8', errors='replace')
        urls = find_audio_urls(html, 'https://example.com/')
        print('example.com 抓取 OK，解析到:', urls[:3] or '无音频')
    except Exception as e:
        print('example.com 抓取失败:', e)
