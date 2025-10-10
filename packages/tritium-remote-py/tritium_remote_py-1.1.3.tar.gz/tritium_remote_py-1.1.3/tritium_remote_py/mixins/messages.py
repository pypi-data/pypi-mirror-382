from ..exceptions import raise_if_graphql_errors


class MessagesMixin:
    async def post_message(self, channel, message):
        """
        Post a message to a named channel for a script to pick up.

        Args:
            channel (str): The channel name
            message (any JSON encodable value): The message
        """
        document = """
mutation PostMessage($input: PostMessageInput!) {
   postMessage(input: $input) 
}
"""
        variables = {"input": {"channel": channel, "message": message}}

        response = await self.query(document, variables)

        raise_if_graphql_errors(response)
