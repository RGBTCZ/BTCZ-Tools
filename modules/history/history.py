import threading
from collections import defaultdict
from datetime import datetime, timezone

import customtkinter as ctk

from app.core import settings
from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.format import format_btcz
from modules.base_module import BaseModule
from modules.mining_tracker.tracker import load_addresses

PROJECTIONS = [("hist.p1m", 30), ("hist.p3m", 90), ("hist.p6m", 180), ("hist.p1y", 365)]


class HistoryModule(BaseModule):
    key = "history"
    name_key = "nav.history"
    icon = "📈"

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.title_lbl = ctk.CTkLabel(header, text=t("hist.title"), font=font(24, "bold"))
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
        self.title_lbl.configure(text=t("hist.title"))
        self.refresh_btn.configure(text=t("common.refresh"))
        self.refresh()

    def refresh(self):
        self.status.configure(text=t("hist.loading"))
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        addresses = load_addresses()
        if not addresses:
            self._clear()
            ctk.CTkLabel(self.body, text=t("hist.no_data"), font=font(13), text_color=COLORS["warn"],
                         anchor="w").grid(row=0, column=0, sticky="w", pady=12)
            self.status.configure(text="")
            return
        try:
            net = self.datalayer.get_network_stats()
            txs = self.datalayer.get_address_transactions(addresses[0], False)
        except Exception as exc:
            self.status.configure(text=t("st.net_unavailable", e=exc))
            return

        months = defaultdict(float)
        total_mined = 0.0
        now = datetime.now(timezone.utc).timestamp()
        avg_window = 0.0
        for tx in txs:
            if not tx.is_mining:
                continue
            total_mined += tx.value
            dt = datetime.fromtimestamp(tx.time, timezone.utc)
            months[f"{dt.year}-{dt.month:02d}"] += tx.value
            if tx.time >= now - 30 * 86400:
                avg_window += tx.value

        avg_day = avg_window / 30.0
        alerts = self._alerts(net.difficulty, total_mined)
        self._render(months, avg_day, alerts)
        self.status.configure(text=addresses[0])

    def _alerts(self, difficulty, total_mined):
        snap = settings.get("history_snapshot", {}) or {}
        alerts = []
        if snap:
            old_diff = float(snap.get("difficulty", 0) or 0)
            if old_diff > 0:
                pct = (difficulty - old_diff) / old_diff * 100
                if abs(pct) >= 0.5:
                    alerts.append(("diff", t("hist.alert_diff", v=f"{'+' if pct >= 0 else ''}{pct:.1f}%")))
            reward_delta = total_mined - float(snap.get("total_mined", 0) or 0)
            if reward_delta > 0:
                alerts.append(("reward", t("hist.alert_reward", v=format_btcz(reward_delta, 2))))
        settings.set("history_snapshot", {"difficulty": difficulty, "total_mined": total_mined})
        return alerts

    def _clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def _render(self, months, avg_day, alerts):
        self._clear()
        row = 0

        SectionTitle(self.body, text=t("sec.alerts")).grid(row=row, column=0, pady=(4, 6), sticky="w")
        row += 1
        if alerts:
            for kind, text in alerts:
                color = COLORS["warn"] if kind == "diff" else COLORS["ok"]
                ctk.CTkLabel(self.body, text=f"🔔  {text}", font=font(13), text_color=color, anchor="w").grid(
                    row=row, column=0, sticky="w", pady=2)
                row += 1
        else:
            ctk.CTkLabel(self.body, text=t("hist.alert_none"), font=font(12), text_color=COLORS["muted"],
                         anchor="w").grid(row=row, column=0, sticky="w")
            row += 1

        keys = sorted(months.keys())
        this_key = keys[-1] if keys else None
        last_key = keys[-2] if len(keys) >= 2 else None
        this_val = months.get(this_key, 0.0) if this_key else 0.0
        last_val = months.get(last_key, 0.0) if last_key else 0.0
        change = ((this_val - last_val) / last_val * 100) if last_val > 0 else 0.0

        cmp_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        cmp_frame.grid(row=row, column=0, pady=(14, 4), sticky="ew")
        row += 1
        for i in range(3):
            cmp_frame.grid_columnconfigure(i, weight=1, uniform="cmp")
        c1 = StatCard(cmp_frame, t("hist.this_month"))
        c1.update_value(f"{format_btcz(this_val, 2)}", subtitle="BTCZ", accent=COLORS["accent"])
        c1.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        c2 = StatCard(cmp_frame, t("hist.last_month"))
        c2.update_value(f"{format_btcz(last_val, 2)}", subtitle="BTCZ")
        c2.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        c3 = StatCard(cmp_frame, t("hist.change"))
        ch_color = COLORS["ok"] if change >= 0 else COLORS["err"]
        c3.update_value(f"{'+' if change >= 0 else ''}{change:.1f} %", accent=ch_color)
        c3.grid(row=0, column=2, padx=6, pady=6, sticky="ew")

        SectionTitle(self.body, text=t("sec.history")).grid(row=row, column=0, pady=(14, 6), sticky="w")
        row += 1
        recent = keys[-8:]
        max_val = max((months[k] for k in recent), default=1) or 1
        bars = ctk.CTkFrame(self.body, fg_color="transparent")
        bars.grid(row=row, column=0, sticky="ew")
        row += 1
        bars.grid_columnconfigure(1, weight=1)
        for r, key in enumerate(reversed(recent)):
            label = datetime.strptime(key, "%Y-%m").strftime("%b %Y")
            ctk.CTkLabel(bars, text=label, font=font(12), text_color=COLORS["muted"], width=80, anchor="w").grid(
                row=r, column=0, padx=(0, 8), pady=3, sticky="w")
            bar = ctk.CTkProgressBar(bars, height=14, progress_color=COLORS["accent"])
            bar.set(months[key] / max_val)
            bar.grid(row=r, column=1, sticky="ew", pady=3)
            ctk.CTkLabel(bars, text=f"{format_btcz(months[key], 0)}", font=font(12, "bold"),
                        text_color=COLORS["text"], width=110, anchor="e").grid(row=r, column=2, padx=(8, 0), pady=3)

        SectionTitle(self.body, text=t("sec.projection")).grid(row=row, column=0, pady=(16, 4), sticky="w")
        row += 1
        ctk.CTkLabel(self.body, text=t("hist.avg", v=format_btcz(avg_day, 2)), font=font(11),
                     text_color=COLORS["muted"], anchor="w").grid(row=row, column=0, sticky="w")
        row += 1
        proj = ctk.CTkFrame(self.body, fg_color="transparent")
        proj.grid(row=row, column=0, pady=(6, 4), sticky="ew")
        row += 1
        for i in range(4):
            proj.grid_columnconfigure(i, weight=1, uniform="proj")
        for i, (key, days) in enumerate(PROJECTIONS):
            card = StatCard(proj, t(key))
            card.update_value(f"{format_btcz(avg_day * days, 0)}", subtitle="BTCZ", accent=COLORS["mine"])
            card.grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        ctk.CTkLabel(self.body, text=t("hist.proj_note"), font=font(11), text_color=COLORS["muted"],
                     wraplength=760, justify="left", anchor="w").grid(row=row, column=0, sticky="w", pady=(8, 6))
