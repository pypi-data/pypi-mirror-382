import asyncio

from .operation import GraphQLOperation


class GraphQLLiveQuery(GraphQLOperation):
    """
    A GraphQL live query, a non-standard addition to the GraphQL world.
    Basically a query that receives updates to the queried value.
    """

    _last_value = None

    def __init__(self, subscription, make_value):
        super().__init__(subscription.request_id)
        self._subscription = subscription
        if make_value:
            self._make_value = make_value
        else:
            self._make_value = lambda d: d
        self._value_changed_event = asyncio.Event()

    async def cancel(self):
        """
        Cancel the live query.
        """
        await self._subscription.cancel()

    def on_result(self, result):
        """
        @private
        """
        self._subscription.on_result(result)
        self._last_value = self._make_value(result["data"])
        self._value_changed_event.set()

    @property
    def more_results_expected(self):
        """
        @private
        """
        return self._subscription.more_results_expected

    @property
    async def value_changed(self):
        """
        Awaitable event indicating that the value has been updated.
        """
        await self._value_changed_event.wait()
        self._value_changed_event.clear()

    @property
    def value(self):
        """
        The current query value.
        """
        return self._last_value
