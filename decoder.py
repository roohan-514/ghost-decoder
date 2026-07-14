"""Ghost Font Decoder — reveals hidden text from anti-AI motion videos.

The Ghost Font (mixfont.com/ghost-font) hides text as moving dots that are
invisible in any single frame.  By tracking dot motion across all frames we
reveal the letter paths.  OCR is best-effort (ghost font is designed to
defeat AI vision); the decoded image is meant for human reading.
"""

import cv2
import numpy as np
from pathlib import Path

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["en"], gpu=False, verbose=False)
    return _reader


def decode(video_path: str, threshold: int = 99, blur: int = 5,
           method: str = "transition", progress_callback=None) -> tuple:
    """Decode a Ghost Font video.

    Args:
        video_path: Path to the video file.
        threshold: Percentile 0-100 (default 99).  Higher = fewer pixels.
        blur: Dilation iterations for connecting dots (default 5).
        method: 'transition' (recommended), 'dark', or 'raw'.
        progress_callback: Optional fn(percent, status_string).

    Returns:
        (decoded ndarray image, str extracted text)
    """
    if method == "raw":
        return _decode_raw(video_path, threshold, blur, progress_callback)
    return _decode_dots(video_path, threshold, blur, method, progress_callback)


def _decode_dots(video_path: str, threshold: int, dilate_iters: int,
                 method: str, progress_callback) -> tuple:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    ret, first = cap.read()
    if not ret:
        raise ValueError("Empty video file")
    h, w = first.shape[:2]
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    prev_dark = np.zeros((h, w), dtype=bool)
    transitions = np.zeros((h, w), dtype=np.int32)
    dark_total = np.zeros((h, w), dtype=np.int32)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dark_now = gray < 50

        transitions += (prev_dark == 0) & dark_now
        dark_total += dark_now.astype(np.int32)
        prev_dark = dark_now
        frame_count += 1

        if progress_callback and frame_count % 10 == 0:
            pct = min(int(frame_count / total_frames * 100), 99)
            progress_callback(pct, f"Frame {frame_count}/{total_frames}")

    cap.release()

    if progress_callback:
        progress_callback(95, "Building image...")

    src = dark_total if method == "dark" else transitions
    mx = src.max()
    if mx == 0:
        return np.zeros((h, w), dtype=np.uint8), ""

    # Keep the top percentile of most-active pixels
    norm = (src.astype(np.float32) / mx * 255).astype(np.uint8)
    p = max(0.1, min(99.9, float(threshold)))
    cutoff = np.percentile(norm, p)
    _, img = cv2.threshold(norm, cutoff, 255, cv2.THRESH_BINARY)

    dilate_iters = max(1, dilate_iters)
    img = cv2.dilate(img, np.ones((3, 3), np.uint8), iterations=dilate_iters)

    if progress_callback:
        progress_callback(97, "Running OCR...")

    text = _ocr_image(img)

    if progress_callback:
        progress_callback(100, "Done")

    return img, text


def _decode_raw(video_path: str, threshold: int, dilate_iters: int,
                progress_callback) -> tuple:
    """Frame-difference accumulation (original method)."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")
    ret, prev = cap.read()
    if not ret:
        raise ValueError("Empty video file")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    acc = np.zeros_like(prev_gray, dtype=np.float32)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        acc += cv2.absdiff(prev_gray, gray).astype(np.float32)
        prev_gray = gray
        frame_count += 1
        if progress_callback and frame_count % 10 == 0:
            pct = min(int(frame_count / total_frames * 100), 99)
            progress_callback(pct, f"Frame {frame_count}/{total_frames}")

    cap.release()
    if progress_callback:
        progress_callback(95, "Building image...")

    mx = acc.max()
    if mx == 0:
        return np.zeros_like(prev_gray, dtype=np.uint8), ""

    norm = (acc / mx * 255).astype(np.uint8)
    p = max(0.1, min(99.9, float(threshold)))
    cutoff = np.percentile(norm, p)
    _, img = cv2.threshold(norm, cutoff, 255, cv2.THRESH_BINARY)
    dilate_iters = max(1, dilate_iters)
    img = cv2.dilate(img, np.ones((3, 3), np.uint8), iterations=dilate_iters)

    if progress_callback:
        progress_callback(97, "Running OCR...")

    text = _ocr_image(img)

    if progress_callback:
        progress_callback(100, "Done")

    return img, text


def _ocr_image(img: np.ndarray) -> str:
    """Best-effort OCR.  Ghost Font is designed to defeat AI vision."""
    try:
        reader = _get_reader()
        results = reader.readtext(img, paragraph=True)
        lines = [r[1] for r in results if r[2] > 0.1]
        return "\n".join(lines) if lines else ""
    except Exception:
        return ""


def save_result(image: np.ndarray, output_path: str):
    cv2.imwrite(output_path, image)


def export_pdf(text: str, image: np.ndarray, output_path: str):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", size=14)
    pdf.cell(0, 10, "Ghost Font Decoder — Result", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    temp_img = Path(output_path).with_suffix(".tmp.png")
    cv2.imwrite(str(temp_img), image)
    from PIL import Image as PILImage
    with PILImage.open(temp_img) as pil:
        w, h = pil.size
        max_w = 180
        if w > max_w:
            h = int(h * max_w / w)
            w = max_w
        pil.thumbnail((w, h))
        pil.save(str(temp_img))
    pdf.image(str(temp_img), x=pdf.w / 2 - w / 2, w=w)
    temp_img.unlink(missing_ok=True)
    pdf.ln(10)
    pdf.set_font("Courier", size=12)
    pdf.multi_cell(0, 8, text or "(no text detected)")
    pdf.output(output_path)


def export_text(text: str, output_path: str):
    Path(output_path).write_text(text or "(no text detected)", encoding="utf-8")


def open_result(image: np.ndarray):
    cv2.imshow("Ghost Decoder — Result", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
