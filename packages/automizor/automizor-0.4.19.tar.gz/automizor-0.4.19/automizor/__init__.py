import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy = Retry(
    total=6,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 520, 521, 522, 523, 524],
    allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
    raise_on_status=False,
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
session.mount("http://", adapter)

version = "0.4.19"
