"""Async Graphon client using httpx."""
import logging
import os
from typing import List, Dict, Any
import asyncio
import httpx


logger = logging.getLogger(__name__)

TIMEOUT = 60.0 * 35

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

    async def generate_upload_urls(self, filenames: List[str]) -> List[Dict[str, Any]]:
        """Generate V4 signed URLs for direct uploads to GCS.

        Args:
            filenames: Basename strings of files to be uploaded. Extensions must be one of
                .mp4, .pdf, .docx as enforced by the API.

        Returns:
            List of dicts with keys: filename, uuid_folder, signed_url, gcs_full_path, gcs_folder
        """
        try:
            endpoint = f"{self.api_base_url}/generate-multiple-upload-urls"
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    endpoint,
                    headers={**self._headers, "Content-Type": "application/json"},
                    json={"filenames": filenames},
                )
                response.raise_for_status()
                payload = response.json()
                return payload.get("upload_urls", [])
        except Exception as e:
            logger.error(f"[UPLOAD_URLS] ERROR: {str(e)}")
            raise e

    async def upload_file_to_signed_url(self, local_path: str, signed_url: str) -> None:
        """Upload a local file directly to a signed URL using HTTP PUT.

        Streams file bytes asynchronously to avoid memory spikes and to be compatible
        with httpx.AsyncClient.
        """
        async def _aiter_file_chunks(path: str, chunk_size: int = 1024 * 1024):
            # Read file on a thread to avoid blocking the event loop
            with open(path, "rb") as f:
                while True:
                    chunk = await asyncio.to_thread(f.read, chunk_size)
                    if not chunk:
                        break
                    yield chunk

        try:
            async with httpx.AsyncClient(timeout=None) as client:
                response = await client.put(
                    signed_url,
                    content=_aiter_file_chunks(local_path),
                    headers={"Content-Type": "application/octet-stream"},
                )
                response.raise_for_status()
        except Exception as e:
            logger.error(f"[SIGNED_PUT] ERROR while uploading {local_path}: {str(e)}")
            raise e

    async def upload_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """High-level helper: request signed URLs and upload the given files.

        Args:
            file_paths: Absolute or relative paths to local files.

        Returns:
            The upload info list returned from the API (filename, uuid_folder, etc.).
        """
        if not file_paths:
            return []

        filenames = [os.path.basename(p) for p in file_paths]
        upload_infos = await self.generate_upload_urls(filenames)
        info_by_name = {info["filename"]: info for info in upload_infos}

        # Validate that every requested file has a corresponding signed URL
        missing = [name for name in filenames if name not in info_by_name]
        if missing:
            raise RuntimeError(f"Missing signed URLs for filenames: {missing}")

        # Upload concurrently with a reasonable cap
        semaphore = asyncio.Semaphore(5)

        async def _upload_one(path: str) -> None:
            name = os.path.basename(path)
            info = info_by_name[name]
            async with semaphore:
                await self.upload_file_to_signed_url(path, info["signed_url"])

        await asyncio.gather(*(_upload_one(p) for p in file_paths))
        return [{"filename": x["filename"], "uuid": x["uuid_folder"]} for x in upload_infos]

    async def create_index(self, uuid_directories: List[str]) -> str:
        """
        Creates a graph from a list of UUID directories.
        """
        try:
            create_index_url = f"{self.api_base_url}/create_index"
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
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
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
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


