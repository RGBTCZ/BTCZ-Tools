import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import customtkinter as ctk

from app.core.datalayer import BTCZDataLayer
from app.core.i18n import LANGUAGE_LABELS, LANGUAGES, i18n, t
from app.ui.theme import COLORS, apply_theme, font
from app.utils.assets import apply_window_icon, ensure_logo, load_logo_image
from config.config import APP_NAME, APP_VERSION
from modules.assistant.assistant import AssistantModule
from modules.dashboard.dashboard import DashboardModule
from modules.history.history import HistoryModule
from modules.holder.holder import HolderModule
from modules.mining_tracker.tracker import MiningTrackerModule
from modules.network_explorer.network_explorer import NetworkExplorerModule
from modules.pool_explorer.pool_explorer import PoolExplorerModule
from modules.profitability.profitability import ProfitabilityModule


class BTCZToolsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        apply_theme()
        ensure_logo()
        self.title(APP_NAME)
        self.geometry("1120x760")
        self.minsize(960, 680)
        self.configure(fg_color=COLORS["bg"])
        apply_window_icon(self)

        self.datalayer = BTCZDataLayer()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=COLORS["sidebar"])
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        brand = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, padx=18, pady=(24, 20), sticky="w")
        logo = load_logo_image((34, 34))
        if logo is not None:
            self.logo_ref = logo
            ctk.CTkLabel(brand, image=logo, text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            brand, text="BTCZ Tools", font=font(20, "bold"), text_color=COLORS["accent"]
        ).pack(side="left")

        self.container = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        module_classes = [
            DashboardModule,
            MiningTrackerModule,
            ProfitabilityModule,
            PoolExplorerModule,
            NetworkExplorerModule,
            HistoryModule,
            HolderModule,
            AssistantModule,
        ]

        self.modules = {}
        self.buttons = {}
        for index, cls in enumerate(module_classes, start=1):
            module = cls(self.container, self.datalayer)
            module.navigate = self.show
            module.grid(row=0, column=0, sticky="nsew")
            self.modules[cls.key] = module

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{cls.icon}  {t(cls.name_key)}",
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=COLORS["card_hover"],
                text_color=COLORS["text"],
                font=font(14),
                command=lambda key=cls.key: self.show(key),
            )
            btn.grid(row=index, column=0, padx=12, pady=4, sticky="ew")
            self.buttons[cls.key] = (btn, cls)

        spacer_row = len(module_classes) + 1
        lang_row = spacer_row + 1
        version_row = spacer_row + 2
        self.sidebar.grid_rowconfigure(spacer_row, weight=1)

        self.lang_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=[LANGUAGE_LABELS[code] for code in LANGUAGES],
            command=self.on_language_change,
            fg_color=COLORS["card"],
            button_color=COLORS["accent_dark"],
            button_hover_color=COLORS["accent"],
        )
        self.lang_menu.set(LANGUAGE_LABELS[i18n.lang])
        self.lang_menu.grid(row=lang_row, column=0, padx=12, pady=(4, 8), sticky="ew")

        ctk.CTkLabel(
            self.sidebar, text=f"v{APP_VERSION}", font=font(11), text_color=COLORS["muted"]
        ).grid(row=version_row, column=0, padx=20, pady=(0, 16), sticky="w")

        i18n.add_listener(self.retranslate_all)

        self.active = None
        self.show(DashboardModule.key)

    def on_language_change(self, label):
        for code, text in LANGUAGE_LABELS.items():
            if text == label:
                i18n.set_language(code)
                break

    def retranslate_all(self):
        for key, (btn, cls) in self.buttons.items():
            btn.configure(text=f"{cls.icon}  {t(cls.name_key)}")
        for module in self.modules.values():
            module.retranslate()
        self._highlight(self.active)

    def _highlight(self, active_key):
        for key, (btn, cls) in self.buttons.items():
            if key == active_key:
                btn.configure(fg_color=COLORS["card"], text_color=COLORS["accent"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text"])

    def show(self, key):
        self._highlight(key)
        module = self.modules[key]
        module.tkraise()
        module.on_show()
        self.active = key


def main():
    app = BTCZToolsApp()
    app.mainloop()


if __name__ == "__main__":
    main()
