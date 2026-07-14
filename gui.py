"""Modern interactive GUI for Ghost Font Decoder."""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
from pathlib import Path
import cv2
from PIL import Image, ImageTk

from decoder import decode, save_result, export_pdf, export_text


THEME_BG = "#1a1a2e"
THEME_SURFACE = "#16213e"
THEME_PRIMARY = "#0f3460"
THEME_ACCENT = "#e94560"
THEME_TEXT = "#eaeaea"
THEME_SECONDARY = "#a0a0b0"


class GhostDecoderGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ghost Font Decoder")
        self.window.geometry("1000x720")
        self.window.minsize(800, 600)
        self.window.configure(bg=THEME_BG)
        self.window.iconphoto(False, tk.PhotoImage(width=1, height=1))

        self.video_path = None
        self.result_image = None
        self.result_text = ""
        self.tk_preview = None
        self.tk_result = None

        self._build_ui()
        self._apply_theme()

    def _apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=THEME_BG)
        style.configure("TLabel", background=THEME_BG, foreground=THEME_TEXT, font=("Segoe UI", 10))
        style.configure("TButton", background=THEME_PRIMARY, foreground=THEME_TEXT,
                        font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TButton", background=[("active", THEME_ACCENT), ("disabled", "#333")])
        style.configure("Accent.TButton", background=THEME_ACCENT, foreground="white")
        style.map("Accent.TButton", background=[("active", "#ff6b81")])
        style.configure("TEntry", fieldbackground=THEME_SURFACE, foreground=THEME_TEXT)
        style.configure("TProgressbar", background=THEME_ACCENT, troughcolor=THEME_SURFACE)
        style.configure("TLabelFrame", background=THEME_BG, foreground=THEME_TEXT)
        style.configure("TLabelframe.Label", background=THEME_BG, foreground=THEME_TEXT)

    def _build_ui(self):
        # Top header
        header = tk.Frame(self.window, bg=THEME_SURFACE, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="👻  Ghost Font Decoder", bg=THEME_SURFACE,
                 fg=THEME_TEXT, font=("Segoe UI", 18, "bold")).pack(side=tk.LEFT, padx=20, pady=12)

        tk.Label(header, text="Reveal messages hidden in motion", bg=THEME_SURFACE,
                 fg=THEME_SECONDARY, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5, pady=15)

        # Main content area (two columns)
        main = tk.Frame(self.window, bg=THEME_BG)
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left column — controls + drop zone
        left = tk.Frame(main, bg=THEME_BG, width=380)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)

        # Drop zone
        self.drop_frame = tk.Frame(left, bg=THEME_SURFACE, height=140, highlightbackground=THEME_PRIMARY,
                                    highlightthickness=2, cursor="hand2")
        self.drop_frame.pack(fill=tk.X, pady=(0, 10))
        self.drop_frame.pack_propagate(False)

        self.drop_label = tk.Label(self.drop_frame,
                                    text="🎥  Drop video here\n\nor click to browse",
                                    bg=THEME_SURFACE, fg=THEME_SECONDARY,
                                    font=("Segoe UI", 12))
        self.drop_label.pack(expand=True, fill=tk.BOTH)
        self.drop_frame.bind("<Button-1>", lambda e: self._browse())
        self.drop_label.bind("<Button-1>", lambda e: self._browse())

        # Settings panel
        settings = tk.LabelFrame(left, text="⚙️  Settings", bg=THEME_BG, fg=THEME_TEXT,
                                  font=("Segoe UI", 10, "bold"), pad=10)
        settings.pack(fill=tk.X, pady=(0, 10))

        row = tk.Frame(settings, bg=THEME_BG)
        row.pack(fill=tk.X, pady=3)
        tk.Label(row, text="Method:", bg=THEME_BG, fg=THEME_TEXT, width=10, anchor="w").pack(side=tk.LEFT)
        self.method_var = tk.StringVar(value="transition")
        ttk.Combobox(row, textvariable=self.method_var, values=["transition", "dark", "raw"],
                     width=12, state="readonly").pack(side=tk.LEFT)
        tk.Label(row, text="transition=best", bg=THEME_BG, fg=THEME_SECONDARY,
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=5)

        row = tk.Frame(settings, bg=THEME_BG)
        row.pack(fill=tk.X, pady=3)
        tk.Label(row, text="Sensitivity:", bg=THEME_BG, fg=THEME_TEXT, width=10, anchor="w").pack(side=tk.LEFT)
        self.threshold_var = tk.IntVar(value=99)
        self.threshold_slider = ttk.Scale(row, from_=95, to=100, variable=self.threshold_var,
                                           orient=tk.HORIZONTAL, length=120)
        self.threshold_slider.pack(side=tk.LEFT, padx=5)
        self.threshold_label = tk.Label(row, textvariable=self.threshold_var, bg=THEME_BG,
                                         fg=THEME_ACCENT, width=3)
        self.threshold_label.pack(side=tk.LEFT)
        tk.Label(row, text="%", bg=THEME_BG, fg=THEME_SECONDARY).pack(side=tk.LEFT)
        tk.Label(row, text="(higher=fewer dots)", bg=THEME_BG, fg=THEME_SECONDARY,
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=5)

        row = tk.Frame(settings, bg=THEME_BG)
        row.pack(fill=tk.X, pady=3)
        tk.Label(row, text="Dilation:", bg=THEME_BG, fg=THEME_TEXT, width=10, anchor="w").pack(side=tk.LEFT)
        self.blur_var = tk.IntVar(value=5)
        ttk.Spinbox(row, from_=1, to=15, textvariable=self.blur_var, width=5).pack(side=tk.LEFT)
        tk.Label(row, text="(connect dots)", bg=THEME_BG, fg=THEME_SECONDARY,
                 font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=5)

        # Status + progress
        self.status_var = tk.StringVar(value="Drop or open a Ghost Font video to start")
        status_bar = tk.Label(left, textvariable=self.status_var, bg=THEME_SURFACE,
                               fg=THEME_SECONDARY, font=("Segoe UI", 9), anchor="w", padx=10, pady=6)
        status_bar.pack(fill=tk.X, pady=(0, 5))

        self.progress = ttk.Progressbar(left, mode="determinate", value=0)
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(left, bg=THEME_BG)
        btn_frame.pack(fill=tk.X)

        self.decode_btn = tk.Button(btn_frame, text="🚀  Decode", bg=THEME_ACCENT, fg="white",
                                     font=("Segoe UI", 12, "bold"), border=0,
                                     activebackground="#ff6b81", activeforeground="white",
                                     command=self._start_decode, height=2)
        self.decode_btn.pack(fill=tk.X, pady=(0, 5))
        self.decode_btn.bind("<Enter>", lambda e: self.decode_btn.configure(bg="#ff6b81"))
        self.decode_btn.bind("<Leave>", lambda e: self.decode_btn.configure(bg=THEME_ACCENT))

        export_row = tk.Frame(left, bg=THEME_BG)
        export_row.pack(fill=tk.X)
        self.save_pdf_btn = tk.Button(export_row, text="📄  Export PDF", bg=THEME_PRIMARY, fg=THEME_TEXT,
                                       font=("Segoe UI", 10), border=0,
                                       command=self._export_pdf, state="disabled")
        self.save_pdf_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.save_txt_btn = tk.Button(export_row, text="📝  Export TXT", bg=THEME_PRIMARY, fg=THEME_TEXT,
                                       font=("Segoe UI", 10), border=0,
                                       command=self._export_txt, state="disabled")
        self.save_txt_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        self.save_img_btn = tk.Button(export_row, text="🖼️  Export PNG", bg=THEME_PRIMARY, fg=THEME_TEXT,
                                       font=("Segoe UI", 10), border=0,
                                       command=self._export_img, state="disabled")
        self.save_img_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        # Right column — results
        right = tk.Frame(main, bg=THEME_BG)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Image preview
        self.canvas = tk.Canvas(right, bg="#0d0d1a", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        # Decoded text output
        text_frame = tk.LabelFrame(right, text="📖  Decoded Message", bg=THEME_BG, fg=THEME_TEXT,
                                    font=("Segoe UI", 10, "bold"), pad=5)
        text_frame.pack(fill=tk.X)

        self.text_display = tk.Text(text_frame, height=4, bg=THEME_SURFACE, fg="#00ff88",
                                     font=("Courier", 14, "bold"), border=0, padx=10, pady=8,
                                     insertbackground=THEME_ACCENT, wrap=tk.WORD)
        self.text_display.pack(fill=tk.X)
        self.text_display.insert("1.0", "Decoded text will appear here...")
        self.text_display.config(state="disabled")

        # Keyboard shortcuts
        self.window.bind("<Control-o>", lambda e: self._browse())
        self.window.bind("<Control-d>", lambda e: self._start_decode())
        self.window.bind("<Return>", lambda e: self._start_decode())

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select Ghost Font Video",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All files", "*.*")],
        )
        if path:
            self._set_video(path)

    def _set_video(self, path):
        self.video_path = path
        name = Path(path).name
        self.drop_label.configure(text=f"🎬  {name}", fg=THEME_TEXT, font=("Segoe UI", 11))
        self.status_var.set(f"Loaded: {name}  |  Ready to decode")
        self.decode_btn.configure(state="normal")

    def _start_decode(self):
        if not self.video_path:
            self._browse()
            return

        self._set_controls_enabled(False)
        self.progress["value"] = 0
        self.status_var.set("Decoding...")
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", "Processing video frames...")
        self.text_display.config(state="disabled")

        threading.Thread(target=self._decode_worker, daemon=True).start()

    def _decode_worker(self):
        def progress_cb(pct, msg):
            self.window.after(0, lambda: self.progress.configure(value=pct))
            self.window.after(0, lambda: self.status_var.set(msg))

        try:
            img, text = decode(
                self.video_path,
                threshold=self.threshold_var.get(),
                blur=self.blur_var.get(),
                method=self.method_var.get(),
                progress_callback=progress_cb,
            )
            self.result_image = img
            self.result_text = text

            # Show image
            rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            pil_img = Image.fromarray(rgb)
            self.window.after(0, lambda: self._show_image(pil_img))

            # Show decoded text
            display_text = text if text else "(no text detected — try different settings)"
            self.window.after(0, lambda: self._show_text(display_text))

            motion = "Motion detected" if img.sum() > 0 else "Nothing found"
            self.window.after(0, lambda: self.status_var.set(
                f"Done — {img.shape[1]}x{img.shape[0]} | {motion}"
            ))
            self.window.after(0, lambda: self._set_controls_enabled(True))

        except Exception as e:
            self.window.after(0, lambda: self.status_var.set(f"Error: {e}"))
            self.window.after(0, lambda: self._set_controls_enabled(True))

    def _show_image(self, pil_img):
        cw = max(self.canvas.winfo_width(), 400)
        ch = max(self.canvas.winfo_height(), 300)
        pil_img.thumbnail((cw, ch), Image.LANCZOS)
        self.tk_result = ImageTk.PhotoImage(pil_img)
        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.tk_result)

    def _show_text(self, text):
        self.text_display.config(state="normal")
        self.text_display.delete("1.0", tk.END)
        self.text_display.insert("1.0", text)
        self.text_display.config(state="disabled")

    def _set_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.decode_btn.configure(state=state)
        for btn in [self.save_pdf_btn, self.save_txt_btn, self.save_img_btn]:
            btn.configure(state="normal" if enabled and self.result_text else "disabled")

    def _export_pdf(self):
        if self.result_image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                            filetypes=[("PDF", "*.pdf")])
        if path:
            export_pdf(self.result_text, self.result_image, path)
            self.status_var.set(f"PDF saved to {Path(path).name}")

    def _export_txt(self):
        if self.result_text is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text", "*.txt")])
        if path:
            export_text(self.result_text, path)
            self.status_var.set(f"Text saved to {Path(path).name}")

    def _export_img(self):
        if self.result_image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG", "*.png")])
        if path:
            save_result(self.result_image, path)
            self.status_var.set(f"Image saved to {Path(path).name}")

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    GhostDecoderGUI().run()
