"""Tkinter GUI for Ghost Font decoder."""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from pathlib import Path
import cv2
from PIL import Image, ImageTk

from decoder import decode, try_ocr


class GhostDecoderGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ghost Font Decoder")
        self.window.geometry("800x600")
        self.window.minsize(600, 400)

        self.video_path = None
        self.result_image = None
        self.tk_image = None

        self._build_ui()

    def _build_ui(self):
        # Top control bar
        controls = ttk.Frame(self.window, padding=10)
        controls.pack(fill=tk.X)

        ttk.Button(controls, text="Open Video", command=self._open_video).pack(side=tk.LEFT, padx=2)

        ttk.Label(controls, text="Threshold:").pack(side=tk.LEFT, padx=(10, 2))
        self.threshold_var = tk.IntVar(value=5)
        ttk.Spinbox(controls, from_=1, to=50, textvariable=self.threshold_var, width=5).pack(side=tk.LEFT, padx=2)

        ttk.Label(controls, text="Blur:").pack(side=tk.LEFT, padx=(10, 2))
        self.blur_var = tk.IntVar(value=1)
        ttk.Spinbox(controls, from_=0, to=15, textvariable=self.blur_var, width=5).pack(side=tk.LEFT, padx=2)

        ttk.Label(controls, text="Method:").pack(side=tk.LEFT, padx=(10, 2))
        self.method_var = tk.StringVar(value="raw")
        ttk.Combobox(controls, textvariable=self.method_var, values=["raw", "binary"], width=6, state="readonly").pack(side=tk.LEFT, padx=2)

        ttk.Button(controls, text="Decode", command=self._start_decode).pack(side=tk.LEFT, padx=10)
        ttk.Button(controls, text="Save Result", command=self._save_result).pack(side=tk.LEFT, padx=2)

        # Status bar
        self.status_var = tk.StringVar(value="Open a Ghost Font video to begin.")
        status_bar = ttk.Label(self.window, textvariable=self.status_var, relief=tk.SUNKEN, padding=(5, 2))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Progress bar
        self.progress = ttk.Progressbar(self.window, mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=10, pady=(0, 5))

        # Image display
        self.canvas = tk.Canvas(self.window, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # OCR result label
        self.ocr_var = tk.StringVar(value="")
        ocr_label = ttk.Label(self.window, textvariable=self.ocr_var, font=("Consolas", 11))
        ocr_label.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Keyboard shortcuts
        self.window.bind("<Control-o>", lambda e: self._open_video())
        self.window.bind("<Control-s>", lambda e: self._save_result())
        self.window.bind("<Return>", lambda e: self._start_decode())

    def _open_video(self):
        path = filedialog.askopenfilename(
            title="Select Ghost Font Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All files", "*.*")],
        )
        if path:
            self.video_path = path
            self.status_var.set(f"Loaded: {Path(path).name}")

    def _start_decode(self):
        if not self.video_path:
            messagebox.showwarning("No Video", "Open a Ghost Font video first.")
            return

        self.progress.start()
        self.status_var.set("Decoding...")
        self.ocr_var.set("")
        threading.Thread(target=self._decode, daemon=True).start()

    def _decode(self):
        try:
            result = decode(
                self.video_path,
                threshold=self.threshold_var.get(),
                blur=self.blur_var.get(),
                method=self.method_var.get(),
            )
            self.result_image = result

            # Convert OpenCV to PIL to Tkinter for display
            rgb = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            pil_img = Image.fromarray(rgb)
            self._show_image(pil_img)

            # Run OCR
            text = try_ocr(result)
            self.window.after(0, lambda: self.ocr_var.set(f"OCR: {text}"))

            self.window.after(0, lambda: self.status_var.set(
                f"Done — {result.shape[1]}x{result.shape[0]} | "
                f"{'Motion detected' if result.sum() > 0 else 'Nothing found — try lowering threshold'}"
            ))
        except Exception as e:
            self.window.after(0, lambda: self.status_var.set(f"Error: {e}"))
        finally:
            self.window.after(0, self.progress.stop)

    def _show_image(self, pil_img):
        max_w = self.canvas.winfo_width() or 760
        max_h = self.canvas.winfo_height() or 500
        pil_img.thumbnail((max_w, max_h), Image.LANCZOS)

        self.tk_image = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(
            self.canvas.winfo_width() // 2 or max_w // 2,
            self.canvas.winfo_height() // 2 or max_h // 2,
            image=self.tk_image,
        )

    def _save_result(self):
        if self.result_image is None:
            messagebox.showwarning("No Result", "Decode a video first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("All files", "*.*")],
        )
        if path:
            import decoder
            decoder.save_result(self.result_image, path)
            self.status_var.set(f"Saved to {Path(path).name}")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    GhostDecoderGUI().run()
