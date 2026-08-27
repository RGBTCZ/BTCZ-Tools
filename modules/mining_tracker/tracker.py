import calendar
import csv
import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from app.core.i18n import t
from app.ui.theme import COLORS, font
from app.ui.widgets import LogConsole, StatCard
from app.utils.format import format_btcz
from config.config import MINING_THRESHOLD
from modules.base_module import BaseModule

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(exist_ok=True)
ADDRESSES_FILE = DATA_DIR / "addresses.json"


def load_addresses():
    if ADDRESSES_FILE.exists():
        try:
            data = json.loads(ADDRESSES_FILE.read_text(encoding="utf-8"))
            return data.get("addresses", [])
        except Exception:
            return []
    return []


def save_addresses(addresses):
    unique = []
    for addr in addresses:
        addr = addr.strip()
        if addr and addr not in unique:
            unique.append(addr)
    ADDRESSES_FILE.write_text(json.dumps({"addresses": unique}, indent=2), encoding="utf-8")
    return unique


def remember_address(address):
    addresses = load_addresses()
    address = address.strip()
    if address in addresses:
        addresses.remove(address)
    addresses.insert(0, address)
    return save_addresses(addresses)


def remove_address(address):
    addresses = load_addresses()
    address = address.strip()
    if address in addresses:
        addresses.remove(address)
    return save_addresses(addresses)


class DatePicker(ctk.CTkToplevel):
    def __init__(self, master, target_entry):
        super().__init__(master)
        self.target_entry = target_entry
        self.title("Select date")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        current = target_entry.get().strip()
        try:
            selected = datetime.strptime(current, "%d/%m/%Y")
        except Exception:
            selected = datetime.now()

        self.year = selected.year
        self.month = selected.month

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=12, pady=(12, 6))
        ctk.CTkButton(self.header, text="<", width=36, command=self.prev_month).pack(side="left")
        self.title_lbl = ctk.CTkLabel(self.header, text="", font=font(15, "bold"))
        self.title_lbl.pack(side="left", expand=True)
        ctk.CTkButton(self.header, text=">", width=36, command=self.next_month).pack(side="right")

        self.grid_frame = ctk.CTkFrame(self)
        self.grid_frame.pack(padx=12, pady=(0, 12))
        self.draw()
        self.after(50, self.center)

    def center(self):
        self.update_idletasks()
        x = self.master.winfo_rootx() + 160
        y = self.master.winfo_rooty() + 200
        self.geometry(f"+{x}+{y}")

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.draw()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.draw()

    def draw(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.title_lbl.configure(text=datetime(self.year, self.month, 1).strftime("%B %Y"))
        days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for col, day in enumerate(days):
            ctk.CTkLabel(self.grid_frame, text=day, width=36).grid(row=0, column=col, padx=2, pady=2)
        month_days = calendar.Calendar(firstweekday=0).monthdayscalendar(self.year, self.month)
        for row, week in enumerate(month_days, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(self.grid_frame, text="", width=36).grid(row=row, column=col, padx=2, pady=2)
                    continue
                date_str = f"{day:02d}/{self.month:02d}/{self.year}"
                ctk.CTkButton(
                    self.grid_frame,
                    text=str(day),
                    width=36,
                    command=lambda value=date_str: self.choose(value),
                ).grid(row=row, column=col, padx=2, pady=2)

    def choose(self, value):
        self.target_entry.delete(0, "end")
        self.target_entry.insert(0, value)
        self.destroy()


class MiningTrackerModule(BaseModule):
    key = "tracker"
    name_key = "nav.tracker"
    icon = "⛏️"

    def build(self):
        self.last_result = None
        self.addresses = load_addresses()
        self.analyzing = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.title_lbl = ctk.CTkLabel(self, text=t("title.tracker"), font=font(24, "bold"))
        self.title_lbl.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="w")

        form = ctk.CTkFrame(self, corner_radius=16, fg_color=COLORS["card"])
        form.grid(row=1, column=0, padx=24, pady=8, sticky="ew")
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

        self.lbl_address = ctk.CTkLabel(form, text=t("f.address"))
        self.lbl_address.grid(row=0, column=0, padx=14, pady=(14, 6), sticky="w")
        address_wrap = ctk.CTkFrame(form, fg_color="transparent")
        address_wrap.grid(row=0, column=1, columnspan=3, padx=14, pady=(14, 6), sticky="ew")
        address_wrap.grid_columnconfigure(0, weight=1)
        self.address = ctk.CTkComboBox(address_wrap, values=self.addresses or [""], height=36)
        self.address.set("")
        self.address.grid(row=0, column=0, sticky="ew")
        self.remove_btn = ctk.CTkButton(
            address_wrap,
            text=t("b.remove"),
            width=90,
            height=36,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            command=self.remove_selected_address,
        )
        self.remove_btn.grid(row=0, column=1, padx=(8, 0))

        self.lbl_hint = ctk.CTkLabel(form, text=t("f.address_hint"), text_color=COLORS["muted"])
        self.lbl_hint.grid(row=1, column=1, columnspan=3, padx=14, pady=(0, 6), sticky="w")

        self.lbl_start = ctk.CTkLabel(form, text=t("f.start"))
        self.lbl_start.grid(row=2, column=0, padx=14, pady=6, sticky="w")
        start_wrap = ctk.CTkFrame(form, fg_color="transparent")
        start_wrap.grid(row=2, column=1, padx=14, pady=6, sticky="ew")
        start_wrap.grid_columnconfigure(0, weight=1)
        self.start = ctk.CTkEntry(start_wrap, placeholder_text=t("f.date_ph"), height=36)
        self.start.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(start_wrap, text="📅", width=42, command=lambda: DatePicker(self, self.start)).grid(
            row=0, column=1, padx=(8, 0)
        )

        self.lbl_end = ctk.CTkLabel(form, text=t("f.end"))
        self.lbl_end.grid(row=2, column=2, padx=14, pady=6, sticky="w")
        end_wrap = ctk.CTkFrame(form, fg_color="transparent")
        end_wrap.grid(row=2, column=3, padx=14, pady=6, sticky="ew")
        end_wrap.grid_columnconfigure(0, weight=1)
        self.end = ctk.CTkEntry(end_wrap, placeholder_text=t("f.end_ph"), height=36)
        self.end.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(end_wrap, text="📅", width=42, command=lambda: DatePicker(self, self.end)).grid(
            row=0, column=1, padx=(8, 0)
        )

        self.details = ctk.CTkSwitch(form, text=t("sw.details"))
        self.details.grid(row=3, column=0, columnspan=2, padx=14, pady=(8, 14), sticky="w")

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=3, column=3, padx=14, pady=(8, 14), sticky="e")
        self.export_btn = ctk.CTkButton(
            buttons, text=t("b.export"), height=40, fg_color="#2b2b2b", command=self.export_csv
        )
        self.export_btn.pack(side="left", padx=(0, 8))
        self.btn = ctk.CTkButton(buttons, text=t("b.analyze"), height=40, command=self.run_analysis)
        self.btn.pack(side="left")

        summary = ctk.CTkFrame(self, fg_color="transparent")
        summary.grid(row=2, column=0, padx=24, pady=(6, 6), sticky="ew")
        for i in range(4):
            summary.grid_columnconfigure(i, weight=1, uniform="sum")
        self.cards = {
            "c.total": StatCard(summary, t("c.total")),
            "c.rewards": StatCard(summary, t("c.rewards")),
            "c.avg": StatCard(summary, t("c.avg")),
            "c.biggest": StatCard(summary, t("c.biggest")),
        }
        for i, key in enumerate(["c.total", "c.rewards", "c.avg", "c.biggest"]):
            self.cards[key].grid(row=0, column=i, padx=6, pady=6, sticky="ew")

        self.console = LogConsole(self)
        self.console.grid(row=3, column=0, padx=24, pady=(8, 8), sticky="nsew")

        self.status = ctk.CTkLabel(self, text=t("st.ready"), anchor="w", text_color=COLORS["muted"])
        self.status.grid(row=4, column=0, padx=26, pady=(0, 14), sticky="ew")

    def retranslate(self):
        if not self.built:
            return
        self.title_lbl.configure(text=t("title.tracker"))
        self.lbl_address.configure(text=t("f.address"))
        self.lbl_hint.configure(text=t("f.address_hint"))
        self.lbl_start.configure(text=t("f.start"))
        self.lbl_end.configure(text=t("f.end"))
        self.remove_btn.configure(text=t("b.remove"))
        self.export_btn.configure(text=t("b.export"))
        self.details.configure(text=t("sw.details"))
        self.start.configure(placeholder_text=t("f.date_ph"))
        self.end.configure(placeholder_text=t("f.end_ph"))
        for key, card in self.cards.items():
            card.set_title(t(key))
        if not self.analyzing:
            self.btn.configure(text=t("b.analyze"))
            self.status.configure(text=t("st.ready"))

    def log(self, text, tag="info"):
        self.console.log(text, tag)

    def refresh_address_box(self, selected=""):
        self.address.configure(values=self.addresses or [""])
        self.address.set(selected)

    def remove_selected_address(self):
        address = self.address.get().strip()
        if not address:
            self.log(t("m.no_addr_selected"), "warn")
            return
        if address not in load_addresses():
            self.address.set("")
            self.log(t("m.addr_not_saved"), "warn")
            return
        self.addresses = remove_address(address)
        self.refresh_address_box("")
        self.log(t("m.addr_removed", a=address), "ok")

    def run_analysis(self):
        address = self.address.get().strip()
        start = self.start.get().strip()
        end = self.end.get().strip() or start
        show_details = self.details.get() == 1

        if not address:
            self.log(t("m.need_address"), "err")
            return
        if not start:
            self.log(t("m.need_start"), "err")
            return

        self.addresses = remember_address(address)
        self.refresh_address_box(address)
        self.console.clear()
        self.last_result = None
        self.analyzing = True
        self.btn.configure(state="disabled", text=t("b.analyzing"))
        self.status.configure(text=t("b.analyzing"))

        threading.Thread(
            target=self._worker, args=(address, start, end, show_details), daemon=True
        ).start()

    def _worker(self, address, start, end, show_details):
        try:
            result = self._analyze(address, start, end, show_details)
            self.last_result = result
            self._update_cards(result)
            self.status.configure(text=t("st.done"))
        except ValueError:
            self.log(t("m.invalid_date"), "err")
            self.status.configure(text=t("st.date_error"))
        except Exception as exc:
            self.log(f"Error: {exc}", "err")
            self.status.configure(text=t("st.error"))
        finally:
            self.analyzing = False
            self.btn.configure(state="normal", text=t("b.analyze"))

    def _analyze(self, address, start_str, end_str, show_details):
        fmt = "%d/%m/%Y" if "/" in start_str else "%Y-%m-%d"
        start = datetime.strptime(start_str, fmt).replace(tzinfo=timezone.utc)
        end = datetime.strptime(end_str, fmt).replace(tzinfo=timezone.utc)
        if end < start:
            self.log(t("m.end_before_start"), "err")
            return None

        single_day = start == end
        self.log(t("m.analyzing", a=start_str, b=end_str) + "\n", "info")
        txs = self.datalayer.get_address_transactions(address, single_day, self.log)

        total_period = 0.0
        mining_total = 0
        biggest = 0.0
        days = []

        current = start
        while current <= end:
            date_str = current.strftime("%d/%m/%Y")
            start_ts = int(current.timestamp())
            end_ts = start_ts + 86400
            daily_total = 0.0
            daily_mining = 0
            for tx in txs:
                if start_ts <= tx.time < end_ts:
                    daily_total += tx.value
                    if tx.value > MINING_THRESHOLD:
                        daily_mining += 1
                        biggest = max(biggest, tx.value)
                        if show_details:
                            self.log(f"MINING  {date_str}  +{tx.value:.8f} BTCZ", "mine")
            if daily_total > 0 or daily_mining > 0:
                days.append((date_str, daily_total, daily_mining))
                total_period += daily_total
                mining_total += daily_mining
            current += timedelta(days=1)

        self.log("=" * 70, "title")
        self.log(t("r.result_header", a=start_str, b=end_str), "ok")
        self.log("=" * 70, "title")
        if not days:
            self.log(t("m.no_tx"), "warn")
        else:
            for date, total, mining in days:
                self.log(
                    f"{date}  ->  {total:12.8f} BTCZ   ({mining:2d} mining rewards)",
                    "ok" if mining else "info",
                )
        self.log("-" * 70, "title")
        self.log(t("r.period_total", v=f"{total_period:.8f}"), "ok")
        self.log(t("r.total_rewards", n=mining_total), "mine")
        self.log("=" * 70, "title")

        return {
            "days": days,
            "total_period": total_period,
            "mining_total": mining_total,
            "biggest": biggest,
        }

    def _update_cards(self, result):
        if not result:
            return
        days = result["days"]
        total = result["total_period"]
        active_days = len(days) or 1
        self.cards["c.total"].update_value(f"{format_btcz(total, 4)}", accent=COLORS["accent"])
        self.cards["c.rewards"].update_value(str(result["mining_total"]))
        self.cards["c.avg"].update_value(f"{format_btcz(total / active_days, 2)}")
        self.cards["c.biggest"].update_value(f"{format_btcz(result['biggest'], 2)}", accent=COLORS["mine"])

    def export_csv(self):
        if not self.last_result or not self.last_result["days"]:
            self.log(t("m.nothing_export"), "warn")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="btcz_mining_report.csv",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Received BTCZ", "Mining rewards"])
            total = 0.0
            mining = 0
            for date, amount, rewards in self.last_result["days"]:
                writer.writerow([date, f"{amount:.8f}", rewards])
                total += amount
                mining += rewards
            writer.writerow([])
            writer.writerow(["TOTAL", f"{total:.8f}", mining])
        self.log(t("m.csv_exported", p=path), "ok")
