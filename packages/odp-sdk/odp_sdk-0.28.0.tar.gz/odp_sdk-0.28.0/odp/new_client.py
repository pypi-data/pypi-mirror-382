import io
import json
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .util.check_version import get_sdk_version

# NOTE(oha): deferred imports to avoid circular dependencies, will be fixed when we remove the old client
# from odp.client.auth import InteractiveTokenProvider

if TYPE_CHECKING:
    from .dataset import Dataset

read_retry_strategy = Retry(
    total=8,
    status_forcelist=[429, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    backoff_factor=1,  # exponential sleep (1s, 2s, 4s…)
)

write_retry_strategy = Retry(
    total=8,
    status_forcelist=[429],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
    backoff_factor=2,
)


class Response:
    def __init__(self, res: requests.Response):
        if res.status_code == 204:
            raise FileNotFoundError(res.text)
        if res.status_code == 400:
            raise ValueError(res.text)
        res.raise_for_status()
        self.res = res

    def reader(self):
        if self.res.raw is None:
            return io.BytesIO(self.res.content)
        return self.res.raw

    def iter(self) -> Iterator[bytes]:
        if self.res.raw is None:
            return iter([self.res.content])
        return self.res.raw

    def all(self) -> bytes:
        if self.res.raw is None:
            return self.res.content
        return self.res.raw.read()

    def json(self) -> Union[dict, list, None]:
        return self.res.json()

    @property
    def content(self) -> Union[bytes, Any]:
        return self.res.content

    @property
    def status_code(self) -> int:
        return self.res.status_code


class Client:
    """
    New ODP client for accessing datasets and other resources.
    supersedes the old odp.OdpClient
    """

    def __init__(self, base_url: str = "https://api.hubocean.earth/", jwt_bearer: str = "", api_key: str = ""):
        if api_key:
            self._auth = lambda: f"ApiKey {api_key}"
        elif jwt_bearer:
            if not jwt_bearer.startswith("Bearer "):
                jwt_bearer = "Bearer " + jwt_bearer
            self._auth = lambda: jwt_bearer

        elif os.getenv("JUPYTERHUB_API_TOKEN"):

            def get_token():
                res = requests.post("http://localhost:8000/access_token")
                res.raise_for_status()
                token: str = res.json()["token"]
                return "Bearer " + token

            self._auth = get_token
        else:
            self._setup_jwt()

        self.base_url = base_url.rstrip("/")

        # FIXME: this is wrong, sessions can't be this long
        self._http_client = requests.Session()
        self._http_client.headers.setdefault("User-Agent", "odp-sdk-python")

    def _setup_jwt(self):
        """
        fire up the JWT setup process on the browser
        """
        client_id = os.getenv("ODP_CLIENT_ID", "f96fc4a5-195b-43cc-adb2-10506a82bb82")
        from odp.client.auth import InteractiveTokenProvider

        prov = InteractiveTokenProvider(client_id=client_id)
        self._auth = lambda: f"Bearer {prov.get_token()}"
        # raise NotImplementedError("JWT authentication is not implemented yet.")

    def request(
        self,
        path: str,
        method: str = "POST",
        params: Optional[dict] = None,
        data: Union[Dict, bytes, Iterator[bytes], io.IOBase, None] = None,
        retry: bool = False,
    ) -> Response:
        """
        send a request to ODP
        """
        req = requests.Request(method, self.base_url + path, params=params, data=data)
        res = self._request(req, retry=retry)

        return Response(res)

    def _request(self, req: requests.Request, retry: bool = True) -> requests.Response:
        """
        base implementation to send a request to ODP
        may be overridden to use mechanisms other than http
        """
        req.headers.setdefault("Authorization", self._auth())  # allow override
        req.headers.setdefault("User-Agent", "odp-sdk-python/" + get_sdk_version())
        if isinstance(req.data, dict):
            req.data = json.dumps(req.data)
            req.headers.setdefault("Content-Type", "application/json")
        preq = req.prepare()
        # logging.info("request: %s %s %s", preq.method, preq.url, preq.body)
        if retry:
            retry_strategy = read_retry_strategy
        else:
            retry_strategy = write_retry_strategy

        with requests.Session() as s:
            adapter = HTTPAdapter(pool_connections=4, pool_maxsize=4, max_retries=retry_strategy)
            s.mount("http://", adapter)
            s.mount("https://", adapter)
            res = s.send(preq, stream=True)
        # this is the time it takes for the response headers to be returned, the body might take longer...
        logging.debug("response: %s in %.2fs from %s", res.status_code, res.elapsed.total_seconds(), res.url)
        return res

    def dataset(self, id: str) -> "Dataset":
        """fetch a dataset by id"""
        from .dataset import Dataset

        return Dataset(self, id)
