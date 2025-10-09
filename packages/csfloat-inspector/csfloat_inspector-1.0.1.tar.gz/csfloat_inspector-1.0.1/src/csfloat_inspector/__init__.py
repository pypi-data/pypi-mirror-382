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
    def __init__(self, UserAgent: str = _DEFAULT_USER_AGENT) -> dict | None:
        self.UserAgent = UserAgent
        self._client = AsyncClient(
            base_url=_BASE_URL,
            headers={"User-Agent": self.UserAgent, **_REQUEST_HEADER},
        )

    async def inspect(self, inspect_link: str) -> dict:
        resp = await self._client.get(f"/?url={inspect_link}")
        if resp.status_code == 200:
            return resp.json()
        else:
            resp.raise_for_status()

    async def getimg(self, inspect_link: str, file: bool = False) -> str | bytes:
        resp = await self._client.get(f"/?url={inspect_link}")
        if resp.status_code == 200:
            imgurl = resp.json().get("iteminfo", {}).get("imageurl", "")
            if not imgurl:
                raise ValueError("No image URL found in the response.")
            if not file:
                return imgurl
            imgresp = await self._client.get(imgurl)
            if imgresp.status_code == 200:
                return imgresp.content
            else:
                imgresp.raise_for_status()
        else:
            resp.raise_for_status()
