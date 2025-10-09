import aiohttp
from typing import Optional, Dict
from .exceptions import JibitException, JibitErrorCode
from .helpers import parse_card_shaba_response
from .models import JibitTokens, Card

class JibitService:
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://napi.jibit.ir/ide/v1"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")

    async def generate_token(self) -> Optional[JibitTokens]:
        url = f"{self.base_url}/tokens/generate"
        payload = {"apiKey": self.api_key, "secretKey": self.secret_key}
        data = await self._post(url, payload)
        return JibitTokens(access_token=data["accessToken"], refresh_token=data["refreshToken"])

    async def refresh_token(self, tokens: JibitTokens) -> JibitTokens:
        url = f"{self.base_url}/tokens/refresh"
        payload = {"accessToken": tokens.access_token, "refreshToken": tokens.refresh_token}
        data = await self._post(url, payload)
        return JibitTokens(access_token=data["accessToken"], refresh_token=data["refreshToken"])

    async def check_service_availability(self, access_token: str) -> bool:
        url = f"{self.base_url}/services/availability?cardToIBAN=true"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = await self._get(url, headers)
        return bool(data)

    async def card_to_shaba(self, access_token: str, card_number: str) -> Card:
        url = f"{self.base_url}/cards?number={card_number}&iban=true"
        headers = {"Authorization": f"Bearer {access_token}"}
        data = await self._get(url, headers)
        return parse_card_shaba_response(data)

    # ---------- Internal helpers ----------
    async def _get(self, url: str, headers: Dict) -> dict:
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    return await self._handle_response(resp)
        except aiohttp.ClientConnectionError:
            raise JibitException(JibitErrorCode.SERVICE_UNAVAILABLE, "Connection failed", http_status=503)

    async def _post(self, url: str, json_data: dict) -> dict:
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=json_data) as resp:
                    return await self._handle_response(resp)
        except aiohttp.ClientConnectionError:
            raise JibitException(JibitErrorCode.SERVICE_UNAVAILABLE, "Connection failed", http_status=503)

    async def _handle_response(self, resp: aiohttp.ClientResponse) -> dict:
        try:
            content = await resp.json(content_type=None)
        except Exception:
            content = await resp.text()

        if resp.status == 400:
            raise JibitException(JibitErrorCode.INVALID_CARD, "Card invalid", http_status=400)
        if resp.status in (401, 403):
            raise JibitException(JibitErrorCode.UNAUTHORIZED, "Token invalid or expired", http_status=401)
        if resp.status >= 500:
            raise JibitException(JibitErrorCode.SERVICE_UNAVAILABLE, "Jibit API unavailable", http_status=503)
        if resp.status not in (200, 201):
            raise JibitException(JibitErrorCode.UNKNOWN_ERROR, f"Unexpected status {resp.status}: {content}", http_status=resp.status)

        if isinstance(content, dict):
            return content
        raise JibitException(JibitErrorCode.UNKNOWN_ERROR, f"Non-JSON response: {content}")
