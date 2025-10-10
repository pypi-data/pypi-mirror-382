import os
import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from typing import Dict, Any, Optional

from wxo_agentic_evaluation.service_instance import tenant_setup


class WXOClient:
    def __init__(
        self, service_url, api_key, env: Optional[Dict[str, Any]] = None
    ):
        self.service_url = service_url
        self.api_key = api_key

        ov = os.getenv("WO_SSL_VERIFY")
        if ov and ov.strip().lower() in ("true", "false"):
            self._verify_ssl = ov.strip().lower() == "true"
        else:
            v, bs = (env.get("verify") if env else None), (
                env.get("bypass_ssl") if env else None
            )
            self._verify_ssl = (
                False
                if (
                    (bs is True)
                    or (isinstance(bs, str) and bs.strip().lower() == "true")
                    or (v is None)
                    or (
                        isinstance(v, str)
                        and v.strip().lower() in {"none", "null"}
                    )
                )
                else (v if isinstance(v, bool) else True)
            )

        if not self._verify_ssl:
            urllib3.disable_warnings(InsecureRequestWarning)

    def _get_headers(self) -> dict:
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def post(self, payload: dict, path: str, stream=False):
        url = f"{self.service_url}/{path}"
        return requests.post(
            url=url,
            headers=self._get_headers(),
            json=payload,
            stream=stream,
            verify=self._verify_ssl,
        )

    def get(self, path: str, params: dict = None):
        url = f"{self.service_url}/{path}"
        return requests.get(
            url,
            params=params,
            headers=self._get_headers(),
            verify=self._verify_ssl,
        )


def get_wxo_client(
    service_url: Optional[str], tenant_name: str, token: Optional[str] = None
) -> WXOClient:

    token, resolved_url, env = tenant_setup(service_url, tenant_name)
    service_url = service_url or resolved_url

    if not (service_url and str(service_url).strip()):
        raise ValueError(
            f"service_url not provided and not found in config for tenant '{tenant_name}'"
        )

    wxo_client = WXOClient(service_url=service_url, api_key=token, env=env)
    return wxo_client
