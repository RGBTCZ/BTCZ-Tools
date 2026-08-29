import os
import sys
import threading
import webbrowser
from tkinter import filedialog

import customtkinter as ctk

from app.core.i18n import t
from app.core.updater import download_update
from app.ui.theme import COLORS, font


class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, master, info):
        super().__init__(master)
        self.info = info
        self.downloading = False
        self.title(t("update.title"))
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg"])
        self.transient(master)
        self.grab_set()

        wrap = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=16)
        wrap.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(wrap, text=t("update.title"), font=font(22, "bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(wrap, text=t("update.subtitle", v=info["latest"], c=info["current"]),
                     font=font(14), text_color=COLORS["text"]).pack(anchor="w", padx=20)

        notes = info.get("notes") or ""
        if notes:
            ctk.CTkLabel(wrap, text=t("update.whatsnew"), font=font(12, "bold"),
                         text_color=COLORS["muted"]).pack(anchor="w", padx=20, pady=(14, 2))
            box = ctk.CTkTextbox(wrap, width=520, height=140, fg_color=COLORS["console_bg"],
                                 text_color=COLORS["text"], font=("Consolas", 12))
            box.pack(padx=20, pady=(0, 4))
            box.insert("1.0", notes[:1500])
            box.configure(state="disabled")

        ctk.CTkLabel(wrap, text=t("update.howto"), font=font(12), text_color=COLORS["muted"],
                     wraplength=520, justify="left").pack(anchor="w", padx=20, pady=(12, 8))

        self.progress = ctk.CTkProgressBar(wrap, width=520, progress_color=COLORS["accent"])
        self.progress.set(0)
        self.status = ctk.CTkLabel(wrap, text="", font=font(12), text_color=COLORS["muted"],
                                   wraplength=520, justify="left")

        buttons = ctk.CTkFrame(wrap, fg_color="transparent")
        buttons.pack(fill="x", padx=20, pady=(6, 18))
        self.later_btn = ctk.CTkButton(buttons, text=t("update.later"), width=100,
                                       fg_color="#2b2b2b", hover_color=COLORS["card_hover"],
                                       command=self.destroy)
        self.later_btn.pack(side="right")
        self.github_btn = ctk.CTkButton(buttons, text=t("update.github"), width=140,
                                        fg_color=COLORS["sidebar"], hover_color=COLORS["card_hover"],
                                        command=lambda: webbrowser.open(info.get("html_url", "")))
        self.github_btn.pack(side="right", padx=(0, 8))
        if info.get("asset_url"):
            self.dl_btn = ctk.CTkButton(buttons, text=t("update.download"), width=170,
                                        fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                                        command=self.start_download)
            self.dl_btn.pack(side="right", padx=(0, 8))
        else:
            self.dl_btn = None

        self.after(60, self._center)

    def _center(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + (self.master.winfo_width() - self.winfo_width()) // 2
        y = self.master.winfo_rooty() + 120
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def start_download(self):
        if self.downloading:
            return
        default_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.expanduser("~")
        out_dir = filedialog.askdirectory(initialdir=default_dir)
        if not out_dir:
            return
        dest = os.path.join(out_dir, self.info["asset_name"])
        self.downloading = True
        self.dl_btn.configure(state="disabled")
        self.later_btn.configure(state="disabled")
        self.progress.pack(padx=20, pady=(4, 2))
        self.status.pack(anchor="w", padx=20, pady=(0, 6))
        self.status.configure(text=t("update.downloading", p=0))
        threading.Thread(target=self._worker, args=(dest, out_dir), daemon=True).start()

    def _worker(self, dest, out_dir):
        def cb(ratio):
            pct = int(ratio * 100)
            self.progress.set(ratio)
            self.status.configure(text=t("update.downloading", p=pct))
        try:
            download_update(self.info["asset_url"], dest, progress_cb=cb)
            self.status.configure(text=t("update.done", p=dest) + "\n" + t("update.done_hint"),
                                  text_color=COLORS["ok"])
            self.later_btn.configure(state="normal")
            self.dl_btn.configure(state="normal", text=t("update.open_folder"),
                                  command=lambda: self._open_folder(out_dir))
        except Exception as exc:
            self.status.configure(text=t("update.error", e=exc), text_color=COLORS["err"])
            self.dl_btn.configure(state="normal")
            self.later_btn.configure(state="normal")
        finally:
            self.downloading = False

    def _open_folder(self, path):
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                webbrowser.open(f"file://{path}")
            else:
                webbrowser.open(f"file://{path}")
        except Exception:
            pass
