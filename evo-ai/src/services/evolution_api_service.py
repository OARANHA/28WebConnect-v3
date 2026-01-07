import logging
import httpx
import asyncio
from typing import Any, Dict, List, Optional, Callable
from src.config.settings import settings

logger = logging.getLogger(__name__)

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

    # ========== EvoAI Methods ==========
    
    async def create_evoai_bot(
        self,
        instance_name: str,
        agent_url: str,
        api_key: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """POST /evoai/create/{instanceName}"""
        url = f"{self.base_url}/evoai/create/{instance_name}"

        payload = {
            "enabled": True,
            "agentUrl": agent_url,
            "apiKey": api_key,
            "triggerType": "all",
            "triggerOperator": "contains",
            "triggerValue": "",
            "expire": 0,
            "keywordFinish": "",
            "delayMessage": 1000,
            "unknownMessage": "Desculpe, não entendi sua mensagem.",
            "listeningFromMe": False,
            "stopBotFromMe": False,
            "keepOpen": False,
            "debounceTime": 0,
            "ignoreJids": []
        }

        if options:
            payload.update(options)

        logger.info(f"🔗 Criando EvoAI bot: {instance_name}")

        async def _req():
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, headers=self._headers(), json=payload)
                logger.info(f"📡 Response {resp.status_code}: {resp.text[:500]}")
                resp.raise_for_status()
                return resp.json()

        return await self._with_retries(_req)

    async def find_evoai_bots(self, instance_name: str) -> Dict[str, Any]:
        """GET /evoai/find/{instanceName}"""
        url = f"{self.base_url}/evoai/find/{instance_name}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def fetch_evoai_bot(self, instance_name: str, bot_id: str) -> Dict[str, Any]:
        """GET /evoai/fetch/{evoaiId}/{instanceName}"""
        url = f"{self.base_url}/evoai/fetch/{bot_id}/{instance_name}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def update_evoai_bot(
        self,
        bot_id: str,
        instance_name: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """PUT /evoai/update/{evoaiId}/{instanceName}"""
        url = f"{self.base_url}/evoai/update/{bot_id}/{instance_name}"
        
        async def _req():
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.put(url, headers=self._headers(), json=updates)
                resp.raise_for_status()
                return resp.json()
        
        return await self._with_retries(_req)

    async def delete_evoai_bot(self, bot_id: str, instance_name: str) -> Dict[str, Any]:
        """DELETE /evoai/delete/{evoaiId}/{instanceName}"""
        url = f"{self.base_url}/evoai/delete/{bot_id}/{instance_name}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.delete(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def evoai_settings(self, instance_name: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /evoai/settings/{instanceName}"""
        url = f"{self.base_url}/evoai/settings/{instance_name}"
        
        async def _req():
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(url, headers=self._headers(), json=settings_data)
                resp.raise_for_status()
                return resp.json()
        
        return await self._with_retries(_req)

    async def fetch_evoai_settings(self, instance_name: str) -> Dict[str, Any]:
        """GET /evoai/fetchSettings/{instanceName}"""
        url = f"{self.base_url}/evoai/fetchSettings/{instance_name}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def change_evoai_status(self, instance_name: str, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /evoai/changeStatus/{instanceName}"""
        url = f"{self.base_url}/evoai/changeStatus/{instance_name}"
        
        async def _req():
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(url, headers=self._headers(), json=status_data)
                resp.raise_for_status()
                return resp.json()
        
        return await self._with_retries(_req)

    async def fetch_evoai_sessions(self, instance_name: str, bot_id: str) -> Dict[str, Any]:
        """GET /evoai/fetchSessions/{evoaiId}/{instanceName}"""
        url = f"{self.base_url}/evoai/fetchSessions/{bot_id}/{instance_name}"
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(url, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def evoai_ignore_jid(self, instance_name: str, ignore_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /evoai/ignoreJid/{instanceName}"""
        url = f"{self.base_url}/evoai/ignoreJid/{instance_name}"
        
        async def _req():
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                resp = await client.post(url, headers=self._headers(), json=ignore_data)
                resp.raise_for_status()
                return resp.json()
        
        return await self._with_retries(_req)
