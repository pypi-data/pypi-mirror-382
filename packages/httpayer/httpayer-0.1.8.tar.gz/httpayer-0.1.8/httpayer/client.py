import requests
from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any

load_dotenv()

class HTTPayerClient:
    """
    Unified HTTPayer client for managing 402 responses, x402 payments,
    and dry-run simulation calls.
    """

    def __init__(self, router_url=None, api_key=None, timeout=60*10, use_session=True):
        """
        HTTPayerClient constructor.

        Args:
            router_url (str, optional): Base URL of the hosted httpayer service (without /pay), defaults to "https://api.httpayer.com".
            api_key (str, optional): API key for authenticating with the httpayer service, defaults to env "HTTPAYER_API_KEY".
            timeout (int, optional): Timeout for HTTP requests in seconds, defaults to 600 seconds (10 minutes).
            use_session (bool, optional): Whether to use a persistent requests.Session for connection pooling, defaults to True.
        """
        base_url = router_url or os.getenv("X402_ROUTER_URL", "https://api.httpayer.com")
        self.base_url = base_url.rstrip("/").removesuffix("/pay")

        self.pay_url = f"{self.base_url}/pay"
        self.sim_url = f"{self.base_url}/sim"

        self.timeout = timeout
        self.session = requests.Session() if use_session else requests

        self.api_key = api_key or os.getenv("HTTPAYER_API_KEY")
        if not self.base_url or not self.api_key:
            missing = []
            if not self.base_url:
                missing.append("X402_ROUTER_URL")
            if not self.api_key:
                missing.append("HTTPAYER_API_KEY")
            raise ValueError(f"Missing configuration: {', '.join(missing)}")

    # -------------------------------
    # Explicit methods
    # -------------------------------

    def pay_invoice(
        self,
        api_url: str,
        api_method: str = "GET",
        api_payload: Optional[Dict[str, Any]] = None,
        api_params: Optional[Dict[str, Any]] = None,
        api_headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Pay a 402 payment (via router service)."""
        return self._call_router(self.pay_url, api_url, api_method, api_payload, api_params, api_headers)


    def simulate_invoice(
        self,
        api_url: str,
        api_method: str = "GET",
        api_payload: Optional[Dict[str, Any]] = None,
        api_params: Optional[Dict[str, Any]] = None,
        api_headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Dry-run simulation call: returns payment requirements without paying."""
        return self._call_router(self.sim_url, api_url, api_method, api_payload, api_params, api_headers)

    # -------------------------------
    # Internal helper
    # -------------------------------

    def _call_router(
        self,
        endpoint: str,
        api_url: str,
        api_method: str = "GET",
        api_payload: Optional[Dict[str, Any]] = None,
        api_params: Optional[Dict[str, Any]] = None,
        api_headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """Helper to POST to /pay or /sim with proper auth + body."""
        data = {
            "api_url": api_url,
            "method": api_method,
            "payload": api_payload or {}
        }
        if api_params:
            data["params"] = api_params
        if api_headers:
            data["headers"] = api_headers

        header = {"x-api-key": self.api_key}
        resp = self.session.post(endpoint, headers=header, json=data, timeout=self.timeout)
        return resp

    # -------------------------------
    # Unified request interface
    # -------------------------------

    def request(self, url: str, method: str, simulate: bool = False, **kwargs) -> requests.Response:
        """
        Perform an HTTP request that auto-handles 402 Payment Required flows.

        If simulate=True, will call the /sim endpoint instead of /pay when 402 occurs.

        Args:
            url (str): The URL to send the request to.
            method (str): The HTTP method to use (e.g., "GET", "POST").
            simulate (bool, optional): If True, will simulate the payment instead of paying. Defaults to False.
            **kwargs: Additional arguments to pass to requests.request (e.g., headers, json, params).
        """
        resp = self.session.request(method, url, timeout=self.timeout, **kwargs)

        if resp.status_code == 402:
            api_payload = kwargs.get("json") or {}
            api_params = kwargs.get("params") or {}
            api_headers = kwargs.get("headers") or {}

            endpoint = self.sim_url if simulate else self.pay_url
            resp = self._call_router(
                endpoint, url, method, api_payload, api_params, api_headers
            )

        return resp
