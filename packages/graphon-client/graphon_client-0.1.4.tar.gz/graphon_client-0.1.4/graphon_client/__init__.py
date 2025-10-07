"""Async Graphon client using httpx."""
import logging
from typing import List
import httpx


logger = logging.getLogger(__name__)


API_BASE_URL = "https://public-api-service-485250924682.us-central1.run.app"

class GraphonClient:
    """A client library for interacting with the Graphon API."""

    def __init__(self, token: str):
        """
        Initializes the client with an API token and the base URL of the service.
        """
        api_base_url = API_BASE_URL
        self.api_base_url = api_base_url.rstrip('/')
        self._headers = {"Authorization": f"Bearer {token}"}

    async def create_index(self, uuid_directories: List[str]) -> str:
        """
        Creates a graph from a list of UUID directories.
        """
        try:
            create_index_url = f"{self.api_base_url}/create_index"
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    create_index_url,
                    headers=self._headers,
                    json={"uuid_directories": uuid_directories},
                )
                response.raise_for_status()
                return response.json()["group_uuid"]
        except Exception as e:
            logger.error(f"[CREATE_INDEX] ERROR: {str(e)}")
            raise e

    async def query(self, group_uuid: str, query_text: str) -> str:
        """
        Queries a graph from a job ID.
        """
        try:
            query_url = f"{self.api_base_url}/query"
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    query_url,
                    headers=self._headers,
                    json={"group_uuid": group_uuid, "query": query_text},
                )
                response.raise_for_status()
                return response.json()["answer"]
        except Exception as e:
            logger.error(f"[QUERY] ERROR: {str(e)}")
            raise e


