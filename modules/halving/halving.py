import threading
from datetime import datetime, timedelta

import customtkinter as ctk

from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.format import block_reward, format_btcz
from config.config import BLOCK_TIME_TARGET, HALVING_INTERVAL, MINER_REWARD_RATIO
from modules.base_module import BaseModule

UNITS = [("halving.days", 86400), ("halving.hours", 3600), ("halving.minutes", 60), ("halving.seconds", 1)]


class HalvingModule(BaseModule):
    key = "halving"
    name_key = "nav.halving"
    icon = "⏳"

    def build(self):
        self._eta = None
        self.height = 0
        self.target = 0
        self.remaining = 0
        self.loading = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.title_lbl = ctk.CTkLabel(header, text=t("halving.title"), font=font(24, "bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w")
        self.refresh_btn = ctk.CTkButton(header, text=t("common.refresh"), width=110, command=self.refresh)
        self.refresh_btn.grid(row=0, column=1, sticky="e")

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.grid(row=1, column=0, padx=24, pady=(6, 6), sticky="new")
        self.body.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(self.body, fg_color=COLORS["card"], corner_radius=18)
        hero.grid(row=0, column=0, sticky="ew")
        hero.grid_columnconfigure(0, weight=1)

        counts = ctk.CTkFrame(hero, fg_color="transparent")
        counts.grid(row=0, column=0, pady=(26, 6))
        self.count_lbls = {}
        for i, (key, _sec) in enumerate(UNITS):
            cell = ctk.CTkFrame(counts, fg_color="transparent")
            cell.grid(row=0, column=i * 2, padx=10)
            num = ctk.CTkLabel(cell, text="--", font=font(54, "bold"), text_color=COLORS["accent"])
            num.pack()
            unit = ctk.CTkLabel(cell, text=t(key), font=font(12, "bold"), text_color=COLORS["muted"])
            unit.pack()
            self.count_lbls[key] = (num, unit)
            if i < len(UNITS) - 1:
                sep = ctk.CTkLabel(counts, text=":", font=font(46, "bold"), text_color=COLORS["scroll"])
                sep.grid(row=0, column=i * 2 + 1)

        self.until_lbl = ctk.CTkLabel(hero, text=t("halving.until"), font=font(15),
                                      text_color=COLORS["text"])
        self.until_lbl.grid(row=1, column=0, pady=(0, 4))
        self.eta_lbl = ctk.CTkLabel(hero, text="", font=font(13), text_color=COLORS["mine"])
        self.eta_lbl.grid(row=2, column=0)
        self.note_lbl = ctk.CTkLabel(hero, text=t("halving.eta_note"), font=font(11),
                                     text_color=COLORS["muted"])
        self.note_lbl.grid(row=3, column=0, pady=(2, 6))

        self.progress = ctk.CTkProgressBar(hero, height=14, progress_color=COLORS["accent"])
        self.progress.set(0)
        self.progress.grid(row=4, column=0, padx=40, pady=(6, 4), sticky="ew")
        self.progress_lbl = ctk.CTkLabel(hero, text="", font=font(12), text_color=COLORS["muted"])
        self.progress_lbl.grid(row=5, column=0, pady=(0, 22))

        reward = ctk.CTkFrame(self.body, fg_color=COLORS["card"], corner_radius=16)
        reward.grid(row=1, column=0, sticky="ew", pady=(14, 0))
        reward.grid_columnconfigure((0, 2), weight=1)
        self.reward_now_lbl = ctk.CTkLabel(reward, text=t("halving.reward_now"), font=font(12, "bold"),
                                           text_color=COLORS["muted"])
        self.reward_now_lbl.grid(row=0, column=0, padx=20, pady=(18, 2))
        self.reward_now_val = ctk.CTkLabel(reward, text="--", font=font(30, "bold"), text_color=COLORS["accent"])
        self.reward_now_val.grid(row=1, column=0, padx=20)
        self.reward_now_sub = ctk.CTkLabel(reward, text="", font=font(11), text_color=COLORS["muted"])
        self.reward_now_sub.grid(row=2, column=0, padx=20, pady=(0, 18))
        ctk.CTkLabel(reward, text="→", font=font(34, "bold"), text_color=COLORS["title"]).grid(row=1, column=1)
        self.reward_after_lbl = ctk.CTkLabel(reward, text=t("halving.reward_after"), font=font(12, "bold"),
                                             text_color=COLORS["muted"])
        self.reward_after_lbl.grid(row=0, column=2, padx=20, pady=(18, 2))
        self.reward_after_val = ctk.CTkLabel(reward, text="--", font=font(30, "bold"), text_color=COLORS["mine"])
        self.reward_after_val.grid(row=1, column=2, padx=20)
        self.reward_after_sub = ctk.CTkLabel(reward, text="", font=font(11), text_color=COLORS["muted"])
        self.reward_after_sub.grid(row=2, column=2, padx=20, pady=(0, 18))

        stats = ctk.CTkFrame(self.body, fg_color="transparent")
        stats.grid(row=2, column=0, sticky="ew", pady=(14, 0))
        for i in range(3):
            stats.grid_columnconfigure(i, weight=1, uniform="hv")
        self.card_current = StatCard(stats, t("halving.current_block"))
        self.card_current.grid(row=0, column=0, padx=6, sticky="ew")
        self.card_target = StatCard(stats, t("halving.target_block"))
        self.card_target.grid(row=0, column=1, padx=6, sticky="ew")
        self.card_left = StatCard(stats, t("halving.blocks_left"))
        self.card_left.grid(row=0, column=2, padx=6, sticky="ew")

        self.status = ctk.CTkLabel(self, text="", font=font(11), text_color=COLORS["muted"], anchor="w")
        self.status.grid(row=3, column=0, padx=26, pady=(0, 12), sticky="ew")

        self._tick()

    def retranslate(self):
        if not self.built:
            return
        self.title_lbl.configure(text=t("halving.title"))
        self.refresh_btn.configure(text=t("common.refresh"))
        self.until_lbl.configure(text=t("halving.until"))
        self.note_lbl.configure(text=t("halving.eta_note"))
        for key, (num, unit) in self.count_lbls.items():
            unit.configure(text=t(key))
        self.reward_now_lbl.configure(text=t("halving.reward_now"))
        self.reward_after_lbl.configure(text=t("halving.reward_after"))
        self.card_current.set_title(t("halving.current_block"))
        self.card_target.set_title(t("halving.target_block"))
        self.card_left.set_title(t("halving.blocks_left"))
        self.refresh()

    def refresh(self):
        if self.loading:
            return
        self.status.configure(text=t("halving.loading"))
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self):
        self.loading = True
        try:
            net = self.datalayer.get_network_stats()
            height = int(net.height or 0)
            if height <= 0:
                self.status.configure(text=t("halving.unavailable", e="height=0"))
                return
            era = height // HALVING_INTERVAL
            target = (era + 1) * HALVING_INTERVAL
            remaining = target - height
            self.height = height
            self.target = target
            self.remaining = remaining
            self._eta = datetime.now() + timedelta(seconds=remaining * BLOCK_TIME_TARGET)
            self._render(era)
            self.status.configure(text="")
        except Exception as exc:
            self.status.configure(text=t("halving.unavailable", e=exc))
        finally:
            self.loading = False

    def _render(self, era):
        done = self.height - era * HALVING_INTERVAL
        pct = done / HALVING_INTERVAL * 100
        self.progress.set(done / HALVING_INTERVAL)
        self.progress_lbl.configure(text=t("halving.progress", pct=f"{pct:.1f}",
                                           done=f"{done:,}", total=f"{HALVING_INTERVAL:,}"))
        self.eta_lbl.configure(text=t("halving.eta", date=self._eta.strftime("%d/%m/%Y")))

        reward_now = block_reward(self.height)
        reward_after = block_reward(self.target)
        self.reward_now_val.configure(text=f"{format_btcz(reward_now, 1)}")
        self.reward_now_sub.configure(text=t("halving.miner_share", v=format_btcz(reward_now * MINER_REWARD_RATIO, 0)))
        self.reward_after_val.configure(text=f"{format_btcz(reward_after, 1)}")
        self.reward_after_sub.configure(text=t("halving.miner_share", v=format_btcz(reward_after * MINER_REWARD_RATIO, 0)))

        self.card_current.update_value(f"{self.height:,}", accent=COLORS["text"])
        self.card_target.update_value(f"{self.target:,}", accent=COLORS["accent"])
        self.card_left.update_value(f"{self.remaining:,}", accent=COLORS["mine"])
        self._update_countdown()

    def _update_countdown(self):
        if not self._eta:
            return
        remaining = int((self._eta - datetime.now()).total_seconds())
        if remaining < 0:
            remaining = 0
        for key, sec in UNITS:
            value = remaining // sec
            remaining -= value * sec
            num, _unit = self.count_lbls[key]
            num.configure(text=f"{value:02d}" if key != "halving.days" else f"{value:,}")

    def _tick(self):
        try:
            self._update_countdown()
        finally:
            self.after(1000, self._tick)
