from app.core import settings
from app.utils.format import SOL_UNITS


def load_rigs():
    data = settings.get("rigs", [])
    return data if isinstance(data, list) else []


def save_rigs(rigs):
    settings.set("rigs", rigs)


def _num(value):
    try:
        return float(str(value).replace(",", ".").strip() or 0)
    except (ValueError, AttributeError):
        return 0.0


def rig_solps(rig):
    return _num(rig.get("hashrate")) * SOL_UNITS.get(rig.get("unit", "KSol/s"), 1)


def rigs_totals(rigs=None):
    if rigs is None:
        rigs = load_rigs()
    total_solps = sum(rig_solps(r) for r in rigs)
    total_power = sum(_num(r.get("power")) for r in rigs)
    return total_solps, total_power
