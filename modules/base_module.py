import customtkinter as ctk

from app.ui.theme import COLORS


class BaseModule(ctk.CTkFrame):
    key = "base"
    name_key = "nav.base"
    icon = ""

    def __init__(self, master, datalayer):
        super().__init__(master, fg_color=COLORS["bg"])
        self.datalayer = datalayer
        self.built = False
        self.navigate = None

    def build(self):
        pass

    def on_show(self):
        if not self.built:
            self.build()
            self.built = True
        self.refresh()

    def refresh(self):
        pass

    def retranslate(self):
        pass
