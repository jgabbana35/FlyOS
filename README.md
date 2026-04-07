# 🚀 Fly OS v5.0 — Triple Hybrid AI Assistant

> **The most capable desktop AI assistant. Powered by Gemini, OpenRouter, and Base44.**

![FlyOS Dark Theme](https://img.shields.io/badge/Theme-Dark%20Premium-6C63FF?style=flat-square)
![Version](https://img.shields.io/badge/Version-5.0-00D4FF?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square)

---

## ✨ Features

### 🧠 Triple Hybrid Engine
- **Engine 1 — Gemini 2.5 Flash** (primary): Multimodal, streaming, image gen, web search
- **Engine 2 — OpenRouter Qwen3** (fallback): Text, analysis, coding
- **Engine 3 — Base44 Agent** (fallback): Final safety net
- Auto-failover between engines with live status badge

### 📎 Multimodal Inputs
- **Images**: JPG, PNG, GIF, WebP — inline preview + full viewer
- **Documents**: PDF, DOCX, XLSX, PPTX, TXT, MD, CSV, JSON, and 30+ code formats
- **Videos**: MP4, MOV, AVI — frame extraction and analysis
- **Audio**: MP3, WAV, M4A — Gemini native audio support
- **URLs**: Paste any link — FlyOS fetches and reads the webpage automatically

### 📤 Export Everything
| Format | Description |
|--------|-------------|
| DOCX   | Styled Word document with FlyOS branding |
| PDF    | Formatted PDF with code blocks |
| PPTX   | Full PowerPoint presentation from any response |
| XLSX   | Excel workbook from tabular data |

### 🎨 Image Generation
- Gemini Imagen 3 — just click **🎨 Image** or say "generate an image of..."
- Inline preview in chat, click to expand

### ⚡ Response Modes
| Mode     | Use Case |
|----------|----------|
| Fast     | Quick answers, low latency |
| Balanced | Default — best quality/speed ratio |
| Research | Deep, comprehensive, 8K tokens |
| Creative | High temperature for creative writing |

### 💬 Chat Features
- Unlimited-height message bubbles (no truncation ever)
- **"Fly is thinking..."** animated indicator while processing
- **Send → Stop** button — cancel mid-generation
- One-click **Copy** on every AI response
- Persistent chat history with search
- Session management — load, delete, search past conversations
- Markdown rendering in responses (headers, bold, code)

### 🔧 Developer Tools
- **Web Search** toggle (Gemini native Google Search grounding)
- **Code Execution** toggle (Gemini code interpreter)
- 6 modes: Chat, Code, Research, Writing, Vision, Data
- Background Python execution with output capture

### 🔄 Auto-Update
- Checks GitHub on startup for new versions
- Update banner with one-click download

---

## 🚀 Getting Started

### Option 1 — Run from source
```bash
git clone https://github.com/jgabbana35/FlyOS.git
cd FlyOS
pip install -r requirements.txt
python main.py
```

### Option 2 — Build your own EXE
```bash
# On Windows:
BUILD.bat
# EXE will be at dist/FlyOS.exe
```

---

## 📁 Project Structure
```
FlyOS_v5/
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── version.json         # Auto-update manifest
├── BUILD.bat            # PyInstaller build script
├── app/
│   ├── __init__.py
│   ├── config.py        # API keys, colors, settings
│   ├── client.py        # AI engines + file handling
│   └── gui.py           # CustomTkinter UI
└── workspace/           # Generated files saved here
```

---

## ⚙️ Configuration

Edit `app/config.py` to update API keys or model settings:

```python
GEMINI_API_KEY     = "your-key-here"
OPENROUTER_API_KEY = "your-key-here"
BASE44_API_KEY     = "your-key-here"

# Auto-update points to your repo
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/jgabbana35/FlyOS/main/version.json"
```

---

## 🔄 Publishing Updates

1. Make your changes, bump `APP_VERSION` in `config.py`
2. Update `version.json` with new version + download URL
3. Run `BUILD.bat` → upload `dist/FlyOS.exe` to a GitHub Release
4. Commit and push `version.json` — users will see the update banner

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `google-genai` | Gemini API |
| `customtkinter` | Modern Tkinter UI |
| `pillow` | Image handling |
| `requests` + `beautifulsoup4` | URL/web fetching |
| `python-docx` | DOCX generation |
| `reportlab` | PDF generation |
| `python-pptx` | PPTX generation |
| `openpyxl` | XLSX generation |
| `pyperclip` | Clipboard copy |
| `pandas` | Spreadsheet reading |
| `opencv-python` *(optional)* | Video frame extraction |

---

## 📝 License

MIT — free to use, modify, and distribute.

---

*Built with ❤️ — FlyOS v5.0*
