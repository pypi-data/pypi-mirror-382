"""
A pure Python library for interacting with a Tritium system.

Example - querying basic system info
```python
import os
import asyncio
import tritium_remote_py


async def main():
    auth_token = os.environ["TRITIUM_AUTH_TOKEN"]
    host = os.environ.get("TRITIUM_HOST", "localhost")

    tritium = await tritium_remote_py.connect_websocket(
        url=f"ws://{host}:1234",
        auth_token=auth_token,
        description="Python tritium-remote example - basic system info",
    )

    info = await tritium.basic_system_info()
    print("Serial:", info.serial)
    print("Version:", info.version)
    print("Name:", info.name)

    await tritium.disconnect()


asyncio.run(main())

```

See `tritium_remote_py.connect.connect` to get started.
"""

from .client import TritiumRemote  # noqa: F401
from .connect import connect_websocket  # noqa: F401
