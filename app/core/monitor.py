import logging
import threading

from app.core import settings
from app.core.currency import currency
from app.core.i18n import t
from app.utils.format import format_btcz, format_fiat

log = logging.getLogger("monitor")

DEFAULTS = {
    "alert_interval": 90,
    "alert_price_on": False,
    "alert_price_target": 0.0,
    "alert_price_dir": "any",
    "alert_payout_on": False,
    "alert_rig_on": False,
    "alert_rig_pool": "",
    "alert_rig_addr": "",
    "alert_diff_on": False,
    "alert_diff_threshold": 5.0,
}


def _get(key):
    return settings.get(key, DEFAULTS.get(key))


class Monitor:
    def __init__(self, datalayer, notifier):
        self.datalayer = datalayer
        self.notifier = notifier
        self._thread = None
        self._stop = threading.Event()

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _state(self):
        state = settings.get("alert_state", {})
        return state if isinstance(state, dict) else {}

    def _save_state(self, state):
        settings.set("alert_state", state)

    def _loop(self):
        while not self._stop.is_set():
            try:
                self.check_once()
            except Exception as exc:
                log.warning("monitor cycle failed: %s", exc)
            interval = float(_get("alert_interval") or 90)
            self._stop.wait(max(30.0, interval))

    def check_once(self):
        state = self._state()
        if _get("alert_price_on"):
            self._check_price(state)
        if _get("alert_payout_on"):
            self._check_payout(state)
        if _get("alert_rig_on"):
            self._check_rig(state)
        if _get("alert_diff_on"):
            self._check_diff(state)
        self._save_state(state)

    def _check_price(self, state):
        target = float(_get("alert_price_target") or 0)
        if target <= 0:
            return
        market = self.datalayer.get_market()
        cur = float(currency.value(market.price_eur, market.price_usd) or 0)
        if cur <= 0:
            return
        sym = currency.symbol()
        last = state.get("price")
        state["price"] = cur
        if last is None:
            return
        direction = _get("alert_price_dir")
        up = last < target <= cur
        down = last > target >= cur
        fire = (direction == "up" and up) or (direction == "down" and down) or (direction == "any" and (up or down))
        if fire:
            arrow = "▲" if cur >= last else "▼"
            self.notifier.notify(
                t("notif.price_title"),
                t("notif.price_body", p=format_fiat(cur, sym, 8), t=format_fiat(target, sym, 8), a=arrow),
            )

    def _check_payout(self, state):
        from modules.mining_tracker.tracker import load_addresses

        recv = state.get("recv", {})
        for addr in load_addresses():
            try:
                stats = self.datalayer.get_address(addr)
            except Exception:
                continue
            total = float(stats.total_received or 0)
            prev = recv.get(addr)
            recv[addr] = total
            if prev is not None and total > prev + 1e-8:
                delta = total - prev
                self.notifier.notify(
                    t("notif.payout_title"),
                    t("notif.payout_body", v=format_btcz(delta, 4), a=self._short(addr)),
                )
        state["recv"] = recv

    def _check_rig(self, state):
        pool = _get("alert_rig_pool")
        addr = _get("alert_rig_addr")
        if not pool or not addr:
            return
        try:
            worker = self.datalayer.get_worker_stats(pool, addr)
        except Exception:
            return
        if worker is None or not worker.ok:
            return
        hp = float(worker.hashps or 0)
        prev = state.get("rig_hp")
        state["rig_hp"] = hp
        if prev is None:
            return
        if prev > 0 and hp == 0:
            self.notifier.notify(t("notif.rig_off_title"), t("notif.rig_off_body", a=self._short(addr)))
        elif prev == 0 and hp > 0:
            self.notifier.notify(t("notif.rig_on_title"), t("notif.rig_on_body", a=self._short(addr)))

    def _check_diff(self, state):
        threshold = float(_get("alert_diff_threshold") or 5)
        net = self.datalayer.get_network_stats()
        diff = float(net.difficulty or 0)
        if diff <= 0:
            return
        last = state.get("diff")
        state["diff"] = diff
        if last is None or last <= 0:
            return
        pct = (diff - last) / last * 100
        if abs(pct) >= threshold:
            sign = "+" if pct >= 0 else ""
            self.notifier.notify(t("notif.diff_title"), t("notif.diff_body", v=f"{sign}{pct:.1f}"))

    def _short(self, addr):
        return addr if len(addr) <= 16 else f"{addr[:8]}…{addr[-6:]}"
