import customtkinter as ctk
import os
import threading
import asyncio
import sys
from typing import Optional
from tkinter import filedialog, messagebox

# Import webtoon downloader core components
from webtoon_downloader.core.webtoon.downloaders import comic
from webtoon_downloader.core.webtoon.downloaders.options import WebtoonDownloadOptions, StorageType
from webtoon_downloader.transformers.image import ImageFormat
from webtoon_downloader.core.webtoon.exporter import DataExporterFormat
from webtoon_downloader.i18n import t

# Set appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class WebtoonDownloaderGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{t('APP_TITLE')} - Premium GUI")
        self.geometry("800x650")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 20))
        self.header_label = ctk.CTkLabel(self.header_frame, text=t("APP_TITLE"), font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=15)

        # Main Input Frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=0)
        self.input_frame.grid_columnconfigure(1, weight=1)

        # URL Input
        self.url_label = ctk.CTkLabel(self.input_frame, text=t("URL_LABEL"))
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text=t("URL_PLACEHOLDER"))
        self.url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        # Output Path
        self.out_label = ctk.CTkLabel(self.input_frame, text=t("DEST_LABEL"))
        self.out_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.out_entry = ctk.CTkEntry(self.input_frame)
        self.out_entry.insert(0, os.path.join(os.getcwd(), "downloads"))
        self.out_entry.grid(row=1, column=1, padx=(10, 0), pady=10, sticky="ew")
        self.browse_btn = ctk.CTkButton(self.input_frame, text=t("BROWSE"), width=80, command=self.browse_folder)
        self.browse_btn.grid(row=1, column=2, padx=10, pady=10)

        # Options Frame
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        
        # Save As
        self.save_as_label = ctk.CTkLabel(self.options_frame, text=t("SAVE_AS"))
        self.save_as_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.save_as_var = ctk.StringVar(value="images")
        self.save_as_menu = ctk.CTkOptionMenu(self.options_frame, values=["images", "zip", "cbz", "pdf"], variable=self.save_as_var)
        self.save_as_menu.grid(row=0, column=1, padx=10, pady=10)

        # Format
        self.format_label = ctk.CTkLabel(self.options_frame, text=t("IMAGE_FORMAT"))
        self.format_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        self.format_var = ctk.StringVar(value="jpg")
        self.format_menu = ctk.CTkOptionMenu(self.options_frame, values=["jpg", "png"], variable=self.format_var)
        self.format_menu.grid(row=0, column=3, padx=10, pady=10)

        # Range
        self.start_label = ctk.CTkLabel(self.options_frame, text=t("START_CHAPTER"))
        self.start_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.start_entry = ctk.CTkEntry(self.options_frame, width=100, placeholder_text=t("OPTIONAL"))
        self.start_entry.grid(row=1, column=1, padx=10, pady=10)

        self.end_label = ctk.CTkLabel(self.options_frame, text=t("END_CHAPTER"))
        self.end_label.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        self.end_entry = ctk.CTkEntry(self.options_frame, width=100, placeholder_text=t("OPTIONAL"))
        self.end_entry.grid(row=1, column=3, padx=10, pady=10)

        # Progress / Log Frame
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.p_bar = ctk.CTkProgressBar(self.log_frame)
        self.p_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.p_bar.set(0)

        self.log_text = ctk.CTkTextbox(self.log_frame)
        self.log_text.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Action Button
        self.download_btn = ctk.CTkButton(self, text=t("START_DOWNLOAD"), command=self.start_download_thread, height=40, font=ctk.CTkFont(weight="bold"))
        self.download_btn.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")

        # State
        self.loop = None
        self.is_downloading = False

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, folder)

    def log(self, message):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def progress_callback(self, current, total):
        # This is expected to be called by the downloader
        if total > 0:
            progress = current / total
            self.p_bar.set(progress)
            self.update_idletasks()

    def on_webtoon_fetched(self, webtoon):
        self.log(t("LOG_FETCHED", title=webtoon.title))
        self.log(t("LOG_COUNT", count=webtoon.chapters_count))

    def start_download_thread(self):
        if self.is_downloading:
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", t("ERROR_URL_REQUIRED"))
            return

        self.is_downloading = True
        self.download_btn.configure(state="disabled", text=t("DOWNLOADING"))
        self.log_text.delete("1.0", "end")
        self.log(t("LOG_STARTING"))

        # Get values
        try:
            start = int(self.start_entry.get()) if self.start_entry.get() else None
            end = int(self.end_entry.get()) if self.end_entry.get() else None
        except ValueError:
            messagebox.showerror("Error", t("ERROR_INVALID_RANGE"))
            self.is_downloading = False
            self.download_btn.configure(state="normal", text=t("START_DOWNLOAD"))
            return

        out_path = self.out_entry.get() or os.path.join(os.getcwd(), "downloads")
        save_as = self.save_as_var.get()
        img_format = self.format_var.get()

        opts = WebtoonDownloadOptions(
            url=url,
            start=start,
            end=end,
            destination=out_path,
            save_as=save_as,
            image_format=img_format,
            chapter_progress_callback=self.progress_callback,
            on_webtoon_fetched=self.on_webtoon_fetched,
            concurrent_chapters=8,
            concurrent_pages=10
        )

        threading.Thread(target=self.run_async_download, args=(opts,), daemon=True).start()

    def run_async_download(self, opts):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(comic.download_webtoon(opts))
            self.after(0, lambda: self.log(t("LOG_FINISHED")))
        except Exception as e:
            self.after(0, lambda: self.log(t("LOG_ERROR", message=str(e))))
        finally:
            self.after(0, self.reset_ui)
            loop.close()

    def reset_ui(self):
        self.is_downloading = False
        self.download_btn.configure(state="normal", text=t("START_DOWNLOAD"))
        self.p_bar.set(0)

if __name__ == "__main__":
    app = WebtoonDownloaderGUI()
    app.mainloop()
