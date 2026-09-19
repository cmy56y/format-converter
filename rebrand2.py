# -*- coding: utf-8 -*-
import io

p2 = r'D:\桌面\asd2\format-forge\main.py'
m = io.open(p2, encoding='utf-8').read()
for old, new in [
    ("'格式工坊 FormatForge',", "'格式转换器 FormatConverter',"),
    ("'格式工坊 GUI 自检',", "'格式转换器 GUI 自检',"),
    ("'格式工坊', 0x10", "'格式转换器', 0x10"),
]:
    n = m.count(old)
    assert n == 1, 'main.py miss: %r (count=%d)' % (old, n)
    m = m.replace(old, new)
io.open(p2, 'w', encoding='utf-8').write(m)
print('main.py ok')
