<div align="center">
  <h1>👻 Ghost Font Decoder</h1>
  <p><em>Decode anti-AI motion fonts — reveal messages hidden in video.</em></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python" alt="Python"/>
    <img src="https://img.shields.io/badge/OpenCV-4.5+-purple?logo=opencv" alt="OpenCV"/>
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT"/>
  </p>
</div>

---

## What It Does

Ghost Font hides text using **moving dots** that are invisible in any single frame. Only the human eye can see the motion trail — until now.

This tool tracks dark moving dots across all frames, accumulates their motion trails, and produces a decoded image showing the hidden message. An optional **EasyOCR** pass attempts automatic text extraction (Ghost Font is designed to defeat AI vision, so OCR may not always succeed — the decoded image is meant for human reading).

## Features

- 🎥 **Drop any Ghost Font video** — MP4, AVI, MOV, MKV
- 🔍 **Three detection methods** — transition-tracking (best), dark-count, frame-difference
- 🤖 **Auto OCR** — best-effort text reading via EasyOCR
- 📄 **Export as PDF** — image + extracted text in one file
- 📝 **Export as TXT** — just the decoded message
- 🖼️ **Export as PNG** — the raw decoded image
- 🎛️ **Adjustable settings** — sensitivity (percentile), dilation, method
- 📊 **Live progress bar** — see each frame being processed
- 🎨 **Dark modern UI** — built with Tkinter

## Quick Start

```bash
# Install
pip install opencv-python numpy easyocr fpdf2 pillow

# GUI mode
python main.py

# CLI mode
python cli.py video.mp4
```

## CLI Usage

```bash
python cli.py video.mp4                          # Decode and show result
python cli.py video.mp4 -o result.png             # Save decoded image
python cli.py video.mp4 --pdf result.pdf          # Export as PDF
python cli.py video.mp4 --txt message.txt         # Export as text

# Method options
python cli.py video.mp4 -m transition             # Transition-tracking (default, best)
python cli.py video.mp4 -m dark                   # Dark-pixel accumulation
python cli.py video.mp4 -m raw                    # Frame-difference accumulation

# Fine-tuning
python cli.py video.mp4 -t 99                     # Percentile (higher=fewer dots)
python cli.py video.mp4 -b 8                      # Dilation iterations (connect dots)
```

## Detection Methods

| Method | Description | Best For |
|--------|-------------|----------|
| `transition` | Counts light→dark transitions per pixel — isolates moving dots from static decoys | **Recommended** — best at separating text dots from noise |
| `dark` | Counts total dark frames per pixel — simpler accumulation | Videos with high dot-density |
| `raw` | Frame-difference accumulation — classic approach | Traditional motion analysis |

## How to Get a Ghost Font Video

1. Go to [mixfont.com/ghost-font](https://www.mixfont.com/ghost-font)
2. Type your message
3. Download the video
4. Run this decoder

## How It Works

1. **Dot detection** — finds dark moving pixels (value < 50) in each frame
2. **Transition counting** — tracks light→dark transitions per pixel (moving dots cause frequent transitions, while static pixels stay constant)
3. **Percentile filtering** — keeps the top percentile of most-active pixels where the letter paths are traced
4. **Dilation** — connects nearby dots into readable strokes
5. **OCR** — EasyOCR attempts to read the final image (best-effort)

## Limitations

Ghost Font is specifically designed to defeat AI vision. The OCR pass is **best-effort** and may not always return text. The decoded image should be readable by a human — if the OCR output is empty, try adjusting the sensitivity or dilation settings in the GUI, or read the text directly from the image preview.

## Requirements

- Python 3.8+
- opencv-python, numpy, easyocr, fpdf2, pillow

## License

MIT
