import threading
from datetime import datetime, timezone

import customtkinter as ctk

from app.core import settings
from app.core.currency import currency
from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.format import SOL_UNITS, format_btcz, format_hashrate
from app.utils.mining_calc import profitability
from modules.base_module import BaseModule
from modules.mining_tracker.tracker import load_addresses

SHORTCUTS = [("tracker", "⛏️", "nav.tracker"), ("profitability", "💰", "nav.profitability"),
             ("pools", "🌊", "nav.pools"), ("network", "🌐", "nav.network")]


class DashboardModule(BaseModule):
    key = "dashboard"
    name_key = "nav.dashboard"
    icon = "📊"

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(18, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="BTCZ Tools", font=font(26, "bold")).grid(row=0, column=0, sticky="w")
        self.refresh_btn = ctk.CTkButton(header, text=t("common.refresh"), width=110, command=self.refresh)
        self.refresh_btn.grid(row=0, column=1, sticky="e")

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, padx=20, pady=(6, 6), sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self.sections = {}
        self.cards = {}
        self._section("sec.network", ["c.block_height", "c.difficulty", "c.net_hashrate", "c.block_reward"], 0)
        self._section("sec.your_mining", ["dash.today", "dash.d7", "dash.d30"], 2)
        self.mining_hint = ctk.CTkLabel(self.body, text="", font=font(11), text_color=COLORS["warn"], anchor="w")
        self.mining_hint.grid(row=4, column=0, padx=4, sticky="w")
        self._section("prof.results", ["prof.revenue", "prof.electricity", "prof.profit"], 5)
        self.profit_hint = ctk.CTkLabel(self.body, text="", font=font(11), text_color=COLORS["warn"], anchor="w")
        self.profit_hint.grid(row=7, column=0, padx=4, sticky="w")
        self._section("sec.market", ["c.price_eur", "c.price_usd", "c.change_24h", "c.market_cap"], 8)

        self.sec_quick = SectionTitle(self.body, text=t("sec.quick"))
        self.sec_quick.grid(row=10, column=0, padx=4, pady=(18, 6), sticky="w")
        quick = ctk.CTkFrame(self.body, fg_color="transparent")
        quick.grid(row=11, column=0, sticky="ew")
        self.shortcut_btns = {}
        for i, (key, icon, name_key) in enumerate(SHORTCUTS):
            quick.grid_columnconfigure(i, weight=1, uniform="q")
            btn = ctk.CTkButton(quick, text=f"{icon}  {t(name_key)}", height=46, fg_color=COLORS["card"],
                                hover_color=COLORS["card_hover"], command=lambda k=key: self._go(k))
            btn.grid(row=0, column=i, padx=6, pady=6, sticky="ew")
            self.shortcut_btns[name_key] = (btn, icon)

        self.status = ctk.CTkLabel(self, text="", font=font(11), text_color=COLORS["muted"], anchor="w")
        self.status.grid(row=2, column=0, padx=26, pady=(4, 12), sticky="ew")

    def _section(self, title_key, card_keys, row):
        self.sections[title_key] = SectionTitle(self.body, text=t(title_key))
        self.sections[title_key].grid(row=row, column=0, padx=4, pady=(14, 6), sticky="w")
        frame = ctk.CTkFrame(self.body, fg_color="transparent")
        frame.grid(row=row + 1, column=0, sticky="ew")
        for i, key in enumerate(card_keys):
            frame.grid_columnconfigure(i, weight=1, uniform=title_key)
            card = StatCard(frame, t(key))
            card.grid(row=0, column=i, padx=6, pady=6, sticky="ew")
            self.cards[key] = card

    def _go(self, key):
        if callable(self.navigate):
            self.navigate(key)

    def retranslate(self):
        if not self.built:
            return
        self.refresh_btn.configure(text=t("common.refresh"))
        for key, lbl in self.sections.items():
            lbl.configure(text=t(key))
        for key, card in self.cards.items():
            card.set_title(t(key))
        self.sec_quick.configure(text=t("sec.quick"))
        for name_key, (btn, icon) in self.shortcut_btns.items():
            btn.configure(text=f"{icon}  {t(name_key)}")
        self.refresh()

    def refresh(self):
        self.status.configure(text=t("st.loading"))
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        net = None
        try:
            net = self.datalayer.get_network_stats()
            self.cards["c.block_height"].update_value(f"{net.height:,}")
            self.cards["c.difficulty"].update_value(f"{net.difficulty:,.2f}")
            self.cards["c.net_hashrate"].update_value(format_hashrate(net.network_hashps()), subtitle=t("sub.hashrate_est"))
            self.cards["c.block_reward"].update_value(
                f"{format_btcz(net.block_reward, 0)} BTCZ",
                subtitle=t("sub.to_miner", v=format_btcz(net.miner_reward, 0)), accent=COLORS["accent"])
        except Exception as exc:
            self.status.configure(text=t("st.net_unavailable", e=exc))

        market = None
        try:
            market = self.datalayer.get_market()
            self.cards["c.price_eur"].update_value(format_btcz(market.price_eur, 8))
            self.cards["c.price_usd"].update_value(format_btcz(market.price_usd, 8))
            color = COLORS["ok"] if market.change_24h >= 0 else COLORS["err"]
            arrow = "+" if market.change_24h >= 0 else ""
            self.cards["c.change_24h"].update_value(f"{arrow}{market.change_24h:.2f} %", accent=color)
            self.cards["c.market_cap"].update_value(
                f"{format_btcz(currency.value(market.market_cap_eur, market.market_cap_usd), 0)} {currency.symbol()}")
            self.status.configure(text=t("st.sources", s=net.source if net else "btcz.rocks"))
        except Exception as exc:
            self.status.configure(text=t("st.price_unavailable", e=exc))

        self._load_mining()
        self._load_profit(net, market)

    def _load_mining(self):
        addresses = load_addresses()
        if not addresses:
            self.mining_hint.configure(text=t("dash.set_address"))
            for key in ["dash.today", "dash.d7", "dash.d30"]:
                self.cards[key].update_value("--", subtitle="")
            return
        self.mining_hint.configure(text="")
        try:
            txs = self.datalayer.get_address_transactions(addresses[0], False)
        except Exception:
            return
        now = datetime.now(timezone.utc).timestamp()
        for key, days in [("dash.today", 1), ("dash.d7", 7), ("dash.d30", 30)]:
            cutoff = now - days * 86400
            total = sum(tx.value for tx in txs if tx.is_mining and tx.time >= cutoff)
            self.cards[key].update_value(f"{format_btcz(total, 2)}", subtitle="BTCZ", accent=COLORS["accent"])

    def _load_profit(self, net, market):
        saved = settings.get("profitability", {}) or {}
        try:
            hashrate = float(str(saved.get("hashrate", "")).replace(",", ".") or 0)
        except ValueError:
            hashrate = 0.0
        if hashrate <= 0 or net is None or market is None:
            self.profit_hint.configure(text=t("dash.set_profit"))
            for key in ["prof.revenue", "prof.electricity", "prof.profit"]:
                self.cards[key].update_value("--", subtitle="")
            return
        self.profit_hint.configure(text="")

        def num(k, d=0.0):
            try:
                return float(str(saved.get(k, "")).replace(",", ".") or d)
            except ValueError:
                return d

        hashrate_solps = hashrate * SOL_UNITS.get(saved.get("unit", "KSol/s"), 1)
        price = currency.value(market.price_eur, market.price_usd)
        unit_txt = f"{currency.symbol()}/day"
        res = profitability(hashrate_solps, num("power"), num("elec"), num("pool_fee"),
                            price, net.network_hashps(), net.block_time, net.miner_reward)
        self.cards["prof.revenue"].update_value(f"{res['revenue']:.4f}", subtitle=unit_txt)
        self.cards["prof.electricity"].update_value(f"-{res['electricity']:.4f}", subtitle=unit_txt, accent=COLORS["err"])
        color = COLORS["ok"] if res["profit"] >= 0 else COLORS["err"]
        sign = "+" if res["profit"] >= 0 else ""
        self.cards["prof.profit"].update_value(f"{sign}{res['profit']:.4f}", subtitle=unit_txt, accent=color)
