<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenCV-4.5+-purple?logo=opencv" alt="OpenCV"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT"/>
  <img src="https://img.shields.io/github/stars/roohan-514/ghost-decoder?style=social" alt="Stars"/>
</p>

<p align="center">
  <h1 align="center">👻 Ghost Font Decoder</h1>
  <p align="center"><em>Reveal hidden messages from anti-AI motion fonts — the tool that reads what AI can't.</em></p>
</p>

---

**Ghost Font** ([mixfont.com/ghost-font](https://mixfont.com/ghost-font)) is a new typeface designed to be **unreadable by AI**. It hides text as moving dots — invisible in any single frame, invisible to OCR, invisible to multimodal models like GPT-5 and Claude 4.

**This decoder** tracks those dots across all frames, rebuilds the motion trails, and reveals the hidden message. It even attempted OCR to read the result automatically.

<p align="center">
  <b>Human-readable → ✅</b><br/>
  <b>AI-readable → only with this tool</b>
</p>

---

## ✨ Features

| | |
|---|---|
| 🎥 **Drop any Ghost Font video** | MP4, AVI, MOV, MKV |
| 🔍 **3 detection methods** | Transition-tracking, dark-count, frame-diff |
| 🤖 **Auto OCR** | EasyOCR reads the decoded image (best-effort) |
| 📄 **Export** | PDF (image + text), TXT, PNG |
| 🎛️ **Tunable** | Sensitivity (percentile), dilation, method |
| 🎨 **Dark UI** | Modern Tkinter GUI with drag-drop |

## 🚀 Quick Start

```bash
git clone https://github.com/roohan-514/ghost-decoder.git
cd ghost-decoder
pip install opencv-python numpy easyocr fpdf2 pillow
python main.py
```

## 🖥️ CLI

```bash
python cli.py video.mp4 -o result.png
python cli.py video.mp4 --pdf result.pdf
python cli.py video.mp4 -m transition -t 99 -b 8
```

## 🧠 How It Works

```
Video frames  →  detect dark moving dots  →  count transitions per pixel
  →  keep top 1% most-active pixels  →  dilate into letter shapes  →  OCR
```

1. **Dot detection** — finds dark moving pixels (value < 50) in each frame
2. **Transition counting** — tracks light→dark transitions per pixel; moving dots cause frequent transitions while static decoys don't
3. **Percentile filtering** — keeps only the most-active pixels where letter paths are traced
4. **Dilation** — connects nearby dots into readable strokes
5. **OCR (optional)** — EasyOCR attempts to read the final image

## ⚠️ Why This Matters

Ghost Font is part of a growing trend: **anti-AI content** designed to be readable only by humans. As AI gets better at OCR, vision, and understanding images, projects like Ghost Font fight back — and tools like this decoder exist at the boundary.

This is a cat-and-mouse game:
- AI generates undreadable fonts → humans build decoders
- AI improves → new anti-AI techniques emerge

We're building the tools that keep **human communication human**.

## 📸 Try It Yourself

1. Go to [mixfont.com/ghost-font](https://www.mixfont.com/ghost-font)
2. Type a secret message
3. Download the video
4. Drop it into the decoder

## 🤝 Contributing

PRs welcome! Ideas:
- Better OCR preprocessing for ghost dots
- Video-native model integration
- A web version (WASM + OpenCV.js)
- Support for other anti-AI fonts

## 📜 License

MIT

---

<p align="center">
  <b>If AI won't read it — we will.</b><br/>
  <a href="https://github.com/roohan-514/ghost-decoder">Star on GitHub</a> ·
  <a href="https://mixfont.com/ghost-font">Try Ghost Font</a>
</p>
