# -*- coding: utf-8 -*-
import io

# 1) index.html
p1 = r'D:\桌面\asd2\format-forge\index.html'
s = io.open(p1, encoding='utf-8').read()
reps = [
    ('<title>格式工坊 FormatForge · 全格式转换中心</title>',
     '<title>格式转换器 · 全格式转换中心</title>'),
    ('<h1>格式工坊</h1>', '<h1>格式转换器</h1>'),
    ('<div class="sub">FORMAT FORGE</div>', '<div class="sub">FORMAT CONVERTER</div>'),
    # 白色 logo 图标：橙色渐变方块 -> 白色；装饰线在白块上用深色
    ('<rect x="3" y="3" width="42" height="42" rx="11" fill="url(#lg1)"/>',
     '<rect x="3" y="3" width="42" height="42" rx="11" fill="#ffffff"/>'),
    ('<path d="M34.5 22.5a3 3 0 100-6 3 3 0 000 6zM32 34h8" stroke="#F5BC5E" stroke-width="2.4" stroke-linecap="round"/>',
     '<path d="M34.5 22.5a3 3 0 100-6 3 3 0 000 6zM32 34h8" stroke="#14100a" stroke-width="2.4" stroke-linecap="round"/>'),
    ('<defs><linearGradient id="lg1" x1="0" y1="0" x2="48" y2="48"><stop stop-color="#E8A33D"/><stop offset="1" stop-color="#B97B1F"/></linearGradient></defs>',
     ''),
    ('格式工坊无法也不支持解密此类文件', '格式转换器无法也不支持解密此类文件'),
]
for old, new in reps:
    assert s.count(old) == 1, 'index.html miss: %r (count=%d)' % (old[:40], s.count(old))
    s = s.replace(old, new)
io.open(p1, 'w', encoding='utf-8').write(s)
print('index.html ok')

# 2) main.py
p2 = r'D:\桌面\asd2\format-forge\main.py'
m = io.open(p2, encoding='utf-8').read()
for old, new in [
    ("'格式工坊 FormatForge · 全格式转换中心'", "'格式转换器 · 全格式转换中心'"),
    ("'格式工坊 GUI 自检'", "'格式转换器 GUI 自检'"),
    ("'格式工坊', 0x10", "'格式转换器', 0x10"),
]:
    assert m.count(old) == 1, 'main.py miss: %r (count=%d)' % (old, m.count(old))
    m = m.replace(old, new)
io.open(p2, 'w', encoding='utf-8').write(m)
print('main.py ok')

# 3) version-info.txt
p3 = r'D:\桌面\asd2\format-forge\version-info.txt'
v = io.open(p3, encoding='utf-8').read()
for old, new in [
    ("'FileDescription', '格式工坊 全格式转换中心（离线版）'", "'FileDescription', '格式转换器 全格式转换中心（离线版）'"),
    ("'OriginalFilename', '格式工坊.exe'", "'OriginalFilename', '格式转换器.exe'"),
    ("'ProductName', '格式工坊 FormatForge'", "'ProductName', '格式转换器 FormatConverter'"),
]:
    assert v.count(old) == 1, 'version miss: %r (count=%d)' % (old, v.count(old))
    v = v.replace(old, new)
io.open(p3, 'w', encoding='utf-8').write(v)
print('version-info.txt ok')
