# 格式转换器 FormatConverter

一个 Windows 桌面端全格式文件转换器，基于 Python + PyWebView + WebView2，离线运行（网页音频提取功能除外）。

## 功能

- **音频转换**：MP3 / WAV / OGG / M4A / AAC / FLAC / Opus 互转（基于 ffmpeg.wasm）
- **视频转换**：MP4 / WebM / MOV / AVI / MKV 互转，可转 GIF
- **图片转换**：PNG / JPG / WebP / GIF / BMP / SVG / AVIF 互转与压缩
- **文档转换**：Word 提取文本、编码修复（GBK→UTF-8）、Markdown、纯文本转 PDF
- **表格转换**：Excel 与 CSV / JSON / HTML 互转
- **PDF 工具**：合并、拆页、转图片、图片合成 PDF、提取文字
- **压缩包工具**：解压 ZIP / TAR / GZ / TGZ，打包为 ZIP / GZ
- **格式侦探**：识别文件真实格式（防改名伪装）
- **网页音频**：从网页 URL 提取音频直链并下载

## 技术栈

- Python 3.14 + PyWebView (WebView2)
- 前端原生 HTML/CSS/JS
- ffmpeg.wasm / xlsx.js / pdf.js / pdf-lib / fflate / mammoth
- PyInstaller 打包为单文件 exe

## 打包

```powershell
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --windowed --onefile `
  --name "格式转换器" --icon format-forge.ico --version-file version-info.txt `
  --add-data "index.html;." --add-data "vendor;vendor" `
  --hidden-import webview.platforms.edgechromium --collect-all webview `
  --collect-all pythonnet --collect-all clr_loader main.py
```

## 许可

仅供学习交流使用。
