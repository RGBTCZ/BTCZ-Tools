import threading
from datetime import datetime

import customtkinter as ctk

from app.core import settings
from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle
from modules.base_module import BaseModule
from modules.mining_tracker.tracker import API_POOLS, load_addresses

DIR_KEYS = ["dir.up", "dir.down", "dir.any"]
DIR_VALUES = {"dir.up": "up", "dir.down": "down", "dir.any": "any"}


class NotificationsModule(BaseModule):
    key = "notifications"
    name_key = "nav.notifications"
    icon = "🔔"

    def set_services(self, notifier, monitor):
        self.notifier = notifier
        self.monitor = monitor
        if getattr(self, "built", False):
            self._render_history()
            self._render_status()

    def build(self):
        self.notifier = getattr(self, "notifier", None)
        self.monitor = getattr(self, "monitor", None)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.title_lbl = ctk.CTkLabel(header, text=t("notif.title"), font=font(24, "bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w")
        self.test_btn = ctk.CTkButton(header, text=t("notif.test"), width=200,
                                      fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                                      command=self.send_test)
        self.test_btn.grid(row=0, column=1, sticky="e")

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, padx=20, pady=(6, 6), sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(self, text="", font=font(11), text_color=COLORS["muted"], anchor="w")
        self.status.grid(row=2, column=0, padx=26, pady=(0, 12), sticky="ew")

        self._build_controls()
        self._load_settings()
        self._render_status()
        self._render_history()

    def _card(self, row):
        frame = ctk.CTkFrame(self.body, fg_color=COLORS["card"], corner_radius=14)
        frame.grid(row=row, column=0, sticky="ew", pady=6)
        frame.grid_columnconfigure(1, weight=1)
        return frame

    def _build_controls(self):
        self.status_banner = ctk.CTkLabel(self.body, text="", font=font(12), text_color=COLORS["muted"],
                                          wraplength=820, justify="left", anchor="w")
        self.status_banner.grid(row=0, column=0, sticky="ew", pady=(2, 8))

        SectionTitle(self.body, text=t("notif.sec_alerts")).grid(row=1, column=0, sticky="w", pady=(4, 2))

        price = self._card(2)
        price.grid_columnconfigure(0, weight=1)
        self.sw_price = ctk.CTkSwitch(price, text=t("notif.price_label"), command=self._save_toggles)
        self.sw_price.grid(row=0, column=0, columnspan=3, padx=16, pady=(14, 2), sticky="w")
        self.lbl_price_help = ctk.CTkLabel(price, text=t("notif.price_help"), text_color=COLORS["muted"],
                                           font=font(11), anchor="w")
        self.lbl_price_help.grid(row=1, column=0, columnspan=3, padx=16, pady=(0, 6), sticky="w")
        self.e_price = ctk.CTkEntry(price, width=180, placeholder_text=t("notif.price_ph"), height=34)
        self.e_price.grid(row=2, column=0, padx=16, pady=(0, 6), sticky="w")
        self.lbl_dir = ctk.CTkLabel(price, text=t("notif.price_dir"), text_color=COLORS["muted"])
        self.lbl_dir.grid(row=2, column=1, padx=(6, 6), pady=(0, 6), sticky="e")
        self.opt_dir = ctk.CTkOptionMenu(price, values=[t(k) for k in DIR_KEYS], width=150,
                                         fg_color=COLORS["sidebar"], button_color=COLORS["accent_dark"],
                                         button_hover_color=COLORS["accent"])
        self.opt_dir.grid(row=2, column=2, padx=(0, 16), pady=(0, 6))
        self.lbl_price_now = ctk.CTkLabel(price, text=t("notif.price_now", p="…"), text_color=COLORS["info"],
                                          font=font(11), anchor="w")
        self.lbl_price_now.grid(row=3, column=0, columnspan=3, padx=16, pady=(0, 14), sticky="w")

        payout = self._card(3)
        self.sw_payout = ctk.CTkSwitch(payout, text=t("notif.payout_label"), command=self._save_toggles)
        self.sw_payout.grid(row=0, column=0, padx=16, pady=14, sticky="w")
        self.lbl_payout_hint = ctk.CTkLabel(payout, text=t("notif.payout_hint"), text_color=COLORS["muted"],
                                            font=font(11))
        self.lbl_payout_hint.grid(row=0, column=1, padx=16, pady=14, sticky="e")

        rig = self._card(4)
        self.sw_rig = ctk.CTkSwitch(rig, text=t("notif.rig_label"), command=self._save_toggles)
        self.sw_rig.grid(row=0, column=0, columnspan=3, padx=16, pady=(14, 6), sticky="w")
        self.opt_pool = ctk.CTkOptionMenu(rig, values=API_POOLS or ["--"], width=170,
                                          fg_color=COLORS["sidebar"], button_color=COLORS["accent_dark"],
                                          button_hover_color=COLORS["accent"])
        self.opt_pool.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")
        self.cb_addr = ctk.CTkComboBox(rig, values=load_addresses() or [""], width=360, height=34)
        self.cb_addr.grid(row=1, column=1, columnspan=2, padx=(0, 16), pady=(0, 14), sticky="ew")

        diff = self._card(5)
        self.sw_diff = ctk.CTkSwitch(diff, text=t("notif.diff_label"), command=self._save_toggles)
        self.sw_diff.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="w")
        self.lbl_thr = ctk.CTkLabel(diff, text=t("notif.diff_thr"), text_color=COLORS["muted"])
        self.lbl_thr.grid(row=1, column=0, padx=16, pady=(0, 14), sticky="w")
        self.e_diff = ctk.CTkEntry(diff, width=100, placeholder_text="5", height=34)
        self.e_diff.grid(row=1, column=1, padx=(0, 16), pady=(0, 14), sticky="w")

        interval = self._card(6)
        self.lbl_interval = ctk.CTkLabel(interval, text=t("notif.interval"), text_color=COLORS["text"])
        self.lbl_interval.grid(row=0, column=0, padx=16, pady=14, sticky="w")
        self.e_interval = ctk.CTkEntry(interval, width=100, placeholder_text="90", height=34)
        self.e_interval.grid(row=0, column=1, padx=16, pady=14, sticky="w")
        self.save_btn = ctk.CTkButton(interval, text=t("notif.save"), width=160, command=self.save_settings)
        self.save_btn.grid(row=0, column=2, padx=16, pady=14, sticky="e")

        hist_head = ctk.CTkFrame(self.body, fg_color="transparent")
        hist_head.grid(row=7, column=0, sticky="ew", pady=(16, 4))
        hist_head.grid_columnconfigure(0, weight=1)
        self.hist_title = SectionTitle(hist_head, text=t("notif.sec_history"))
        self.hist_title.grid(row=0, column=0, sticky="w")
        self.clear_btn = ctk.CTkButton(hist_head, text=t("notif.clear_all"), width=120, height=30,
                                       fg_color="#2b2b2b", hover_color=COLORS["danger"],
                                       command=self.clear_history)
        self.clear_btn.grid(row=0, column=1, sticky="e")
        self.hist_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.hist_frame.grid(row=8, column=0, sticky="ew")
        self.hist_frame.grid_columnconfigure(0, weight=1)

    def retranslate(self):
        if not self.built:
            return
        self.title_lbl.configure(text=t("notif.title"))
        self.test_btn.configure(text=t("notif.test"))
        self.sw_price.configure(text=t("notif.price_label"))
        self.lbl_price_help.configure(text=t("notif.price_help"))
        self.e_price.configure(placeholder_text=t("notif.price_ph"))
        self.lbl_dir.configure(text=t("notif.price_dir"))
        self.opt_dir.configure(values=[t(k) for k in DIR_KEYS])
        self.sw_payout.configure(text=t("notif.payout_label"))
        self.lbl_payout_hint.configure(text=t("notif.payout_hint"))
        self.sw_rig.configure(text=t("notif.rig_label"))
        self.sw_diff.configure(text=t("notif.diff_label"))
        self.lbl_thr.configure(text=t("notif.diff_thr"))
        self.lbl_interval.configure(text=t("notif.interval"))
        self.save_btn.configure(text=t("notif.save"))
        self.hist_title.configure(text=t("notif.sec_history"))
        self.clear_btn.configure(text=t("notif.clear_all"))
        self._load_settings()
        self._render_status()
        self._render_history()
        self._update_price_hint()

    def refresh(self):
        self.cb_addr.configure(values=load_addresses() or [""])
        self._render_status()
        self._render_history()
        self._update_price_hint()

    def _update_price_hint(self):
        threading.Thread(target=self._fetch_price_hint, daemon=True).start()

    def _fetch_price_hint(self):
        try:
            market = self.datalayer.get_market()
            price = self._fmt_price(market.price_eur)
            self.lbl_price_now.configure(text=t("notif.price_now", p=price or "—"))
        except Exception:
            self.lbl_price_now.configure(text=t("notif.price_now", p="—"))

    def _dir_from_value(self, value):
        for key, val in DIR_VALUES.items():
            if val == value:
                return t(key)
        return t("dir.any")

    def _load_settings(self):
        self._set_switch(self.sw_price, settings.get("alert_price_on", False))
        self._set_switch(self.sw_payout, settings.get("alert_payout_on", False))
        self._set_switch(self.sw_rig, settings.get("alert_rig_on", False))
        self._set_switch(self.sw_diff, settings.get("alert_diff_on", False))
        self._set_entry(self.e_price, self._fmt_price(settings.get("alert_price_target", "")))
        self.opt_dir.set(self._dir_from_value(settings.get("alert_price_dir", "any")))
        pool = settings.get("alert_rig_pool", "")
        if pool in (API_POOLS or []):
            self.opt_pool.set(pool)
        elif API_POOLS:
            self.opt_pool.set(API_POOLS[0])
        self.cb_addr.set(settings.get("alert_rig_addr", "") or "")
        self._set_entry(self.e_diff, settings.get("alert_diff_threshold", 5.0))
        self._set_entry(self.e_interval, settings.get("alert_interval", 90))

    def _fmt_price(self, value):
        try:
            num = float(value)
        except (ValueError, TypeError):
            return ""
        if num <= 0:
            return ""
        return f"{num:.8f}".rstrip("0").rstrip(".")

    def _set_switch(self, sw, on):
        sw.select() if on else sw.deselect()

    def _set_entry(self, entry, value):
        entry.delete(0, "end")
        if value not in ("", None):
            entry.insert(0, str(value))

    def _save_toggles(self):
        settings.set("alert_price_on", bool(self.sw_price.get()))
        settings.set("alert_payout_on", bool(self.sw_payout.get()))
        settings.set("alert_rig_on", bool(self.sw_rig.get()))
        settings.set("alert_diff_on", bool(self.sw_diff.get()))

    def save_settings(self):
        self._save_toggles()
        settings.set("alert_price_target", self._float(self.e_price.get(), 0.0))
        for key in DIR_KEYS:
            if self.opt_dir.get() == t(key):
                settings.set("alert_price_dir", DIR_VALUES[key])
                break
        settings.set("alert_rig_pool", self.opt_pool.get() if self.opt_pool.get() in (API_POOLS or []) else "")
        settings.set("alert_rig_addr", self.cb_addr.get().strip())
        settings.set("alert_diff_threshold", self._float(self.e_diff.get(), 5.0))
        settings.set("alert_interval", int(self._float(self.e_interval.get(), 90)))
        self.status.configure(text=t("notif.saved"))

    def send_test(self):
        if self.notifier is not None:
            self.notifier.notify(t("notif.test_title"), t("notif.test_body"))
        self._render_history()

    def clear_history(self):
        if self.notifier is not None:
            self.notifier.clear_history()
        self._render_history()

    def delete_one(self, index):
        if self.notifier is not None:
            self.notifier.remove_at(index)
        self._render_history()

    def _float(self, text, default):
        try:
            return float(str(text).replace(",", ".").strip())
        except (ValueError, AttributeError):
            return default

    def _render_status(self):
        if self.notifier is not None and self.notifier.available():
            self.status_banner.configure(text="🟢  " + t("notif.tray_ok"), text_color=COLORS["ok"])
        else:
            self.status_banner.configure(text="🟡  " + t("notif.tray_off"), text_color=COLORS["warn"])

    def _render_history(self):
        for widget in self.hist_frame.winfo_children():
            widget.destroy()
        history = self.notifier.history if self.notifier is not None else []
        if not history:
            ctk.CTkLabel(self.hist_frame, text=t("notif.no_history"), font=font(12),
                         text_color=COLORS["muted"], anchor="w").grid(row=0, column=0, sticky="w", pady=6)
            return
        for i, (ts, title, message) in enumerate(history[:20]):
            row = ctk.CTkFrame(self.hist_frame, fg_color=COLORS["card"], corner_radius=10)
            row.grid(row=i, column=0, sticky="ew", pady=3)
            row.grid_columnconfigure(1, weight=1)
            when = datetime.fromtimestamp(ts).strftime("%d/%m %H:%M")
            ctk.CTkLabel(row, text=when, font=font(11), text_color=COLORS["muted"], width=90,
                         anchor="w").grid(row=0, column=0, padx=(14, 8), pady=8, sticky="w")
            ctk.CTkLabel(row, text=f"{title} — {message}", font=font(12), text_color=COLORS["text"],
                         anchor="w", justify="left").grid(row=0, column=1, padx=(0, 14), pady=8, sticky="w")
            ctk.CTkButton(row, text="✕", width=30, height=26, fg_color="transparent",
                          hover_color=COLORS["danger"], text_color=COLORS["muted"],
                          command=lambda idx=i: self.delete_one(idx)).grid(row=0, column=2, padx=(0, 8), pady=6)
