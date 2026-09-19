# -*- coding: utf-8 -*-
import io
p = r'D:\桌面\asd2\format-forge\index.html'
s = io.open(p, encoding='utf-8').read()

old_root = """  --bg:#0E1218; --bg-deep:#0A0E13; --panel:#161C26; --panel-2:#1B2330; --panel-3:#212B3B;
  --line:#28324a; --line-2:#33405c;
  --txt:#E9EDF4; --txt-2:#9AA5B8; --txt-3:#66718A;
  --amber:#E8A33D; --amber-hi:#F5BC5E; --amber-dim:rgba(232,163,61,.14);
  --green:#3FBF8F; --red:#E06C5B; --cyan:#4FB8C9; --blue:#4A9BE8; --violet:#7C6FE8;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Consolas,"Courier New",monospace;
  --sans:"Segoe UI","PingFang SC","Microsoft YaHei","Noto Sans SC",-apple-system,sans-serif;
  --radius:12px; --radius-sm:8px;
  --shadow:0 10px 30px rgba(0,0,0,.35);"""
new_root = """  --bg:#F4F6F9; --bg-deep:#EAEFF5; --panel:#FFFFFF; --panel-2:#F2F5F9; --panel-3:#E7ECF2;
  --line:#E2E7EE; --line-2:#C7D0DC;
  --txt:#1E2632; --txt-2:#5B6678; --txt-3:#8B95A6;
  --amber:#E8A33D; --amber-hi:#D9912B; --amber-dim:rgba(232,163,61,.12);
  --green:#2E9E73; --red:#D05A48; --cyan:#3A9FB2; --blue:#3A86D6; --violet:#6A5BE0;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Consolas,"Courier New",monospace;
  --sans:"Segoe UI","PingFang SC","Microsoft YaHei","Noto Sans SC",-apple-system,sans-serif;
  --radius:12px; --radius-sm:8px;
  --shadow:0 10px 30px rgba(30,45,70,.08);"""
assert s.count(old_root) == 1, 'root miss'
s = s.replace(old_root, new_root)

# 浅色背景光斑（更淡）
old_bg = """  background-image:
    radial-gradient(1100px 500px at 85% -10%, rgba(232,163,61,.07), transparent 60%),
    radial-gradient(900px 420px at -10% 110%, rgba(79,184,201,.06), transparent 60%);"""
new_bg = """  background-image:
    radial-gradient(1100px 500px at 85% -10%, rgba(232,163,61,.10), transparent 60%),
    radial-gradient(900px 420px at -10% 110%, rgba(79,184,201,.08), transparent 60%);"""
assert s.count(old_bg) == 1, 'bg miss'
s = s.replace(old_bg, new_bg)

# 输入框深色底 -> 白色
old_url = ".web-url{\n  flex:1;min-width:280px;background:#0c1017;"
new_url = ".web-url{\n  flex:1;min-width:280px;background:#FFFFFF;"
assert s.count(old_url) == 1, 'url miss'
s = s.replace(old_url, new_url)

io.open(p, 'w', encoding='utf-8').write(s)
print('theme light ok')
