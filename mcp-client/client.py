import json
import copy
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp.types import TextContent, ClientResult, CreateMessageResult
from mcp import ClientSession, StdioServerParameters, CreateMessageResult
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env
SERVER_SCRIPT_PATH = os.getenv("SERVER_SCRIPT_PATH")
MODEL = os.getenv("MODEL")

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    # methods will go here

    async def connect_to_mcp_server(self):
        """Connect to an MCP serve
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        server_script_path = SERVER_SCRIPT_PATH
        print(server_script_path)
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        # python <path to server script - main.py>
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path, "--mode", "stdio"], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write, sampling_callback=self.sampling_callback)
        )

        # Client sends initialize request with protocol version and capabilities
        # Server responds with its protocol version and capabilities
        # Client sends initialized notification as acknowledgment
        # Normal message exchange begins
        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_antropic_query(self, messages, include_tools=True) -> str:
        """Process a query using Claude and available tools"""
        messages_copy = copy.deepcopy(messages)

        response, available_tools = await self.send_request_to_antropic(messages_copy, include_tools)

        # Process response and handle tool calls
        final_text = []
        assistant_message_content = []
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                
                # Taking the first result content will only work if the tool returns a single result
                first_result_content = result.content[0].text
                is_json = first_result_content.startswith("{") and first_result_content.endswith("}") or first_result_content.startswith("[") and first_result_content.endswith("]")
                json_result = is_json and json.loads(first_result_content)
                if json_result:
                    return json_result
                else:
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                    assistant_message_content.append(content)
                    messages_copy.append(
                        {"role": "assistant", "content": assistant_message_content}
                    )
                    messages_copy.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": result.content,
                                }
                            ],
                        }
                    )

                    # Get next response from Claude
                    response = self.anthropic.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        messages=messages_copy,
                        tools=available_tools,
                    )

                    final_text.append(response.content[0].text)
        return "\n".join(final_text)

    async def send_request_to_antropic(self, messages_2, include_tools):
        available_tools = []
        if include_tools:
            response = await self.session.list_tools()
            # self.session.list_resources()
            # resource = await self.session.read_resource("greeting://anusha")
            available_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in response.tools
            ]
            # available_resources = [{
            #     "name": resource.name,
            #     "description": resource.description,
            #     "input_schema": resource.inputSchema,
            # } for resource in response_resources.resources]
            # available_tools.extend(available_resources)

            # Initial Claude API call

            response = self.anthropic.messages.create(
                model=MODEL,
                max_tokens=1000,
                messages=messages_2,
                tools=available_tools,
            )            
        return response, available_tools
    
    async def sampling_callback(self, context, params):
        print(context)
        print(params)
        
        lst_messages = []
        for message in params.messages:
            lst_messages.append({"role": message.role, "content": message.content.text})
        if lst_messages:
            model_response = self.anthropic.messages.create(
                    model=MODEL,
                    max_tokens=4000,
                    messages=lst_messages,
                )
            lst_cumulative_response = [content.text for content in model_response.content]
            str_final_response = "\n".join(lst_cumulative_response)
            response = ClientResult(CreateMessageResult(content=TextContent(text=str_final_response, type="text"), model=MODEL, role="assistant"))
        else:
            response = ClientResult(CreateMessageResult(content=TextContent(text="Something went wrong while processing the request", type="text"), model=MODEL, role="assistant"))
        return response
        
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_antropic_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

    

async def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python client.py <path_to_server_script>")
    #     sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_mcp_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


# if __name__ == "__main__":
#     asyncio.run(main())
