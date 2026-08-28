import threading

import customtkinter as ctk

from app.core import settings
from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.format import SOL_UNITS, format_btcz, format_fiat, format_hashrate
from app.utils.mining_calc import breakeven_price, price_scenarios, profitability, roi_days
from config.gpu_presets import GPU_PRESETS
from modules.base_module import BaseModule

MULTIPLIERS = [0.5, 1, 2, 5, 10]
DEFAULTS = {
    "hashrate": "",
    "unit": "KSol/s",
    "power": "",
    "elec": "0.15",
    "pool_fee": "1",
    "hardware": "",
}


class ProfitabilityModule(BaseModule):
    key = "profitability"
    name_key = "nav.profitability"
    icon = "💰"

    def build(self):
        self.saved = {**DEFAULTS, **(settings.get("profitability", {}) or {})}
        self.net = None
        self.market = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title_lbl = ctk.CTkLabel(self, text=t("title.prof"), font=font(24, "bold"))
        self.title_lbl.grid(row=0, column=0, padx=24, pady=(20, 6), sticky="w")

        self.sec_net = SectionTitle(self, text=t("prof.network_data"))
        self.sec_net.grid(row=1, column=0, padx=24, pady=(6, 4), sticky="w")
        strip = ctk.CTkFrame(self, fg_color="transparent")
        strip.grid(row=2, column=0, padx=24, sticky="ew")
        for i in range(5):
            strip.grid_columnconfigure(i, weight=1, uniform="nd")
        self.nd = {
            "c.difficulty": StatCard(strip, t("c.difficulty")),
            "c.block_reward": StatCard(strip, t("c.block_reward")),
            "prof.block_time": StatCard(strip, t("prof.block_time")),
            "c.net_hashrate": StatCard(strip, t("c.net_hashrate")),
            "c.price_eur": StatCard(strip, t("c.price_eur")),
        }
        for i, key in enumerate(["c.difficulty", "c.block_reward", "prof.block_time", "c.net_hashrate", "c.price_eur"]):
            self.nd[key].grid(row=0, column=i, padx=5, pady=6, sticky="ew")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=3, column=0, padx=24, pady=(10, 8), sticky="nsew")
        content.grid_columnconfigure(0, weight=1, uniform="c")
        content.grid_columnconfigure(1, weight=1, uniform="c")
        content.grid_rowconfigure(0, weight=1)

        self._build_inputs(content)
        self._build_results(content)

    def _build_inputs(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color=COLORS["card"])
        card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        self.lbl_setup = SectionTitle(card, text=t("prof.setup"))
        self.lbl_setup.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="w")

        self.lbl_gpu = ctk.CTkLabel(card, text=t("prof.gpu_preset"), anchor="w")
        self.lbl_gpu.grid(row=1, column=0, padx=16, pady=(6, 0), sticky="w")
        self.gpu_menu = ctk.CTkOptionMenu(
            card, values=self._gpu_values(), command=self._on_gpu_select,
            fg_color=COLORS["sidebar"], button_color=COLORS["accent_dark"],
            button_hover_color=COLORS["accent"],
        )
        self.gpu_menu.set(t("prof.gpu_custom"))
        self.gpu_menu.grid(row=2, column=0, padx=16, pady=(0, 6), sticky="ew")

        self.lbl_hashrate = ctk.CTkLabel(card, text=t("prof.hashrate"), anchor="w")
        self.lbl_hashrate.grid(row=3, column=0, padx=16, pady=(6, 0), sticky="w")
        hr = ctk.CTkFrame(card, fg_color="transparent")
        hr.grid(row=4, column=0, padx=16, pady=(0, 6), sticky="ew")
        hr.grid_columnconfigure(0, weight=1)
        self.in_hashrate = ctk.CTkEntry(hr, height=34)
        self.in_hashrate.insert(0, self.saved["hashrate"])
        self.in_hashrate.grid(row=0, column=0, sticky="ew")
        self.unit_menu = ctk.CTkOptionMenu(
            hr, values=list(SOL_UNITS.keys()), width=110,
            fg_color=COLORS["sidebar"], button_color=COLORS["accent_dark"],
            button_hover_color=COLORS["accent"],
        )
        self.unit_menu.set(self.saved["unit"] if self.saved["unit"] in SOL_UNITS else "KSol/s")
        self.unit_menu.grid(row=0, column=1, padx=(8, 0))

        self.lbl_power = ctk.CTkLabel(card, text=t("prof.power"), anchor="w")
        self.lbl_power.grid(row=5, column=0, padx=16, pady=(6, 0), sticky="w")
        self.in_power = ctk.CTkEntry(card, height=34)
        self.in_power.insert(0, self.saved["power"])
        self.in_power.grid(row=6, column=0, padx=16, pady=(0, 6), sticky="ew")

        self.lbl_elec = ctk.CTkLabel(card, text=t("prof.elec"), anchor="w")
        self.lbl_elec.grid(row=7, column=0, padx=16, pady=(6, 0), sticky="w")
        self.in_elec = ctk.CTkEntry(card, height=34)
        self.in_elec.insert(0, self.saved["elec"])
        self.in_elec.grid(row=8, column=0, padx=16, pady=(0, 6), sticky="ew")

        self.lbl_fee = ctk.CTkLabel(card, text=t("prof.pool_fee"), anchor="w")
        self.lbl_fee.grid(row=9, column=0, padx=16, pady=(6, 0), sticky="w")
        self.in_fee = ctk.CTkEntry(card, height=34)
        self.in_fee.insert(0, self.saved["pool_fee"])
        self.in_fee.grid(row=10, column=0, padx=16, pady=(0, 6), sticky="ew")

        self.lbl_hw = ctk.CTkLabel(card, text=t("prof.hardware"), anchor="w")
        self.lbl_hw.grid(row=11, column=0, padx=16, pady=(6, 0), sticky="w")
        self.in_hw = ctk.CTkEntry(card, height=34)
        self.in_hw.insert(0, self.saved["hardware"])
        self.in_hw.grid(row=12, column=0, padx=16, pady=(0, 10), sticky="ew")

        self.calc_btn = ctk.CTkButton(card, text=t("prof.calculate"), height=40, command=self.calculate)
        self.calc_btn.grid(row=13, column=0, padx=16, pady=(4, 16), sticky="ew")

    def _gpu_values(self):
        return [t("prof.gpu_custom")] + [g["name"] for g in GPU_PRESETS]

    def _on_gpu_select(self, name):
        if name == t("prof.gpu_custom"):
            return
        for gpu in GPU_PRESETS:
            if gpu["name"] == name:
                self.unit_menu.set("Sol/s")
                self.in_hashrate.delete(0, "end")
                self.in_hashrate.insert(0, str(gpu["sols"]))
                self.in_power.delete(0, "end")
                self.in_power.insert(0, str(gpu["watts"]))
                break

    def _build_results(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color=COLORS["card"])
        card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        self.lbl_results = SectionTitle(card, text=t("prof.results"))
        self.lbl_results.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="w")

        self.head_coins = ctk.CTkLabel(card, text="--", font=font(30, "bold"), text_color=COLORS["accent"])
        self.head_coins.grid(row=1, column=0, padx=16, pady=(4, 0), sticky="w")
        self.head_unit = ctk.CTkLabel(card, text=t("prof.per_day"), font=font(12), text_color=COLORS["muted"])
        self.head_unit.grid(row=2, column=0, padx=16, pady=(0, 10), sticky="w")

        self.rows_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.rows_frame.grid(row=3, column=0, padx=16, pady=4, sticky="ew")
        self.rows_frame.grid_columnconfigure(0, weight=1)
        self.rows_frame.grid_columnconfigure(1, weight=0)

        self.res_labels = {}
        self._result_row(0, "prof.revenue", "revenue")
        self._result_row(1, "prof.electricity", "electricity")
        self._result_row(2, "prof.pool_fee_line", "fee")
        sep = ctk.CTkFrame(self.rows_frame, height=1, fg_color=COLORS["scroll"])
        sep.grid(row=3, column=0, columnspan=2, sticky="ew", pady=6)
        self._result_row(4, "prof.profit", "profit", big=True)

        self.extra = ctk.CTkFrame(card, fg_color="transparent")
        self.extra.grid(row=4, column=0, padx=16, pady=(10, 6), sticky="ew")
        self.extra.grid_columnconfigure(0, weight=1)
        self.lbl_be = ctk.CTkLabel(self.extra, text="", font=font(12), text_color=COLORS["info"], anchor="w")
        self.lbl_be.grid(row=0, column=0, sticky="w")
        self.lbl_roi = ctk.CTkLabel(self.extra, text="", font=font(12), text_color=COLORS["mine"], anchor="w")
        self.lbl_roi.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.sec_sc = SectionTitle(card, text=t("prof.scenarios"))
        self.sec_sc.grid(row=5, column=0, padx=16, pady=(12, 4), sticky="w")
        self.sc_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.sc_frame.grid(row=6, column=0, padx=16, pady=(0, 14), sticky="ew")
        self.sc_frame.grid_columnconfigure(0, weight=1)
        self.sc_frame.grid_columnconfigure(1, weight=1)

        self.status = ctk.CTkLabel(card, text=t("prof.fill"), font=font(11), text_color=COLORS["muted"])
        self.status.grid(row=7, column=0, padx=16, pady=(0, 14), sticky="w")

    def _result_row(self, row, key, name, big=False):
        lbl = ctk.CTkLabel(self.rows_frame, text=t(key), anchor="w",
                           font=font(14, "bold" if big else "normal"),
                           text_color=COLORS["text"] if big else COLORS["muted"])
        lbl.grid(row=row, column=0, sticky="w", pady=3)
        val = ctk.CTkLabel(self.rows_frame, text="--", anchor="e",
                          font=font(15, "bold" if big else "normal"), text_color=COLORS["text"])
        val.grid(row=row, column=1, sticky="e", pady=3)
        self.res_labels[name] = (lbl, key, val)

    def retranslate(self):
        if not self.built:
            return
        self.title_lbl.configure(text=t("title.prof"))
        self.sec_net.configure(text=t("prof.network_data"))
        self.lbl_setup.configure(text=t("prof.setup"))
        self.lbl_results.configure(text=t("prof.results"))
        self.lbl_gpu.configure(text=t("prof.gpu_preset"))
        current = self.gpu_menu.get()
        self.gpu_menu.configure(values=self._gpu_values())
        if current not in [g["name"] for g in GPU_PRESETS]:
            self.gpu_menu.set(t("prof.gpu_custom"))
        self.lbl_hashrate.configure(text=t("prof.hashrate"))
        self.lbl_power.configure(text=t("prof.power"))
        self.lbl_elec.configure(text=t("prof.elec"))
        self.lbl_fee.configure(text=t("prof.pool_fee"))
        self.lbl_hw.configure(text=t("prof.hardware"))
        self.calc_btn.configure(text=t("prof.calculate"))
        self.head_unit.configure(text=t("prof.per_day"))
        self.sec_sc.configure(text=t("prof.scenarios"))
        for key, card in self.nd.items():
            card.set_title(t(key))
        for name, (lbl, key, val) in self.res_labels.items():
            lbl.configure(text=t(key))

    def refresh(self):
        threading.Thread(target=self._load_network, daemon=True).start()

    def _load_network(self):
        try:
            self.net = self.datalayer.get_network_stats()
            self.nd["c.difficulty"].update_value(f"{self.net.difficulty:,.2f}")
            self.nd["c.block_reward"].update_value(f"{format_btcz(self.net.miner_reward, 0)} BTCZ")
            self.nd["prof.block_time"].update_value(f"{self.net.block_time} s")
            self.nd["c.net_hashrate"].update_value(format_hashrate(self.net.network_hashps()))
        except Exception:
            pass
        try:
            self.market = self.datalayer.get_market()
            self.nd["c.price_eur"].update_value(format_btcz(self.market.price_eur, 8))
        except Exception:
            pass

    def _parse(self, entry, default=0.0):
        raw = entry.get().strip().replace(",", ".")
        if raw == "":
            return default
        return float(raw)

    def calculate(self):
        self.status.configure(text="...")
        threading.Thread(target=self._calculate, daemon=True).start()

    def _calculate(self):
        try:
            hashrate = self._parse(self.in_hashrate)
            unit = self.unit_menu.get()
            power = self._parse(self.in_power)
            elec = self._parse(self.in_elec)
            fee = self._parse(self.in_fee)
            hardware = self._parse(self.in_hw)
        except ValueError:
            self.status.configure(text=t("prof.invalid"))
            return

        settings.set("profitability", {
            "hashrate": self.in_hashrate.get().strip(),
            "unit": unit,
            "power": self.in_power.get().strip(),
            "elec": self.in_elec.get().strip(),
            "pool_fee": self.in_fee.get().strip(),
            "hardware": self.in_hw.get().strip(),
        })

        if self.net is None:
            try:
                self.net = self.datalayer.get_network_stats()
            except Exception as exc:
                self.status.configure(text=t("st.net_unavailable", e=exc))
                return
        if self.market is None:
            try:
                self.market = self.datalayer.get_market()
            except Exception as exc:
                self.status.configure(text=t("st.price_unavailable", e=exc))
                return

        hashrate_solps = hashrate * SOL_UNITS.get(unit, 1)
        network_solps = self.net.network_hashps()
        price = self.market.price_eur

        res = profitability(
            hashrate_solps, power, elec, fee, price,
            network_solps, self.net.block_time, self.net.miner_reward,
        )
        self.head_coins.configure(text=f"≈ {format_btcz(res['coins'], 4)}")
        self.res_labels["revenue"][2].configure(
            text=f"+{format_fiat(res['revenue'], 'EUR', 4)}{t('prof.day_unit')}", text_color=COLORS["text"]
        )
        self.res_labels["electricity"][2].configure(
            text=f"-{format_fiat(res['electricity'], 'EUR', 4)}{t('prof.day_unit')}", text_color=COLORS["err"]
        )
        self.res_labels["fee"][2].configure(
            text=f"-{format_fiat(res['fee'], 'EUR', 4)}{t('prof.day_unit')}", text_color=COLORS["warn"]
        )
        profit_color = COLORS["ok"] if res["profit"] >= 0 else COLORS["err"]
        sign = "+" if res["profit"] >= 0 else ""
        self.res_labels["profit"][2].configure(
            text=f"{sign}{format_fiat(res['profit'], 'EUR', 4)}{t('prof.day_unit')}", text_color=profit_color
        )

        be = breakeven_price(res["coins"], power, elec, fee)
        self.lbl_be.configure(text=f"{t('prof.breakeven')}: {format_fiat(be, 'EUR', 10)}")

        days = roi_days(hardware, res["profit"])
        if hardware > 0:
            roi_text = t("prof.roi_days", d=f"{days:.0f}") if days else t("prof.roi_never")
            self.lbl_roi.configure(text=f"{t('prof.roi')}: {roi_text}")
        else:
            self.lbl_roi.configure(text="")

        self._render_scenarios(price, res["coins"], power, elec, fee)
        self.status.configure(text=t("st.sources", s=self.net.source))

    def _render_scenarios(self, price, coins, power, elec, fee):
        for widget in self.sc_frame.winfo_children():
            widget.destroy()
        scenarios = price_scenarios(price, coins, power, elec, fee, MULTIPLIERS)
        for r, sc in enumerate(scenarios):
            tag = f"  ({t('prof.current')})" if sc["mult"] == 1 else ""
            price_lbl = ctk.CTkLabel(
                self.sc_frame, text=f"{format_fiat(sc['price'], 'EUR', 10)}{tag}",
                font=font(12), text_color=COLORS["muted"], anchor="w",
            )
            price_lbl.grid(row=r, column=0, sticky="w", pady=2)
            color = COLORS["ok"] if sc["profit"] >= 0 else COLORS["err"]
            sign = "+" if sc["profit"] >= 0 else ""
            profit_lbl = ctk.CTkLabel(
                self.sc_frame, text=f"{sign}{format_fiat(sc['profit'], 'EUR', 4)}{t('prof.day_unit')}",
                font=font(12, "bold"), text_color=color, anchor="e",
            )
            profit_lbl.grid(row=r, column=1, sticky="e", pady=2)