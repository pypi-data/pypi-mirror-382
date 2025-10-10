import asyncio

from .operation import GraphQLOperation


class GraphQLSubscription(GraphQLOperation):
    """
    A GraphQL subscription providing a stream of results.
    """

    def __init__(self, request_id, cancel):
        super().__init__(request_id)
        self._cancel = cancel
        self._queue = asyncio.Queue()

    @property
    async def results(self):
        """
        Asynchronous iterator of results.

        Each is a `dict` with `data` and possible `errors`.
        """

        while True:
            result = await self._queue.get()
            yield result

    async def cancel(self):
        """
        Cancel the subscription.
        """
        await self._cancel()

    def on_result(self, result):
        """
        @private
        """
        self._queue.put_nowait(result)

    @property
    def more_results_expected(self):
        """
        @private
        """
        return True
