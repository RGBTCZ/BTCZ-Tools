import threading
from tkinter import filedialog

import customtkinter as ctk

from app.core import settings
from app.core.currency import currency
from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import SectionTitle, StatCard
from app.utils.format import circulating_supply, format_btcz, format_fiat
from app.utils.share_card import generate_cards
from config.config import HOLDER_TIERS, MILESTONES_EUR, MOONSHOT_TARGETS_EUR
from modules.base_module import BaseModule

SETTINGS_KEY = "holder_addresses"


def load_holder_addresses():
    data = settings.get(SETTINGS_KEY, [])
    return data if isinstance(data, list) else []


def save_holder_addresses(addresses):
    unique = []
    for addr in addresses:
        addr = addr.strip()
        if addr and addr not in unique:
            unique.append(addr)
    settings.set(SETTINGS_KEY, unique)
    return unique


def tier_for(amount):
    current = HOLDER_TIERS[0]
    nxt = None
    for i, tier in enumerate(HOLDER_TIERS):
        if amount >= tier["min"]:
            current = tier
            nxt = HOLDER_TIERS[i + 1] if i + 1 < len(HOLDER_TIERS) else None
    return current, nxt


class HolderModule(BaseModule):
    key = "holder"
    name_key = "nav.holder"
    icon = "🐳"

    def build(self):
        self.total_btcz = 0.0
        self.price_eur = 0.0
        self.price_usd = 0.0
        self.ath_eur = 0.0
        self.ath_usd = 0.0
        self.supply = 0.0
        self.loading = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 4), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        self.title_lbl = ctk.CTkLabel(header, text=t("holder.title"), font=font(24, "bold"))
        self.title_lbl.grid(row=0, column=0, sticky="w")
        self.hide_switch = ctk.CTkSwitch(header, text=t("holder.hide_amounts"))
        self.hide_switch.grid(row=0, column=1, padx=(0, 12), sticky="e")
        self.share_btn = ctk.CTkButton(header, text=t("holder.share"), width=150,
                                       fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                                       command=self.share_card)
        self.share_btn.grid(row=0, column=2, padx=(0, 8), sticky="e")
        self.refresh_btn = ctk.CTkButton(header, text=t("common.refresh"), width=110, command=self.refresh)
        self.refresh_btn.grid(row=0, column=3, sticky="e")

        form = ctk.CTkFrame(self, corner_radius=16, fg_color=COLORS["card"])
        form.grid(row=1, column=0, padx=24, pady=(6, 4), sticky="ew")
        form.grid_columnconfigure(0, weight=1)
        self.lbl_addr = ctk.CTkLabel(form, text=t("holder.add_addr"), text_color=COLORS["muted"])
        self.lbl_addr.grid(row=0, column=0, columnspan=3, padx=14, pady=(12, 2), sticky="w")
        self.addr_box = ctk.CTkComboBox(form, values=load_holder_addresses() or [""], height=38)
        self.addr_box.set("")
        self.addr_box.grid(row=1, column=0, padx=(14, 8), pady=(2, 14), sticky="ew")
        self.addr_box.bind("<Return>", lambda _e: self.add_address())
        self.add_btn = ctk.CTkButton(form, text=t("holder.add"), width=110, height=38, command=self.add_address)
        self.add_btn.grid(row=1, column=1, padx=(0, 8), pady=(2, 14))
        self.remove_btn = ctk.CTkButton(form, text=t("b.remove"), width=110, height=38,
                                        fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
                                        command=self.remove_selected)
        self.remove_btn.grid(row=1, column=2, padx=(0, 14), pady=(2, 14))

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.grid(row=2, column=0, padx=20, pady=(6, 6), sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        self.status = ctk.CTkLabel(self, text="", font=font(11), text_color=COLORS["muted"], anchor="w")
        self.status.grid(row=3, column=0, padx=26, pady=(0, 12), sticky="ew")

    def retranslate(self):
        if not self.built:
            return
        self.title_lbl.configure(text=t("holder.title"))
        self.refresh_btn.configure(text=t("common.refresh"))
        self.hide_switch.configure(text=t("holder.hide_amounts"))
        self.share_btn.configure(text=t("holder.share"))
        self.lbl_addr.configure(text=t("holder.add_addr"))
        self.add_btn.configure(text=t("holder.add"))
        self.remove_btn.configure(text=t("b.remove"))
        self.refresh()

    def _refresh_box(self, selected=""):
        addresses = load_holder_addresses()
        self.addr_box.configure(values=addresses or [""])
        self.addr_box.set(selected)

    def add_address(self):
        addr = self.addr_box.get().strip()
        if not addr:
            return
        addresses = load_holder_addresses()
        addresses.append(addr)
        save_holder_addresses(addresses)
        self._refresh_box("")
        self.refresh()

    def remove_selected(self):
        addr = self.addr_box.get().strip()
        if not addr:
            return
        addresses = [a for a in load_holder_addresses() if a != addr]
        save_holder_addresses(addresses)
        self._refresh_box("")
        self.refresh()

    def refresh(self):
        if self.loading:
            return
        self.status.configure(text=t("holder.loading"))
        threading.Thread(target=self._load, daemon=True).start()

    def share_card(self):
        if not load_holder_addresses() or self.supply <= 0:
            self.status.configure(text=t("holder.no_addr"))
            return
        current, _ = tier_for(self.total_btcz)
        pct = self.total_btcz / self.supply * 100 if self.supply > 0 else 0.0
        one_in = int(self.supply / self.total_btcz) if self.total_btcz > 0 else 0
        data = {
            "emoji": current["emoji"],
            "tier": t(current["key"]),
            "stack": self.total_btcz,
            "value": self.total_btcz * currency.value(self.price_eur, self.price_usd),
            "sym": currency.symbol(),
            "supply_pct": pct,
            "one_in": one_in,
        }
        hide = bool(self.hide_switch.get())
        out_dir = filedialog.askdirectory()
        if not out_dir:
            return
        try:
            generate_cards(data, out_dir, hide)
            self.status.configure(text=t("holder.card_saved", p=out_dir))
        except Exception as exc:
            self.status.configure(text=t("holder.card_error", e=exc))

    def _clear(self):
        for widget in self.body.winfo_children():
            widget.destroy()

    def _load(self):
        self.loading = True
        try:
            addresses = load_holder_addresses()
            if not addresses:
                self._clear()
                ctk.CTkLabel(self.body, text=t("holder.no_addr"), font=font(13), text_color=COLORS["warn"],
                             anchor="w").grid(row=0, column=0, sticky="w", pady=12)
                self.status.configure(text="")
                return
            total = 0.0
            for addr in addresses:
                try:
                    stats = self.datalayer.get_address(addr)
                    total += stats.balance
                except Exception:
                    pass
            info = self.datalayer.get_coin_info()
            net = self.datalayer.get_network_stats()
            self.total_btcz = total
            self.price_eur = info.price_eur
            self.price_usd = info.price_usd
            self.ath_eur = info.ath_eur
            self.ath_usd = info.ath_usd
            self.supply = circulating_supply(net.height)
            self._render(addresses)
            self.status.configure(text="")
        except Exception as exc:
            self.status.configure(text=t("holder.unavailable", e=exc))
        finally:
            self.loading = False

    def _render(self, addresses):
        self._clear()
        self.addr_box.configure(values=addresses or [""])
        row = 0

        sym = currency.symbol()
        price = currency.value(self.price_eur, self.price_usd)
        value_fiat = self.total_btcz * price

        SectionTitle(self.body, text=t("sec.stack")).grid(row=row, column=0, pady=(16, 6), sticky="w")
        row += 1
        stack = ctk.CTkFrame(self.body, fg_color="transparent")
        stack.grid(row=row, column=0, sticky="ew")
        row += 1
        for i in range(2):
            stack.grid_columnconfigure(i, weight=1, uniform="stk")
        c_stack = StatCard(stack, "BTCZ")
        c_stack.update_value(format_btcz(self.total_btcz, 2), accent=COLORS["accent"])
        c_stack.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        c_val = StatCard(stack, t("holder.value"))
        c_val.update_value(format_fiat(value_fiat, sym), accent=COLORS["mine"])
        c_val.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        current, nxt = tier_for(self.total_btcz)
        SectionTitle(self.body, text=t("sec.rank")).grid(row=row, column=0, pady=(18, 6), sticky="w")
        row += 1
        rank = ctk.CTkFrame(self.body, fg_color=COLORS["card"], corner_radius=14)
        rank.grid(row=row, column=0, sticky="ew", pady=(0, 4))
        row += 1
        rank.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(rank, text=current["emoji"], font=font(46)).grid(
            row=0, column=0, rowspan=2, padx=(18, 14), pady=16)
        ctk.CTkLabel(rank, text=t(current["key"]), font=font(22, "bold"), text_color=COLORS["accent"],
                     anchor="w").grid(row=0, column=1, padx=(0, 16), pady=(16, 0), sticky="w")
        if nxt is not None:
            span = nxt["min"] - current["min"]
            progress = (self.total_btcz - current["min"]) / span if span > 0 else 0.0
            progress = max(0.0, min(1.0, progress))
            remaining = nxt["min"] - self.total_btcz
            bar = ctk.CTkProgressBar(rank, height=14, progress_color=COLORS["accent"])
            bar.set(progress)
            bar.grid(row=1, column=1, padx=(0, 18), pady=(6, 4), sticky="ew")
            ctk.CTkLabel(rank, text=t("holder.to_next", v=format_btcz(remaining, 0), tier=f"{nxt['emoji']} {t(nxt['key'])}"),
                         font=font(12), text_color=COLORS["muted"], anchor="w").grid(
                row=2, column=1, padx=(0, 18), pady=(0, 14), sticky="w")
        else:
            ctk.CTkLabel(rank, text=t("holder.max_rank"), font=font(13), text_color=COLORS["mine"],
                         anchor="w").grid(row=1, column=1, padx=(0, 18), pady=(0, 16), sticky="w")

        SectionTitle(self.body, text=t("sec.moonshot")).grid(row=row, column=0, pady=(18, 6), sticky="w")
        row += 1
        moon = ctk.CTkFrame(self.body, fg_color=COLORS["card"], corner_radius=14)
        moon.grid(row=row, column=0, sticky="ew")
        row += 1
        moon.grid_columnconfigure(0, weight=1)
        self.moon_price = ctk.CTkLabel(moon, text="", font=font(14, "bold"), text_color=COLORS["info"])
        self.moon_price.grid(row=0, column=0, padx=18, pady=(16, 2), sticky="w")
        self.moon_slider = ctk.CTkSlider(moon, from_=0, to=len(MOONSHOT_TARGETS_EUR) - 1,
                                         number_of_steps=len(MOONSHOT_TARGETS_EUR) - 1,
                                         command=self._on_moonshot)
        self.moon_slider.grid(row=1, column=0, padx=18, pady=(2, 6), sticky="ew")
        self.moon_stack_lbl = ctk.CTkLabel(moon, text=t("holder.stack_value"), font=font(11),
                                           text_color=COLORS["muted"], anchor="w")
        self.moon_stack_lbl.grid(row=2, column=0, padx=18, pady=(2, 0), sticky="w")
        self.moon_value = ctk.CTkLabel(moon, text="", font=font(26, "bold"), text_color=COLORS["accent"], anchor="w")
        self.moon_value.grid(row=3, column=0, padx=18, pady=(0, 2), sticky="w")
        self.moon_mult = ctk.CTkLabel(moon, text="", font=font(13), text_color=COLORS["mine"], anchor="w")
        self.moon_mult.grid(row=4, column=0, padx=18, pady=(0, 8), sticky="w")
        self.moon_ath = ctk.CTkLabel(moon, text="", font=font(12), text_color=COLORS["muted"], anchor="w")
        self.moon_ath.grid(row=5, column=0, padx=18, pady=(0, 16), sticky="w")
        default_idx = len(MOONSHOT_TARGETS_EUR) // 2
        self.moon_slider.set(default_idx)
        self._on_moonshot(default_idx)

        SectionTitle(self.body, text=t("sec.milestones")).grid(row=row, column=0, pady=(18, 6), sticky="w")
        row += 1
        miles = ctk.CTkFrame(self.body, fg_color="transparent")
        miles.grid(row=row, column=0, sticky="ew")
        row += 1
        for i in range(len(MILESTONES_EUR)):
            miles.grid_columnconfigure(i, weight=1, uniform="mile")
        for i, target in enumerate(MILESTONES_EUR):
            card = StatCard(miles, format_fiat(target, sym, 0))
            if value_fiat >= target:
                card.update_value(t("holder.reached"), accent=COLORS["ok"])
            elif self.total_btcz > 0:
                need = target / self.total_btcz
                card.update_value(t("holder.need_price", p=f"{need:.6f}", c=sym), accent=COLORS["mine"])
            else:
                card.update_value("--")
            card.grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        SectionTitle(self.body, text=t("sec.supply")).grid(row=row, column=0, pady=(18, 6), sticky="w")
        row += 1
        if self.supply > 0 and self.total_btcz > 0:
            pct = self.total_btcz / self.supply * 100
            one_in = int(self.supply / self.total_btcz) if self.total_btcz > 0 else 0
            ctk.CTkLabel(self.body, text=t("holder.supply_pct", pct=f"{pct:.6f}"), font=font(14, "bold"),
                         text_color=COLORS["accent"], anchor="w").grid(row=row, column=0, sticky="w")
            row += 1
            ctk.CTkLabel(self.body, text=t("holder.supply_one", n=f"{one_in:,}"), font=font(12),
                         text_color=COLORS["muted"], anchor="w").grid(row=row, column=0, sticky="w", pady=(0, 12))
            row += 1

    def _on_moonshot(self, value):
        idx = int(round(float(value)))
        idx = max(0, min(len(MOONSHOT_TARGETS_EUR) - 1, idx))
        target = MOONSHOT_TARGETS_EUR[idx]
        sym = currency.symbol()
        price = currency.value(self.price_eur, self.price_usd)
        ath = currency.value(self.ath_eur, self.ath_usd)
        stack_value = self.total_btcz * target
        self.moon_price.configure(text=t("holder.at_price", p=f"{target:g}", c=sym))
        self.moon_value.configure(text=format_fiat(stack_value, sym))
        if price > 0:
            mult = target / price
            self.moon_mult.configure(text=t("holder.multiplier", x=f"×{mult:,.0f}"))
        else:
            self.moon_mult.configure(text="")
        if ath > 0:
            ath_value = self.total_btcz * ath
            ath_mult = (ath / price) if price > 0 else 0
            self.moon_ath.configure(text=t("holder.ath", p=f"{ath:g}", c=sym,
                                          v=format_fiat(ath_value, sym), x=f"×{ath_mult:,.0f}"))
        else:
            self.moon_ath.configure(text="")
