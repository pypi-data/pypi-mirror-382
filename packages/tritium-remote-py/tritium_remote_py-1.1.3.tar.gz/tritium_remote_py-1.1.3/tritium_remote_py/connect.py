from .client import TritiumRemote
from .connection import WebSocketConnector
from .exceptions import TritiumRemoteError


async def connect(**kwargs):
    """
    Connects to a remote Tritium system, using the supplied keyword arguments
    to choose the connection method.

    Currently only WebSocket connections are supported. See `connect_websocket`
    below for more details.

    Returns:
        The connected `tritium_remote_py.client.TritiumRemote`.
    """

    try:
        url = kwargs["url"]
        auth_token = kwargs["auth_token"]
    except KeyError as e:
        raise TritiumRemoteError("Missing connection argument") from e

    description = kwargs.get("description")
    return await connect_websocket(url, auth_token, description)


async def connect_websocket(url, auth_token, description=None):
    """
    Connects to a remote Tritium system via WebSocket.

    Args:
        url (str): The Tritium system Gateway URL.
        auth_token (str): A JWT granting access to the given system.
        description (str): Human readable description of the connection.

    Returns:
        The connected `tritium_remote_py.client.TritiumRemote`.

    """

    connector = WebSocketConnector(url, auth_token, description)
    tritium_remote = TritiumRemote(connector)

    await tritium_remote.connect()

    return tritium_remote
