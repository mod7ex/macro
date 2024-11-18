import json
import urllib.parse as urlparse
from urllib.parse import urlencode

def params() -> object:
    with open('../.json') as json_data:
        data = json.load(json_data)
    return data

def url_target(release_id: int, realtime_start: str, realtime_end: str):
    _params = params()

    API_URL = _params['API_URL']

    url_parts = list(urlparse.urlparse(API_URL))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({
        "release_id": release_id,
        "api_key": _params['API_KEY'],
        "file_type": "json",
        "realtime_start": realtime_start,
        "realtime_end": realtime_end,
    })
    query

    url_parts[4] = urlencode(query)

    return urlparse.urlunparse(url_parts)