import customtkinter as ctk

COLORS = {
    "bg": "#0d0f0e",
    "sidebar": "#141816",
    "card": "#1a1f1c",
    "card_hover": "#222824",
    "accent": "#3DDC97",
    "accent_dark": "#2b9e6d",
    "console_bg": "#0f1211",
    "scroll": "#2b332e",
    "text": "#e8e8e8",
    "muted": "#9aa0a6",
    "ok": "#3DDC97",
    "err": "#FF6B6B",
    "warn": "#F4C430",
    "info": "#7EC8E3",
    "mine": "#FFD166",
    "title": "#C084FC",
    "danger": "#8B1E1E",
    "danger_hover": "#A82828",
}


def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")


def font(size=13, weight="normal"):
    return ctk.CTkFont(size=size, weight=weight)
