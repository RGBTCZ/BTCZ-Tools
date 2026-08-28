import tkinter as tk

import customtkinter as ctk

from app.ui.theme import COLORS, font


class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value="--", subtitle="", accent=None, **kwargs):
        super().__init__(master, corner_radius=14, fg_color=COLORS["card"], **kwargs)
        self.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self,
            text=title.upper(),
            font=font(11, "bold"),
            text_color=COLORS["muted"],
        )
        self.title_lbl.grid(row=0, column=0, padx=16, pady=(14, 2), sticky="w")

        self.value_lbl = ctk.CTkLabel(
            self,
            text=value,
            font=font(22, "bold"),
            text_color=accent or COLORS["text"],
        )
        self.value_lbl.grid(row=1, column=0, padx=16, pady=(0, 2), sticky="w")

        self.sub_lbl = ctk.CTkLabel(
            self,
            text=subtitle,
            font=font(11),
            text_color=COLORS["muted"],
        )
        self.sub_lbl.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")

        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        wrap = max(event.width - 28, 40)
        self.title_lbl.configure(wraplength=wrap)
        self.value_lbl.configure(wraplength=wrap)
        self.sub_lbl.configure(wraplength=wrap)

    def set_title(self, title):
        self.title_lbl.configure(text=title.upper())

    def update_value(self, value, subtitle=None, accent=None):
        self.value_lbl.configure(text=value)
        if accent:
            self.value_lbl.configure(text_color=accent)
        if subtitle is not None:
            self.sub_lbl.configure(text=subtitle)


class SectionTitle(ctk.CTkLabel):
    def __init__(self, master, text, **kwargs):
        super().__init__(
            master,
            text=text,
            font=font(16, "bold"),
            text_color=COLORS["title"],
            anchor="w",
            **kwargs,
        )


class LogConsole(ctk.CTkFrame):
    TAGS = {
        "ok": COLORS["ok"],
        "err": COLORS["err"],
        "warn": COLORS["warn"],
        "info": COLORS["info"],
        "mine": COLORS["mine"],
        "title": COLORS["title"],
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=12, fg_color=COLORS["card"], **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.text = tk.Text(
            self,
            wrap="word",
            bg=COLORS["console_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            font=("Consolas", 11),
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=14,
            pady=12,
        )
        self.text.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)

        self.scroll = ctk.CTkScrollbar(
            self,
            command=self.text.yview,
            fg_color="transparent",
            button_color=COLORS["scroll"],
            button_hover_color=COLORS["accent"],
            width=14,
        )
        self.scroll.grid(row=0, column=1, sticky="ns", padx=(2, 8), pady=8)
        self.text.configure(yscrollcommand=self.scroll.set)

        for tag, color in self.TAGS.items():
            self.text.tag_config(tag, foreground=color)

    def log(self, text, tag="info"):
        self.text.insert("end", text + "\n", tag)
        self.text.see("end")
        self.update_idletasks()

    def clear(self):
        self.text.delete("1.0", "end")


class Placeholder(ctk.CTkFrame):
    def __init__(self, master, title, message, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title_lbl = ctk.CTkLabel(
            self, text=title, font=font(24, "bold"), text_color=COLORS["accent"]
        )
        self.title_lbl.grid(row=1, column=0, pady=(0, 8))
        self.msg_lbl = ctk.CTkLabel(
            self,
            text=message,
            font=font(14),
            text_color=COLORS["muted"],
            wraplength=520,
            justify="center",
        )
        self.msg_lbl.grid(row=2, column=0)

    def set_text(self, title, message):
        self.title_lbl.configure(text=title)
        self.msg_lbl.configure(text=message)
