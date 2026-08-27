from app.core.i18n import t
from app.ui.widgets import Placeholder
from modules.base_module import BaseModule


class PoolExplorerModule(BaseModule):
    key = "pools"
    name_key = "nav.pools"
    icon = "🌊"

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.placeholder = Placeholder(self, t("title.pools"), t("body.pools"))
        self.placeholder.grid(row=0, column=0, sticky="nsew", padx=24, pady=24)

    def retranslate(self):
        if self.built:
            self.placeholder.set_text(t("title.pools"), t("body.pools"))
