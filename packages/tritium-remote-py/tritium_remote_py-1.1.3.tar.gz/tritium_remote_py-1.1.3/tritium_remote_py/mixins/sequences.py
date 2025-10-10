from ..exceptions import raise_if_graphql_errors


class SequencesMixin:
    async def play_sequence(self, project_path):
        """
        Play the given sequence.

        Args:
            project_path (str): The Tritium Animator project asset path
        """
        document = """
mutation PlaySequence($input: PlaySequenceInput!) {
    playSequence(input: $input) {
        id
    }
}
"""
        variables = {"input": {"projectPath": project_path}}
        response = await self.query(document, variables)

        raise_if_graphql_errors(response)

        # TODO what is this ID?
        return response["data"]["playSequence"]["id"]
