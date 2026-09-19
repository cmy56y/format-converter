# -*- coding: utf-8 -*-
import io

p = r'D:\桌面\asd2\format-forge\main.py'
s = io.open(p, encoding='utf-8').read()

anchor = '                "dd: document.querySelectorAll(\'.dd\').length,"\n'
new_line = '                "ddEmpty: [...document.querySelectorAll(\'.dd-label\')].filter(e => !e.textContent.trim()).length,"\n'

n = s.count(anchor)
assert n == 1, 'anchor count = %d' % n
assert 'ddEmpty' not in s, 'already patched'
io.open(p, 'w', encoding='utf-8').write(s.replace(anchor, anchor + new_line))
print('replaced ok')
