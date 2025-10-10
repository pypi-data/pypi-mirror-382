import asyncio

from .operation import GraphQLOperation


class GraphQLQuery(GraphQLOperation):
    """
    A simple GrapQL query for data.
    """

    def __init__(self, request_id):
        super().__init__(request_id)

        loop = asyncio.get_running_loop()
        self._future = loop.create_future()

    def on_result(self, result):
        """
        @private
        """
        self._future.set_result(result)

    @property
    def more_results_expected(self):
        """
        @private
        """
        return False

    @property
    async def result(self):
        """
        The query result as a `dict` with `data` and possibly `errors`.
        """
        await self._future
        return self._future.result()
