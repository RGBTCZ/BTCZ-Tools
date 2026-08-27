import threading

import customtkinter as ctk

from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.format import format_btcz, format_hashrate, human_age, short_hash
from modules.base_module import BaseModule

COLUMNS = [("col.height", 1), ("col.age", 1), ("col.tx", 1), ("col.mined_by", 3), ("col.reward", 1)]


class NetworkExplorerModule(BaseModule):
    key = "network"
    name_key = "nav.network"
    icon = "🌐"

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.title_lbl = ctk.CTkLabel(header, text=t("title.network"), font=font(24, "bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w")
        self.refresh_btn = ctk.CTkButton(
            header, text=t("common.refresh"), width=110, command=self.refresh
        )
        self.refresh_btn.grid(row=0, column=1, sticky="e")

        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=1, column=0, padx=24, pady=(12, 6), sticky="ew")
        for i in range(4):
            stats.grid_columnconfigure(i, weight=1, uniform="ns")
        self.cards = {
            "c.block_height": StatCard(stats, t("c.block_height")),
            "c.difficulty": StatCard(stats, t("c.difficulty")),
            "c.net_hashrate": StatCard(stats, t("c.net_hashrate")),
            "c.connections": StatCard(stats, t("c.connections")),
        }
        for i, key in enumerate(["c.block_height", "c.difficulty", "c.net_hashrate", "c.connections"]):
            self.cards[key].grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        self.sec_blocks = SectionTitle(self, text=t("sec.latest_blocks"))
        self.sec_blocks.grid(row=2, column=0, padx=24, pady=(16, 4), sticky="w")

        head = ctk.CTkFrame(self, fg_color=COLORS["sidebar"], corner_radius=8)
        head.grid(row=3, column=0, padx=24, sticky="ew")
        self.col_labels = []
        for i, (key, weight) in enumerate(COLUMNS):
            head.grid_columnconfigure(i, weight=weight)
            lbl = ctk.CTkLabel(head, text=t(key), font=font(11, "bold"), text_color=COLORS["muted"])
            lbl.grid(row=0, column=i, padx=12, pady=8, sticky="w")
            self.col_labels.append((key, lbl))

        self.rows = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.rows.grid(row=4, column=0, padx=24, pady=(0, 8), sticky="nsew")
        for i, (key, weight) in enumerate(COLUMNS):
            self.rows.grid_columnconfigure(i, weight=weight)

        self.status = ctk.CTkLabel(self, text="", font=font(11), text_color=COLORS["muted"], anchor="w")
        self.status.grid(row=5, column=0, padx=26, pady=(0, 12), sticky="ew")

    def retranslate(self):
        if not self.built:
            return
        self.title_lbl.configure(text=t("title.network"))
        self.refresh_btn.configure(text=t("common.refresh"))
        self.sec_blocks.configure(text=t("sec.latest_blocks"))
        for key, card in self.cards.items():
            card.set_title(t(key))
        for key, lbl in self.col_labels:
            lbl.configure(text=t(key))
        self.refresh()

    def refresh(self):
        self.status.configure(text=t("st.loading_net"))
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        try:
            net = self.datalayer.get_network_stats()
            self.cards["c.block_height"].update_value(f"{net.height:,}")
            self.cards["c.difficulty"].update_value(f"{net.difficulty:,.2f}")
            self.cards["c.net_hashrate"].update_value(
                format_hashrate(net.computed_hashps), subtitle=t("sub.est")
            )
            self.cards["c.connections"].update_value(str(net.connections))
        except Exception as exc:
            self.status.configure(text=t("st.net_unavailable", e=exc))
            return

        try:
            blocks = self.datalayer.get_latest_blocks(15)
            self._render_blocks(blocks)
            self.status.configure(text=t("st.blocks_count", n=len(blocks), s=net.source))
        except Exception as exc:
            self.status.configure(text=t("st.blocks_unavailable", e=exc))

    def _render_blocks(self, blocks):
        for widget in self.rows.winfo_children():
            widget.destroy()
        for r, block in enumerate(blocks):
            miner = block.mined_by or "-"
            if miner.startswith("t1") or miner.startswith("t3"):
                miner = short_hash(miner, 8)
            values = [
                (f"{block.height:,}", COLORS["accent"]),
                (human_age(block.time), COLORS["muted"]),
                (str(block.tx_count), COLORS["text"]),
                (miner, COLORS["info"]),
                (f"{format_btcz(block.reward, 0)}", COLORS["mine"]),
            ]
            for c, (text, color) in enumerate(values):
                ctk.CTkLabel(self.rows, text=text, font=font(12), text_color=color, anchor="w").grid(
                    row=r, column=c, padx=12, pady=4, sticky="w"
                )
