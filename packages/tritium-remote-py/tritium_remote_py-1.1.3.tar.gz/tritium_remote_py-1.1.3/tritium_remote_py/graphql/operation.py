class GraphQLOperation:
    """
    GraphQL operation base class
    """

    def __init__(self, request_id):
        self._request_id = request_id

    @property
    def request_id(self):
        """
        The operation request ID.
        """
        return self._request_id

    def on_result(self, result):
        """
        @private
        """
        # must be overidden
        raise NotImplementedError()

    @property
    def more_results_expected(self):
        """
        @private
        """
        # must be overidden
        raise NotImplementedError()
