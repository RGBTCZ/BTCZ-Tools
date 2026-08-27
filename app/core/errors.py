import requests

from config.config import HTTP_TIMEOUT


class DataError(Exception):
    pass


class NetworkError(DataError):
    pass


def http_get_json(url, timeout=HTTP_TIMEOUT, params=None):
    try:
        resp = requests.get(url, timeout=timeout, params=params)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        raise NetworkError(str(exc)) from exc
    except ValueError as exc:
        raise DataError("Invalid JSON response") from exc
