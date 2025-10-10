import asyncio
import websockets
import json


class WebSocketConnector:
    _ws = None
    _listen_task = None

    def __init__(self, url, auth_token, description):
        self._url = url
        self._auth_token = auth_token
        self._description = description

    @property
    def connected(self):
        return self._ws and self._ws.open

    @property
    def _headers(self):
        auth_token = self._auth_token
        metadata = json.dumps(
            {"session_type": "graphql", "description": self._description}
        )
        return {"x-tritium-token": auth_token, "x-tritium-session-metadata": metadata}

    async def connect(self, on_message):
        ws = await websockets.connect(self._url, additional_headers=self._headers)
        self._ws = ws

        async def listen():
            while True:
                msg = await ws.recv()
                on_message(msg)

        self._listen_task = asyncio.create_task(listen())

    async def disconnect(self):
        ws = self._ws
        if ws:
            self._ws = None
            await ws.close()

        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None

    async def send(self, msg):
        if self._ws:
            await self._ws.send(msg)
