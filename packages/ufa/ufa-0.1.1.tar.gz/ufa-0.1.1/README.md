# ufa-client-tiny

Small UFA client

## Downloading files


```python
from pathlib import Path
from ufa.client import UFAClient

client = UFAClient(base_url="https://api.edge.deeporigin.io/files/", token="...", org_key="deeporigin")

# Download to a specific directory; it will be created if missing
out_path = asyncio.run(
    client.download_file(
        file_path="tests/ufa/ligand.sdf",
        org_key="deeporigin",
        download_dir=Path("/tmp/ufa-downloads")
    )
)
print(out_path)  # absolute path to the downloaded file
```

