# -*- coding: utf-8 -*-
import io
p = r'D:\桌面\asd2\format-forge\version-info.txt'
v = io.open(p, encoding='utf-8').read()
for old, new in [
    ("'FileDescription', '格式工坊 全格式转换中心（离线版）'", "'FileDescription', '格式转换器 全格式转换中心（离线版）'"),
    ("'OriginalFilename', '格式工坊.exe'", "'OriginalFilename', '格式转换器.exe'"),
    ("'ProductName', '格式工坊 FormatForge'", "'ProductName', '格式转换器 FormatConverter'"),
]:
    n = v.count(old)
    assert n == 1, 'miss: %r (count=%d)' % (old, n)
    v = v.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(v)
print('version-info.txt ok')
