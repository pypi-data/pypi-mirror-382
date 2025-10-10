import asyncio
import json

from .graphql import GraphQLQuery, GraphQLSubscription, GraphQLLiveQuery

from .mixins.basic_system_info import BasicSystemInfoMixin
from .mixins.scripts import ScriptsMixin
from .mixins.sequences import SequencesMixin
from .mixins.messages import MessagesMixin


class TritiumRemote(BasicSystemInfoMixin, ScriptsMixin, SequencesMixin, MessagesMixin):
    """
    A connecton to a remote Tritium system for interaction using its GraphQL API.

    Supports free-form GraphQL queries, mutations, subscriptions and live
    queries, or more specialised methods for controlling scripts, playing
    sequences etc
    """

    TIMEOUT_SECONDS = 10

    _connector = None

    def __init__(self, connector, on_message_handling_error=None):
        """
        Args:
            connector: Connection method (currently WebSocket only)
            on_message_handling_error (callback): For notification of errors during message handling, passed as `dict`.
        """
        self._connector = connector
        self._on_message_handling_error = on_message_handling_error
        self._next_request_id = 0
        self._graphql_operations_by_id = {}

    @property
    def connected(self):
        """
        True if connected to the Tritium system.
        """
        return self._connector and self._connector.connected

    async def connect(self):
        """
        Attempts to connect to the Tritium system
        """
        await self._connector.connect(self._on_message)

    async def disconnect(self):
        """
        Disconnects from the Tritium system (permanently).
        """
        await self._connector.disconnect()
        self._connector = None
        self._send = None

    ##########################################################################

    async def query(self, document, variables=None):
        """
        Sends a free-form GraphQL `query` or `mutation` request, and waits for the response.

        Args:
            document (str): A GraphQL `query` or `mutation` document
            variables (dict): Variable values by name, which must be declared in the document.

        Raises:
            `TimeoutError` if the Tritium system does not reply within `TIMEOUT_SECONDS`.

        Returns:
            The response from the system as a `dict` with `data` and possible `errors`.
        """
        request_id = await self._send_graphql_message(document, variables)

        query = GraphQLQuery(request_id)
        self._add_graphql_operation(request_id, query)

        # wait for response, or eventually raise asyncio.TimeoutError
        return await asyncio.wait_for(query.result, self.TIMEOUT_SECONDS)

    async def subscribe(self, document, variables=None):
        """
        Sends a GraphQL `subscription` request and provides a stream of results.

        Args:
            document (str): A GraphQL `subscription` document
            variables (dict): Variable values by name, which must be declared in the document.

        Returns:
            A `tritium_remote_py.graphql.subscription.GraphQLSubscription` object

        """
        request_id = await self._send_graphql_message(document, variables)

        async def cancel():
            self._remove_graphql_operation(request_id)
            await self._send_graphql_close_message(request_id)

        subscription = GraphQLSubscription(request_id, cancel)
        self._add_graphql_operation(request_id, subscription)

        return subscription

    async def live_query(self, document, variables=None, make_value=None):
        """
        Sends a GraphQL `subscription` request but returns an object for watching the
        response value.

        The GraphQL API is expected to provide a stream of updated values of a certain variable
        or structure.  By convention, live query subscriptions are named `live{Something}` to
        distinguish them from plain stream-of-data GraphQL subscriptions.

        Args:
            document (str): A GraphQL `subscription` document
            variables (dict): Variable values by name, which must be declared in the document.
            make_value (function): A function which creates the required value type from the raw response data

        Returns:
            A `tritium_remote_py.graphql.live_query.GraphQLLiveQuery` object

        """
        subscription = await self.subscribe(document, variables)
        live_query = GraphQLLiveQuery(subscription, make_value)
        # replaces subscription
        self._add_graphql_operation(subscription.request_id, live_query)
        return live_query

    ##########################################################################

    async def _send(self, msg):
        if self._connector:
            await self._connector.send(msg)

    def _on_message(self, msg):
        try:
            m = json.loads(msg)
        except Exception as e:
            self._on_message_error(error="failed to decode message JSON", exception=e)
            return

        try:
            message_type = m["type"]
            result = m["data"]
            request_id = m["request_id"]
        except KeyError as e:
            self._on_message_error(error="invalid message", exception=e)
            return

        if message_type == "graphql_response":
            self._on_graphql_response(request_id, result)
        else:
            self._on_message_error(error=f"unrecognised message type: {message_type}")

    def _on_message_error(self, **error):
        if self._on_message_handling_error:
            self.self._on_message_handling_error(error)

    async def _send_graphql_message(self, document, variables):
        request_id = self._next_request_id
        self._next_request_id += 1

        msg = json.dumps(
            {
                "type": "graphql",
                "request_id": request_id,
                "document": document,
                "variable_values": variables,
            }
        )

        await self._send(msg)

        return request_id

    async def _send_graphql_close_message(self, request_id):
        msg = json.dumps(
            {
                "type": "graphql_close",
                "request_id": request_id,
            }
        )

        await self._send(msg)

    def _add_graphql_operation(self, request_id, graphql_operation):
        self._graphql_operations_by_id[request_id] = graphql_operation

    def _remove_graphql_operation(self, request_id):
        try:
            del self._graphql_operations_by_id[request_id]
        except KeyError:
            pass

    def _on_graphql_response(self, request_id, result):
        try:
            op = self._graphql_operations_by_id[request_id]
            op.on_result(result)

            if not op.more_results_expected:
                self._remove_graphql_operation(request_id)
        except KeyError:
            pass
