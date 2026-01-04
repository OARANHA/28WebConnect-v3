import httpx
import asyncio
from typing import Any, Dict, List, Optional, Callable
from src.config.settings import settings

DEFAULT_TIMEOUT = 15.0
MAX_RETRIES = 3
BACKOFF_SECONDS = 1.0

class EvolutionApiService:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or settings.EVOLUTION_API_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.EVOLUTION_API_APIKEY
        if not self.api_key:
            # allow boot but raise on request
            pass

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["apikey"] = self.api_key
        return headers

    async def _with_retries(self, func: Callable[[], Any]):
        last_exc = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return await func()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_exc = e
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(BACKOFF_SECONDS * attempt)
                else:
                    raise

    async def fetch_instances(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/instance/fetchInstances"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
            # Evolution-API returns { status, error, response } where response is an array
            if isinstance(data, dict):
                if "data" in data and isinstance(data["data"], list):
                    return data["data"] or []
                if "response" in data and isinstance(data["response"], list):
                    return data["response"] or []
            if isinstance(data, list):
                return data
            return []

    async def create_instance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/instance/create"
        async def _req():
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(url, headers=self._headers(), json=payload)
                resp.raise_for_status()
                return resp.json()
        return await self._with_retries(_req)

    async def connect_instance(self, instance: str) -> Dict[str, Any]:
        url = f"{self.base_url}/instance/connect/{instance}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def get_connection_state(self, instance: str) -> Dict[str, Any]:
        url = f"{self.base_url}/instance/connectionState/{instance}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def logout_instance(self, instance: str) -> Dict[str, Any]:
        url = f"{self.base_url}/instance/logout/{instance}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.delete(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def delete_instance(self, instance: str) -> Dict[str, Any]:
        url = f"{self.base_url}/instance/delete/{instance}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.delete(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    # Chatbot EvoAI integration (optional phase-1 wiring)
    async def create_evoai_bot(self, instance_name: str, agent_url: str, api_key: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        # Evolution-API expects instance context (commonly via query param) and evoai payload
        url = f"{self.base_url}/chatbot/evoai/create"
        params = {"instanceName": instance_name}
        body = {
            "enabled": True,
            "agentUrl": agent_url,
            "apiKey": api_key,
            "triggerType": "all",
        }
        if extra:
            body.update(extra)
        async def _req():
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(url, headers=self._headers(), params=params, json=body)
                resp.raise_for_status()
                return resp.json()
        return await self._with_retries(_req)
