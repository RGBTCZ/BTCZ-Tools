import requests

from config.config import APP_VERSION, GITHUB_API_LATEST, HTTP_TIMEOUT


def _parse(version):
    version = str(version).strip().lstrip("vV")
    parts = []
    for chunk in version.split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def check_for_update(timeout=HTTP_TIMEOUT):
    resp = requests.get(GITHUB_API_LATEST, headers={"Accept": "application/vnd.github+json"}, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    tag = data.get("tag_name", "") or ""
    if _parse(tag) <= _parse(APP_VERSION):
        return None
    latest = tag.lstrip("vV")
    asset_url = None
    for asset in data.get("assets", []) or []:
        name = (asset.get("name") or "").lower()
        if name.endswith(".exe"):
            asset_url = asset.get("browser_download_url")
            break
    return {
        "latest": latest,
        "current": APP_VERSION,
        "html_url": data.get("html_url", "") or "",
        "asset_url": asset_url,
        "asset_name": f"BTCZ-Tools-v{latest}.exe",
        "notes": (data.get("body") or "").strip(),
    }


def download_update(asset_url, dest_path, progress_cb=None, timeout=60):
    with requests.get(asset_url, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("Content-Length", 0) or 0)
        done = 0
        with open(dest_path, "wb") as handle:
            for chunk in resp.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                handle.write(chunk)
                done += len(chunk)
                if progress_cb and total:
                    progress_cb(done / total)
    if progress_cb:
        progress_cb(1.0)
    return dest_path
