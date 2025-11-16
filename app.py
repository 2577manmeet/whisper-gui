import threading
import traceback
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from transcriber import transcribe_file, check_ffmpeg


# Global appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class WhisperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Whisper GUI Transcriber")
        self.geometry("900x560")
        self.minsize(780, 480)

        self.selected_file: Path | None = None
        self.worker_thread = None

        # Main layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ---------- HEADER ---------------------------------------------------
        header = ctk.CTkFrame(self, fg_color=("gray13", "gray13"))
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Whisper GUI",
            font=("Segoe UI Semibold", 22),
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Local, privacy-friendly transcription with openai-whisper",
            font=("Segoe UI", 12),
            text_color=("gray80", "gray70"),
        )
        subtitle.grid(row=1, column=0, sticky="w")

        self.ffmpeg_status = ctk.CTkLabel(
            header,
            text="ffmpeg: unknown",
            text_color=("gray80", "gray70"),
            font=("Segoe UI", 11),
        )
        self.ffmpeg_status.grid(row=0, column=1, sticky="e", padx=(0, 8))

        btn_ffmpeg = ctk.CTkButton(
            header,
            text="Check ffmpeg",
            width=120,
            command=self.check_ffmpeg_clicked,
        )
        btn_ffmpeg.grid(row=1, column=1, sticky="e", pady=(4, 0))

        # ---------- BODY: two columns ---------------------------------------
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        body.grid_columnconfigure(0, weight=0)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # LEFT: controls card
        left = ctk.CTkFrame(
            body,
            corner_radius=14,
            fg_color=("gray15", "gray15"),
        )
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 10), pady=0)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left,
            text="Input & Settings",
            font=("Segoe UI Semibold", 14),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))

        # File selector "card"
        file_frame = ctk.CTkFrame(left, fg_color=("gray10", "gray10"))
        file_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 8))
        file_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            file_frame,
            text="Audio / Video file",
            font=("Segoe UI", 11),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 2))

        pick_btn = ctk.CTkButton(
            file_frame,
            text="Choose file…",
            width=110,
            command=self.pick_file,
        )
        pick_btn.grid(row=1, column=0, padx=8, pady=(4, 10), sticky="w")

        self.file_label = ctk.CTkLabel(
            file_frame,
            text="No file selected",
            anchor="w",
            text_color=("gray80", "gray65"),
            wraplength=220,
        )
        self.file_label.grid(row=1, column=1, padx=(0, 8), pady=(4, 10), sticky="ew")

        # Model settings "card"
        model_frame = ctk.CTkFrame(left, fg_color=("gray10", "gray10"))
        model_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
        model_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            model_frame,
            text="Model",
            font=("Segoe UI", 11),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(8, 2))

        ctk.CTkLabel(
            model_frame,
            text="Size",
            text_color=("gray80", "gray70"),
        ).grid(row=1, column=0, sticky="w", padx=8, pady=(4, 4))

        self.model_var = ctk.StringVar(value="base")
        self.model_combo = ctk.CTkComboBox(
            model_frame,
            variable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            width=150,
        )
        self.model_combo.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 8))

        ctk.CTkLabel(
            model_frame,
            text="Tip: tiny/base are fast • medium/large are higher quality",
            font=("Segoe UI", 10),
            text_color=("gray80", "gray65"),
            wraplength=260,
            justify="left",
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(0, 8))

        # Run button at bottom of left card
        self.run_button = ctk.CTkButton(
            left,
            text="Transcribe",
            height=40,
            command=self.transcribe_clicked,
        )
        self.run_button.grid(row=3, column=0, sticky="ew", padx=14, pady=(8, 14))

        # RIGHT: output panel
        right = ctk.CTkFrame(
            body,
            corner_radius=14,
            fg_color=("gray15", "gray15"),
        )
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right,
            text="Transcription log",
            font=("Segoe UI Semibold", 14),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 4))

        self.textbox = ctk.CTkTextbox(
            right,
            wrap="word",
            corner_radius=10,
        )
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))

        # Bottom row: progress + open folder
        bottom = ctk.CTkFrame(right, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
        bottom.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(bottom, height=10)
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.progress.set(0.0)

        open_output_btn = ctk.CTkButton(
            bottom,
            text="Open output folder",
            width=150,
            command=self.open_output_folder,
        )
        open_output_btn.grid(row=0, column=1, sticky="e")

    # ---------------------- Utility Methods ----------------------

    def log(self, msg: str):
        """Append text to the textbox on the main thread."""
        def _append():
            self.textbox.insert("end", msg + "\n")
            self.textbox.see("end")
        self.after(0, _append)

    def set_progress(self, value: float):
        """Set progress bar (0.0–1.0) safely on main thread."""
        def _set():
            self.progress.set(max(0.0, min(1.0, value)))
        self.after(0, _set)

    # ---------------------- File selection -----------------------

    def pick_file(self):
        f = filedialog.askopenfilename(
            title="Choose audio or video file",
            filetypes=[
                ("Media files", "*.mp3 *.mp4 *.wav *.m4a *.ogg *.flac *.webm"),
                ("All files", "*.*"),
            ],
        )
        if f:
            self.selected_file = Path(f)
            self.file_label.configure(text=str(self.selected_file))

    # ---------------------- Transcription ------------------------

    def transcribe_clicked(self):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showinfo("Busy", "Transcription is already running.")
            return

        if not self.selected_file:
            messagebox.showwarning("No file", "Please choose a file first.")
            return

        if not check_ffmpeg():
            messagebox.showwarning(
                "ffmpeg missing",
                "ffmpeg is not available on PATH.\n\n"
                "Install ffmpeg and make sure the 'ffmpeg' command works."
            )
            self.ffmpeg_status.configure(text="ffmpeg: missing ⚠")
            return
        else:
            self.ffmpeg_status.configure(text="ffmpeg: OK ✅")

        model = self.model_var.get()

        self.textbox.delete("1.0", "end")
        self.log(f"Selected file: {self.selected_file}")
        self.log(f"Model: {model} | Language: auto-detect")
        self.set_progress(0.0)

        self.run_button.configure(state="disabled", text="Transcribing…")

        def worker():
            try:
                result = transcribe_file(
                    str(self.selected_file),
                    model_name=model,
                    log=self.log,
                    progress=self.update_progress_from_segments,
                )
                self.log("")
                self.log("=== Done ===")
                self.log(f"Transcript saved to: {result['output_txt']}")
                self.log(f"SRT saved to:       {result['output_srt']}")
            except Exception as e:
                traceback.print_exc()
                self.log("")
                self.log("!!! Error during transcription !!!")
                self.log(f"{type(e).__name__}: {e}")
                messagebox.showerror("Error", f"{type(e).__name__}: {e}")
            finally:
                self.after(
                    0,
                    lambda: self.run_button.configure(
                        state="normal", text="Transcribe"
                    ),
                )
                self.set_progress(1.0)

        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def update_progress_from_segments(self, current: int, total: int):
        if total <= 0:
            self.set_progress(0.0)
        else:
            self.set_progress(current / total)

    # ---------------------- Misc buttons -------------------------

    def check_ffmpeg_clicked(self):
        if check_ffmpeg():
            self.ffmpeg_status.configure(text="ffmpeg: OK ✅")
            messagebox.showinfo("ffmpeg", "ffmpeg is available on PATH ✅")
        else:
            self.ffmpeg_status.configure(text="ffmpeg: missing ⚠")
            messagebox.showwarning(
                "ffmpeg",
                "ffmpeg was NOT found on PATH.\n\n"
                "Install ffmpeg and make sure the 'ffmpeg' command "
                "works in your terminal.",
            )

    def open_output_folder(self):
        out_dir = Path("output")
        out_dir.mkdir(exist_ok=True)
        try:
            import os
            os.startfile(out_dir.resolve())
        except Exception as e:
            messagebox.showerror("Open folder", f"Could not open folder: {e}")


if __name__ == "__main__":
    app = WhisperGUI()
    app.mainloop()
