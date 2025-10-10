from enum import Enum

from ..exceptions import raise_if_graphql_errors


class ScriptAction(Enum):
    START = "START"
    STOP = "STOP"


class ScriptStatus(Enum):
    LOADED = "LOADED"
    RUNNING = "RUNNING"
    ERROR = "ERROR"


class ScriptsMixin:
    async def start_script(self, path):
        """
        Start executing the given script.

        *NB* The returned script status is the value after the `script` State
        Engine activity is started, but before that activity is picked up by
        the Scripts node to run the script.  Use `script_status` or
        `watch_script_status` to determine if the script actually runs OK.

        Args:
            path (str): The script path

        Returns:
            The script status (but see the note above).
        """
        return await self._trigger_script(path, ScriptAction.START)

    async def stop_script(self, path):
        """
        Stop the given script.

        Args:
            path (str): The script path

        Returns:
            The script status.
        """
        return await self._trigger_script(path, ScriptAction.STOP)

    async def _trigger_script(self, path, action):
        document = """
mutation ManuallyTriggerScript($input: ScriptTriggerInput!) {
    manuallyTriggerScript(input: $input) {
        script {
            status
        }
    }
}"""
        variables = {"input": {"path": path, "action": action.value}}
        response = await self.query(document, variables)

        raise_if_graphql_errors(response)

        status_text = response["data"]["manuallyTriggerScript"]["script"]["status"]

        return ScriptStatus[status_text]

    async def script_status(self, path):
        """
        Queries the given script's status.

        Args:
            path (str): The script path

        Returns:
            The script status.
        """
        document = """
query Script($path: String!) {
    script(path: $path) {
        status
    }
}"""
        variables = {"path": path}
        response = await self.query(document, variables)

        raise_if_graphql_errors(response)

        status_text = response["data"]["script"]["status"]

        return ScriptStatus[status_text]

    async def watch_script_status(self, path):
        """
        Watches the given script's status for changes.

        Args:
            path (str): The script path

        Returns:
            `tritium_remote_py.graphql.live_query.GraphQLLiveQuery`
        """

        document = """
subscription LiveScript($path: String!) {
    liveScript(path: $path) {
        status
    }
}"""
        variables = {"path": path}

        def make_value(response_data):
            return response_data["liveScript"]["status"]

        return await self.live_query(document, variables, make_value)
