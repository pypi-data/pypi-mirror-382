from httpx import AsyncClient

_DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
_BASE_URL = "https://api.csfloat.com/"
_REQUEST_HEADER = {
    "Accept": "application/json, text/plain, */*",
    "DNT": "1",
    "Referer": "https://csfloat.com/",
    "Origin": "https://csfloat.com",
}


class CSFloatInspector:
    def __init__(self, userAgent: str = _DEFAULT_USER_AGENT, proxy: str | None = None) -> dict | None:
        """
        :param userAgent: The User-Agent string to use for requests. Default is a common browser User-Agent.
        :param proxy: Proxy settings. Can be a string (proxy URL) or None for no proxy.
        :raises TypeError: If userAgent is not a string or if proxy is not a string or None.
        :return: dict or None
        """
        self.userAgent = userAgent
        self.proxy = proxy
        if not isinstance(self.userAgent, str):
            raise TypeError("userAgent must be a string.")
        if not isinstance(proxy, (str, type(None))):
            raise TypeError("proxy must be a string or None.")
        self._client = AsyncClient(
            base_url=_BASE_URL,
            headers={"User-Agent": self.userAgent, **_REQUEST_HEADER},
            proxy=self.proxy,
        )

    async def inspect(self, inspect_link: str) -> dict:
        """
        :param inspect_link: The Steam inspect link of the item to inspect. Example: "steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561198309889674A22713179946D10143347042148975421"
        :raises httpx.HTTPStatusError: If the request to the API fails.
        :return: A dictionary containing the inspection data.
        """
        resp = await self._client.get(f"/?url={inspect_link}")
        resp.raise_for_status()
        return resp.json()
            

    async def getimg(self, inspect_link: str, file: bool = False) -> str | bytes:
        """
        :param inspect_link: The Steam inspect link of the item to inspect. Example: "steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20S76561198309889674A22713179946D10143347042148975421"
        :param file: If True, returns the image content as bytes. If False, returns the image URL as a string. Default is False.
        :raises httpx.HTTPStatusError: If the request to the API or image fails.
        :raises ValueError: If no image URL is found in the response.
        :return: The image URL as a string or the image content as bytes.
        """
        resp = await self._client.get(f"/?url={inspect_link}")
        if resp.status_code == 200:
            imgurl = resp.json().get("iteminfo", {}).get("imageurl", "")
            if not imgurl:
                raise ValueError("No image URL found in the response.")
            if not file:
                return imgurl
            imgresp = await self._client.get(imgurl)
            imgresp.raise_for_status()
            return imgresp.content
        resp.raise_for_status()
