"""Core engine: frame-difference accumulation to reveal Ghost Font messages."""

import cv2
import numpy as np


def decode(video_path: str, threshold: int = 5, blur: int = 1, method: str = "raw") -> np.ndarray:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    ret, prev = cap.read()
    if not ret:
        raise ValueError("Empty video file")

    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    acc = np.zeros_like(prev_gray, dtype=np.float32)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if blur > 1:
            gp = cv2.GaussianBlur(prev_gray, (blur, blur), 0)
            gg = cv2.GaussianBlur(gray, (blur, blur), 0)
            diff = cv2.absdiff(gp, gg)
        else:
            diff = cv2.absdiff(prev_gray, gray)

        if method == "binary":
            _, mask = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
            acc += mask.astype(np.float32) / 255.0
        else:
            acc += diff.astype(np.float32)

        prev_gray = gray
        frame_count += 1

    cap.release()

    if frame_count == 0:
        raise ValueError("Video has only one frame.")

    # Normalize to 0-255
    mx = acc.max()
    if mx == 0:
        return acc.astype(np.uint8)
    acc = (acc / mx * 255).astype(np.uint8)

    # Denoise with median filter
    acc = cv2.medianBlur(acc, 3)

    # Adaptive threshold to isolate moving dots from background noise
    acc = cv2.adaptiveThreshold(acc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 31, 2)

    # Morphological cleanup
    kernel = np.ones((2, 2), np.uint8)
    acc = cv2.morphologyEx(acc, cv2.MORPH_OPEN, kernel)
    acc = cv2.morphologyEx(acc, cv2.MORPH_CLOSE, kernel)

    return acc


def try_ocr(image: np.ndarray) -> str:
    try:
        import pytesseract
        inv = cv2.bitwise_not(image)
        data = pytesseract.image_to_string(inv, config="--psm 6 --oem 3").strip()
        return data if data else "(no text detected)"
    except ImportError:
        return "(install pytesseract + tesseract-ocr for OCR)"
    except Exception as e:
        return f"(OCR error: {e})"


def save_result(image: np.ndarray, output_path: str):
    cv2.imwrite(output_path, image)


def open_result(image: np.ndarray):
    cv2.imshow("Ghost Decoder — Result", image)
    print("Press any key in the image window to close.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
