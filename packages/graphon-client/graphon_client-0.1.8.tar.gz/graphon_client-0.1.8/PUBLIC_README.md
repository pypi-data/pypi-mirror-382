# Graphon Client (Python)

Simple async client for the Graphon API.

## Installation

```bash
pip install graphon-client
```

Requires Python 3.8+.

## Quickstart

```python
import asyncio
from graphon_client import GraphonClient

async def main():
    # 1) Create the client with your API token
    client = GraphonClient(token="<YOUR_TOKEN>")

    # 2) Upload some local files (mp4/pdf/docx). This will:
    #    - Request signed upload URLs
    #    - Stream each file via HTTP PUT
    uploads = await client.upload_files([
        "/absolute/path/to/file1.pdf",
        "/absolute/path/to/file2.mp4",
    ])

    # uploads -> [{"filename": "file1.pdf", "uuid": "<uuid_folder>"}, ...]
    uuid_directories = [u["uuid"] for u in uploads]

    # 3) Create an index/graph and obtain a group UUID
    group_uuid = await client.create_index(uuid_directories)

    # 4) Query the graph
    answer = await client.query(group_uuid, "What are the key takeaways?")
    print(answer)

asyncio.run(main())
```

## API Surface

- `upload_files(file_paths: List[str]) -> List[dict]`
- `create_index(uuid_directories: List[str]) -> str`
- `query(group_uuid: str, query_text: str) -> str`



