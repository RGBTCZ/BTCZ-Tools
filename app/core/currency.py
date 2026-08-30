from app.core import settings


class Currency:
    def __init__(self):
        code = settings.get("currency", "EUR")
        self.code = code if code in ("EUR", "USD") else "EUR"
        self._listeners = []

    def symbol(self):
        return "€" if self.code == "EUR" else "$"

    def value(self, eur, usd):
        return usd if self.code == "USD" else eur

    def set(self, code):
        if code not in ("EUR", "USD") or code == self.code:
            return
        self.code = code
        settings.set("currency", code)
        for callback in list(self._listeners):
            try:
                callback()
            except Exception:
                pass

    def add_listener(self, callback):
        self._listeners.append(callback)


currency = Currency()
