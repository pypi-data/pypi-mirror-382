import asyncio
import json


class MockConnector:
    _connected = False

    def __init__(self, auth_token=None):
        self._auth_token = auth_token
        self._mock_replies = asyncio.Queue()
        self._mock_reply_tasks = []

    @property
    def connected(self):
        return self._connected

    async def connect(self, on_message):
        self._on_message = on_message
        self._connected = True

    async def disconnect(self):
        self._connected = False

    async def send(self, msg):
        self.last_sent_msg = json.loads(msg)

        self.send_mock_replies()

    def add_mock_reply(self, **msg):
        self._mock_replies.put_nowait(msg)

    def send_mock_replies(self):
        while True:
            try:
                msg = self._mock_replies.get_nowait()
                task = asyncio.create_task(self.send_mock_reply(**msg))
                self._mock_reply_tasks.append(task)
            except asyncio.QueueEmpty:
                break

    async def send_mock_reply(self, **msg):
        self._on_message(json.dumps(msg))
