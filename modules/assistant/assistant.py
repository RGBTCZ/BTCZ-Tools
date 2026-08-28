import threading

import customtkinter as ctk

from app.core import settings
from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.analyst import analyze
from app.utils.format import SOL_UNITS, format_hashrate
from config.config import POOLS
from modules.base_module import BaseModule

LEVEL_ICON = {"ok": "✅", "warn": "⚠️", "info": "💡", "target": "🎯"}
LEVEL_COLOR = {"ok": COLORS["ok"], "warn": COLORS["warn"], "info": COLORS["info"], "target": COLORS["mine"]}


class AssistantModule(BaseModule):
    key = "assistant"
    name_key = "nav.assistant"
    icon = "🚀"

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.title_lbl = ctk.CTkLabel(header, text=t("assist.title"), font=font(24, "bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w")
        self.refresh_btn = ctk.CTkButton(header, text=t("common.refresh"), width=110, command=self.refresh)
        self.refresh_btn.grid(row=0, column=1, sticky="e")

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, padx=20, pady=(6, 6), sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(self, text="", font=font(11), text_color=COLORS["muted"], anchor="w")
        self.status.grid(row=2, column=0, padx=26, pady=(0, 12), sticky="ew")

    def retranslate(self):
        if not self.built:
            return
        self.title_lbl.configure(text=t("assist.title"))
        self.refresh_btn.configure(text=t("common.refresh"))
        self.refresh()

    def refresh(self):
        self.status.configure(text=t("assist.loading"))
        threading.Thread(target=self._load, daemon=True).start()

    def _num(self, saved, key, default=0.0):
        try:
            return float(str(saved.get(key, "")).replace(",", ".") or default)
        except ValueError:
            return default

    def _load(self):
        saved = settings.get("profitability", {}) or {}
        hashrate = self._num(saved, "hashrate")
        if hashrate <= 0:
            self._clear()
            ctk.CTkLabel(self.body, text=t("assist.no_setup"), font=font(13), text_color=COLORS["warn"],
                         anchor="w").grid(row=0, column=0, sticky="w", pady=12)
            self.status.configure(text="")
            return
        try:
            net = self.datalayer.get_network_stats()
            market = self.datalayer.get_market()
        except Exception as exc:
            self.status.configure(text=t("st.net_unavailable", e=exc))
            return

        unit = saved.get("unit", "KSol/s")
        hashrate_solps = hashrate * SOL_UNITS.get(unit, 1)
        power = self._num(saved, "power")
        elec = self._num(saved, "elec")
        fee = self._num(saved, "pool_fee")
        hardware = self._num(saved, "hardware")

        active_pools = [p for p in POOLS if p.get("active") and p.get("fee") is not None]
        best_pool = min(active_pools, key=lambda p: p["fee"]) if active_pools else None

        insights, _ = analyze(hashrate_solps, power, elec, fee, hardware, market.price_eur,
                              net.network_hashps(), net.block_time, net.miner_reward, best_pool)
        self._render(saved, hashrate_solps, unit, power, elec, fee, hardware, insights)
        self.status.configure(text=t("st.sources", s=net.source))

    def _clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def _render(self, saved, hashrate_solps, unit, power, elec, fee, hardware, insights):
        self._clear()
        row = 0

        SectionTitle(self.body, text=t("sec.setup")).grid(row=row, column=0, pady=(4, 6), sticky="w")
        row += 1
        setup = ctk.CTkFrame(self.body, fg_color="transparent")
        setup.grid(row=row, column=0, sticky="ew")
        row += 1
        cells = [
            (t("prof.hashrate"), format_hashrate(hashrate_solps)),
            (t("prof.power"), f"{power:.0f} W"),
            (t("prof.elec"), f"{elec:.2f} €/kWh"),
            (t("prof.pool_fee"), f"{fee:.2f} %"),
            (t("prof.hardware"), f"{hardware:.0f} €" if hardware > 0 else t("pool.unknown")),
        ]
        for i, (title, value) in enumerate(cells):
            setup.grid_columnconfigure(i, weight=1, uniform="setup")
            card = StatCard(setup, title)
            card.value_lbl.configure(font=font(16, "bold"))
            card.update_value(value)
            card.grid(row=0, column=i, padx=5, pady=6, sticky="ew")

        SectionTitle(self.body, text=t("sec.analysis")).grid(row=row, column=0, pady=(16, 6), sticky="w")
        row += 1
        for level, key, params in insights:
            icon = LEVEL_ICON.get(level, "•")
            color = LEVEL_COLOR.get(level, COLORS["text"])
            ctk.CTkLabel(self.body, text=f"{icon}  {t(key, **params)}", font=font(13),
                         text_color=color, anchor="w", justify="left", wraplength=780).grid(
                row=row, column=0, sticky="w", pady=4)
            row += 1
