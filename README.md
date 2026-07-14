<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/OpenCV-4.5+-5C3EE8?style=for-the-badge&logo=opencv" alt="OpenCV"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT"/>
  <img src="https://img.shields.io/github/stars/roohan-514/ghost-decoder?style=for-the-badge" alt="Stars"/>
</p>

<h1 align="center">Ghost Font Decoder</h1>

<p align="center">
  <em>Decode Ghost Font videos — reveal messages hidden in anti-AI motion-based fonts.</em><br/>
  Uses frame-difference accumulation to extract text from moving dots.
</p>

---

## How It Works

Ghost Font hides text using moving dots that blend with the background. A single screenshot shows nothing — but the **motion trail** reveals the message to the human eye.

This tool applies the same technique programmatically:

1. Reads each frame of the video
2. Computes pixel differences between consecutive frames
3. Accumulates all motion over time — the static decoy disappears, the moving dots solidify
4. Applies adaptive thresholding and cleanup to reveal the message

---

## Quick Start

```bash
# Install dependencies
pip install opencv-python numpy

# Decode a Ghost Font video
python cli.py path/to/ghost-font-video.mp4 --output result.png

# Show the result window
python cli.py path/to/video.mp4
```

### GUI Mode

```bash
python main.py --gui
# or just
python main.py
```

---

## Command Line

```bash
python cli.py <video> [options]

Options:
  -o, --output FILE    Save decoded image
  -t, --threshold N    Motion sensitivity (default: 5, lower = more sensitive)
  -b, --blur N         Gaussian blur kernel (default: 1, 0 to skip)
  -m, --method METHOD  'raw' or 'binary' (default: raw)
  --ocr                Attempt OCR (requires pytesseract)
  --no-show            Don't display result window
```

### Examples

```bash
# Basic decode
python cli.py secret-message.mp4

# Save with high sensitivity
python cli.py secret-message.mp4 -t 3 --output result.png

# Use binary frame thresholding
python cli.py secret-message.mp4 -m binary -t 15
```

---

## How to Get a Ghost Font Video

1. Go to https://www.mixfont.com/ghost-font
2. Type your message in the playground
3. Click **Download message**
4. Run this decoder on the downloaded video

---

## Why This Works

Current multimodal AI models process video as individual static frames. Ghost Font exploits this by making each frame look like noise. But the motion between frames contains the real message — and that's exactly what frame differencing detects.

This tool demonstrates that Ghost Font is **not** truly AI-proof — it only defeats models that don't use temporal analysis. Once video-native models or frame-differencing tools are used, the hidden message is revealed.

---

## Requirements

- Python 3.8+
- OpenCV (`pip install opencv-python numpy`)
- Tesseract (optional, for OCR: install from https://github.com/tesseract-ocr/tesseract)

---

## License

MIT
