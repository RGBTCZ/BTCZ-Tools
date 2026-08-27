import threading

import customtkinter as ctk

from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.format import format_btcz, format_fiat, format_hashrate
from modules.base_module import BaseModule


class DashboardModule(BaseModule):
    key = "dashboard"
    name_key = "nav.dashboard"
    icon = "📊"

    def build(self):
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="BTCZ Tools", font=font(26, "bold")).grid(row=0, column=0, sticky="w")
        self.refresh_btn = ctk.CTkButton(
            header, text=t("common.refresh"), width=110, command=self.refresh
        )
        self.refresh_btn.grid(row=0, column=1, sticky="e")

        self.sec_net = SectionTitle(self, text=t("sec.network"))
        self.sec_net.grid(row=1, column=0, padx=24, pady=(16, 6), sticky="w")
        net = ctk.CTkFrame(self, fg_color="transparent")
        net.grid(row=2, column=0, padx=24, sticky="ew")
        for i in range(4):
            net.grid_columnconfigure(i, weight=1, uniform="net")
        self.cards = {
            "c.block_height": StatCard(net, t("c.block_height")),
            "c.difficulty": StatCard(net, t("c.difficulty")),
            "c.net_hashrate": StatCard(net, t("c.net_hashrate")),
            "c.block_reward": StatCard(net, t("c.block_reward")),
        }
        for i, key in enumerate(["c.block_height", "c.difficulty", "c.net_hashrate", "c.block_reward"]):
            self.cards[key].grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        self.sec_market = SectionTitle(self, text=t("sec.market"))
        self.sec_market.grid(row=3, column=0, padx=24, pady=(16, 6), sticky="w")
        market = ctk.CTkFrame(self, fg_color="transparent")
        market.grid(row=4, column=0, padx=24, sticky="ew")
        for i in range(4):
            market.grid_columnconfigure(i, weight=1, uniform="mk")
        for key in ["c.price_eur", "c.price_usd", "c.change_24h", "c.market_cap"]:
            self.cards[key] = StatCard(market, t(key))
        for i, key in enumerate(["c.price_eur", "c.price_usd", "c.change_24h", "c.market_cap"]):
            self.cards[key].grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        self.status = ctk.CTkLabel(self, text="", font=font(11), text_color=COLORS["muted"], anchor="w")
        self.status.grid(row=5, column=0, padx=26, pady=(18, 12), sticky="ew")

    def retranslate(self):
        if not self.built:
            return
        self.refresh_btn.configure(text=t("common.refresh"))
        self.sec_net.configure(text=t("sec.network"))
        self.sec_market.configure(text=t("sec.market"))
        for key, card in self.cards.items():
            card.set_title(t(key))
        self.refresh()

    def refresh(self):
        self.status.configure(text=t("st.loading"))
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        source = ""
        try:
            net = self.datalayer.get_network_stats()
            source = net.source
            self.cards["c.block_height"].update_value(f"{net.height:,}")
            self.cards["c.difficulty"].update_value(f"{net.difficulty:,.2f}")
            self.cards["c.net_hashrate"].update_value(
                format_hashrate(net.network_hashps()), subtitle=t("sub.hashrate_est")
            )
            self.cards["c.block_reward"].update_value(
                f"{format_btcz(net.block_reward, 0)} BTCZ",
                subtitle=t("sub.to_miner", v=format_btcz(net.miner_reward, 0)),
                accent=COLORS["accent"],
            )
        except Exception as exc:
            self.status.configure(text=t("st.net_unavailable", e=exc))

        try:
            mk = self.datalayer.get_market()
            self.cards["c.price_eur"].update_value(format_fiat(mk.price_eur, "EUR", 8))
            self.cards["c.price_usd"].update_value(format_fiat(mk.price_usd, "USD", 8))
            color = COLORS["ok"] if mk.change_24h >= 0 else COLORS["err"]
            arrow = "+" if mk.change_24h >= 0 else ""
            self.cards["c.change_24h"].update_value(f"{arrow}{mk.change_24h:.2f} %", accent=color)
            self.cards["c.market_cap"].update_value(format_fiat(mk.market_cap_eur, "EUR", 0))
            self.status.configure(text=t("st.sources", s=source or "btcz.rocks"))
        except Exception as exc:
            self.status.configure(text=t("st.price_unavailable", e=exc))
