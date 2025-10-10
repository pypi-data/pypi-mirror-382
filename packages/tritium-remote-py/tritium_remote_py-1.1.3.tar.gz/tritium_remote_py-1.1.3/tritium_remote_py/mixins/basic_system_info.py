from collections import namedtuple

from ..exceptions import raise_if_graphql_errors


BasicSystemInfo = namedtuple("BasicSystemInfo", ["serial", "version", "name"])


class BasicSystemInfoMixin:
    async def basic_system_info(self):
        """
        Queries the system for basic information:
        - Serial
        - Tritium version
        - Name
        """

        response = await self.query(
            """
query BasicSystemInfo {
    system {
        serial
        version
        name
    }
}            
        """
        )

        raise_if_graphql_errors(response)

        info = response["data"]["system"]
        return BasicSystemInfo(**info)
