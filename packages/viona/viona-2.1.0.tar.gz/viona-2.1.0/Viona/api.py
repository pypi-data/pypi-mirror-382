import os
import json
import time
import requests
import aiohttp
import asyncio
from typing import Optional, Dict, Any


class Viona:
    BASE_URL = "https://viona.orvixgames.com/app/api/v1/models-1.5/orvix-viona-api/api.viona-1.5.php"

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 20,
        max_retries: int = 3,
        delay: float = 1.5,
    ):
        self.api_key = api_key or os.getenv("VIONA_API_KEY")
        if not self.api_key:
            raise ValueError("API anahtarı belirtilmeli veya VIONA_API_KEY ortam değişkeni tanımlanmalıdır.")
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay = delay

    def _request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                r = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
                duration = round(time.time() - start, 2)
                r.raise_for_status()
                data = r.json()
                data["response_time"] = f"{duration}s"
                return data
            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    return {"hata": "İstek zaman aşımına uğradı."}
                time.sleep(self.delay)
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                return {"hata": str(e)}
        return {"hata": "Bilinmeyen hata oluştu."}

    async def _async_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.BASE_URL, params=params, timeout=self.timeout) as resp:
                        text = await resp.text()
                        duration = round(time.time() - start, 2)
                        try:
                            data = json.loads(text)
                            data["response_time"] = f"{duration}s"
                            return data
                        except json.JSONDecodeError:
                            return {"hata": f"Geçersiz JSON yanıtı: {text}"}
            except asyncio.TimeoutError:
                if attempt == self.max_retries:
                    return {"hata": "Zaman aşımı (async)."}
                await asyncio.sleep(self.delay)
            except Exception as e:
                return {"hata": str(e)}
        return {"hata": "Bilinmeyen hata (async)."}

    def sor(self, soru: str) -> str:
        if not soru or not isinstance(soru, str):
            return "Geçerli bir metin girilmelidir."
        params = {"soru": soru.strip(), "key": self.api_key}
        data = self._request(params)
        if "cevap" in data:
            return data["cevap"]
        return data.get("hata", f"Beklenmeyen yanıt: {data}")

    async def sor_async(self, soru: str) -> str:
        if not soru or not isinstance(soru, str):
            return "Geçerli bir metin girilmelidir."
        params = {"soru": soru.strip(), "key": self.api_key}
        data = await self._async_request(params)
        if "cevap" in data:
            return data["cevap"]
        return data.get("hata", f"Beklenmeyen yanıt: {data}")

    def kontrol(self) -> str:
        params = {"soru": "ping", "key": self.api_key}
        data = self._request(params)
        if "cevap" in data:
            return f"Bağlantı başarılı ({data.get('response_time', 'N/A')})."
        return f"Bağlantı hatası: {data}"

    def model(self) -> str:
        return "Viona API v1.5 (Orvix Games)"

    def bilgi(self) -> Dict[str, Any]:
        return {
            "model": self.model(),
            "base_url": self.BASE_URL,
            "timeout": self.timeout,
            "retries": self.max_retries,
        }

    def __repr__(self):
        return f"<Viona | Model: {self.model()} | Timeout: {self.timeout}s | Retries: {self.max_retries}>"
