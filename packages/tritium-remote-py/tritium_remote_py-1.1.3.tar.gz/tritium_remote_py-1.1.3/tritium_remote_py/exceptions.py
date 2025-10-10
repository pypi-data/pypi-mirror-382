class TritiumRemoteError(Exception):
    """
    Exception thrown when something goes wrong using `tritium_remote_py`.
    """

    pass


class GraphQLErrors(TritiumRemoteError):
    """
    Raised when a GraphQL response contains errors.
    """

    def __init__(self, graphql_errors):
        super().__init__(f"GraphQL errors: {graphql_errors}")
        self._graphql_errors = graphql_errors


def raise_if_graphql_errors(graphql_response):
    """
    Raises `GraphQLErrors` if there are *any* errors in the response.

    *NB* This may not be the behaviour you want - in some circumstances it is
    perfectly reasonable for a GraphQL operation to return both data and errors.
    """
    try:
        errors = graphql_response["errors"]
        if errors:
            raise GraphQLErrors(errors)
    except KeyError:
        pass
