import threading

import customtkinter as ctk

from app.core import settings
from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle
from app.utils.format import SOL_UNITS, format_btcz, format_hashrate, human_age
from app.utils.mining_calc import coins_per_day
from config.config import POOLS
from modules.base_module import BaseModule

MEDALS = ["🥇", "🥈", "🥉"]


class PoolExplorerModule(BaseModule):
    key = "pools"
    name_key = "nav.pools"
    icon = "🌊"

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.title_lbl = ctk.CTkLabel(header, text=t("title.pools"), font=font(24, "bold"))
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
        self.title_lbl.configure(text=t("title.pools"))
        self.refresh_btn.configure(text=t("common.refresh"))
        self.refresh()

    def refresh(self):
        self.status.configure(text=t("pool.loading"))
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        try:
            data = self.datalayer.get_pool_stats()
            net = self.datalayer.get_network_stats()
        except Exception as exc:
            self.status.configure(text=t("pool.unavailable", e=exc))
            return
        try:
            live = self.datalayer.get_pool_live()
        except Exception:
            live = {}
        reco = self._build_reco(net, live)
        self._render(data, reco, live)
        self.status.configure(text=t("st.blocks_count", n=data["window"], s=net.source))

    def _build_reco(self, net, live=None):
        live = live or {}
        saved = settings.get("profitability", {}) or {}
        try:
            hashrate = float(str(saved.get("hashrate", "")).replace(",", ".") or 0)
        except ValueError:
            hashrate = 0.0
        unit = saved.get("unit", "KSol/s")
        hashrate_solps = hashrate * SOL_UNITS.get(unit, 1)
        gross = None
        if hashrate_solps > 0:
            gross = coins_per_day(hashrate_solps, net.network_hashps(), net.block_time, net.miner_reward)

        rows = []
        for pool in POOLS:
            net_day = None
            if gross is not None and pool["fee"] is not None:
                net_day = gross * (1 - pool["fee"] / 100.0)
            active = pool.get("active", False)
            lv = live.get(pool["name"])
            if lv is not None and lv.ok:
                active = lv.miner_count > 0
            rows.append({
                "name": pool["name"],
                "fee": pool["fee"],
                "scheme": pool["scheme"],
                "min_pay": pool.get("min_pay"),
                "active": active,
                "net": net_day,
            })
        rows.sort(key=lambda r: (0 if r["active"] else 1, -(r["net"] if r["net"] is not None else -1)))
        active_count = sum(1 for r in rows if r["active"])
        return {"hashrate_solps": hashrate_solps, "expected_gross": gross, "rows": rows, "active_count": active_count}

    def _header_row(self, parent, cols):
        for i, (key, w) in enumerate(cols):
            parent.grid_columnconfigure(i, weight=w)
            ctk.CTkLabel(parent, text=t(key), font=font(11, "bold"),
                         text_color=COLORS["muted"], anchor="w").grid(
                row=0, column=i, padx=8, pady=(0, 4), sticky="w")

    def _render(self, data, reco, live=None):
        live = live or {}
        for widget in self.body.winfo_children():
            widget.destroy()
        row = 0

        SectionTitle(self.body, text=t("pool.distribution", n=data["window"])).grid(
            row=row, column=0, pady=(4, 6), sticky="w")
        row += 1
        dist = ctk.CTkFrame(self.body, fg_color="transparent")
        dist.grid(row=row, column=0, sticky="ew")
        row += 1
        self._header_row(dist, [("pool.col_pool", 3), ("pool.col_share", 3),
                                ("pool.col_blocks", 1), ("pool.col_hashrate", 2), ("pool.col_last", 1)])
        for i, pool in enumerate(data["pools"], start=1):
            name = t("pool.solo") if pool.is_solo else pool.name
            name_color = COLORS["muted"] if pool.is_solo else COLORS["accent"]
            ctk.CTkLabel(dist, text=name, font=font(13, "bold"), text_color=name_color, anchor="w").grid(
                row=i, column=0, padx=8, pady=4, sticky="w")
            cell = ctk.CTkFrame(dist, fg_color="transparent")
            cell.grid(row=i, column=1, padx=8, pady=4, sticky="ew")
            cell.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(cell, text=f"{pool.share * 100:.1f}%", font=font(12), width=52, anchor="w").grid(row=0, column=0)
            bar = ctk.CTkProgressBar(cell, height=8, progress_color=COLORS["accent"])
            bar.set(pool.share)
            bar.grid(row=0, column=1, sticky="ew", padx=(6, 0))
            ctk.CTkLabel(dist, text=str(pool.blocks_found), font=font(12), text_color=COLORS["text"], anchor="w").grid(
                row=i, column=2, padx=8, pady=4, sticky="w")
            ctk.CTkLabel(dist, text=format_hashrate(pool.est_hashps), font=font(12), text_color=COLORS["info"], anchor="w").grid(
                row=i, column=3, padx=8, pady=4, sticky="w")
            ctk.CTkLabel(dist, text=human_age(pool.last_time), font=font(12), text_color=COLORS["muted"], anchor="w").grid(
                row=i, column=4, padx=8, pady=4, sticky="w")

        SectionTitle(self.body, text=t("pool.live")).grid(row=row, column=0, pady=(18, 4), sticky="w")
        row += 1
        live_rows = [lv for lv in live.values() if lv.ok]
        if live_rows:
            livef = ctk.CTkFrame(self.body, fg_color="transparent")
            livef.grid(row=row, column=0, sticky="ew")
            row += 1
            self._header_row(livef, [("pool.col_pool", 3), ("pool.col_hashrate", 2),
                                     ("pool.col_share", 2), ("pool.col_workers", 1)])
            net_hashps = data.get("network_hashps", 0) or 0
            live_rows.sort(key=lambda lv: lv.hashps, reverse=True)
            for i, lv in enumerate(live_rows, start=1):
                share = (lv.hashps / net_hashps) if net_hashps > 0 else 0
                ctk.CTkLabel(livef, text=lv.name, font=font(13, "bold"), text_color=COLORS["accent"], anchor="w").grid(
                    row=i, column=0, padx=8, pady=4, sticky="w")
                ctk.CTkLabel(livef, text=format_hashrate(lv.hashps), font=font(12), text_color=COLORS["info"], anchor="w").grid(
                    row=i, column=1, padx=8, pady=4, sticky="w")
                ctk.CTkLabel(livef, text=f"{share * 100:.1f}%", font=font(12), text_color=COLORS["text"], anchor="w").grid(
                    row=i, column=2, padx=8, pady=4, sticky="w")
                ctk.CTkLabel(livef, text=str(lv.worker_count), font=font(12), text_color=COLORS["text"], anchor="w").grid(
                    row=i, column=3, padx=8, pady=4, sticky="w")
        else:
            ctk.CTkLabel(self.body, text=t("pool.live_none"), font=font(12), text_color=COLORS["muted"], anchor="w").grid(
                row=row, column=0, sticky="w")
            row += 1

        SectionTitle(self.body, text=t("pool.expected")).grid(row=row, column=0, pady=(18, 4), sticky="w")
        row += 1
        if reco["expected_gross"] is not None:
            ctk.CTkLabel(self.body, text=t("pool.before_fees", v=format_btcz(reco["expected_gross"], 2)),
                         font=font(20, "bold"), text_color=COLORS["accent"], anchor="w").grid(row=row, column=0, sticky="w")
            row += 1
            ctk.CTkLabel(self.body, text=t("pool.your_hashrate", h=format_hashrate(reco["hashrate_solps"])),
                         font=font(11), text_color=COLORS["muted"], anchor="w").grid(row=row, column=0, sticky="w")
        else:
            ctk.CTkLabel(self.body, text=t("pool.set_hashrate"), font=font(12), text_color=COLORS["warn"], anchor="w").grid(
                row=row, column=0, sticky="w")
        row += 1

        SectionTitle(self.body, text=t("pool.known")).grid(row=row, column=0, pady=(18, 4), sticky="w")
        row += 1
        known = ctk.CTkFrame(self.body, fg_color="transparent")
        known.grid(row=row, column=0, sticky="ew")
        row += 1
        self._header_row(known, [("pool.col_pool", 3), ("pool.col_fee", 1), ("pool.col_scheme", 2),
                                 ("pool.col_minpay", 1), ("pool.col_status", 1), ("pool.col_net", 2)])
        for i, r in enumerate(reco["rows"], start=1):
            medal = MEDALS[i - 1] if r["active"] and (i - 1) < len(MEDALS) and (i - 1) < reco["active_count"] else ""
            label = f"{medal}  {r['name']}" if medal else r["name"]
            ctk.CTkLabel(known, text=label, font=font(13), text_color=COLORS["text"], anchor="w").grid(
                row=i, column=0, padx=8, pady=4, sticky="w")
            fee_txt = f"{r['fee']:.2f} %" if r["fee"] is not None else t("pool.unknown")
            ctk.CTkLabel(known, text=fee_txt, font=font(12), text_color=COLORS["muted"], anchor="w").grid(
                row=i, column=1, padx=8, pady=4, sticky="w")
            ctk.CTkLabel(known, text=r["scheme"] or t("pool.unknown"), font=font(12), text_color=COLORS["muted"], anchor="w").grid(
                row=i, column=2, padx=8, pady=4, sticky="w")
            minpay_txt = f"{r['min_pay']:g}" if r["min_pay"] is not None else t("pool.unknown")
            ctk.CTkLabel(known, text=minpay_txt, font=font(12), text_color=COLORS["muted"], anchor="w").grid(
                row=i, column=3, padx=8, pady=4, sticky="w")
            status_txt = t("pool.active") if r["active"] else t("pool.quiet")
            status_color = COLORS["ok"] if r["active"] else COLORS["muted"]
            ctk.CTkLabel(known, text=status_txt, font=font(12, "bold"), text_color=status_color, anchor="w").grid(
                row=i, column=4, padx=8, pady=4, sticky="w")
            if r["net"] is not None:
                net_txt = f"{format_btcz(r['net'], 2)} BTCZ"
                net_color = COLORS["accent"] if r["active"] else COLORS["muted"]
            else:
                net_txt = t("pool.unknown")
                net_color = COLORS["muted"]
            ctk.CTkLabel(known, text=net_txt, font=font(12, "bold"), text_color=net_color, anchor="w").grid(
                row=i, column=5, padx=8, pady=4, sticky="w")

        ctk.CTkLabel(self.body, text=t("pool.note"), font=font(11), text_color=COLORS["muted"],
                     wraplength=760, justify="left", anchor="w").grid(row=row, column=0, sticky="w", pady=(14, 6))
