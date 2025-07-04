import json
import copy
import os
import asyncio
from typing import Optional, List, Dict
from contextlib import AsyncExitStack

from mcp.types import TextContent, ClientResult, CreateMessageResult
from mcp import ClientSession, StdioServerParameters, CreateMessageResult
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env
SERVER_SCRIPT_PATH = os.getenv("SERVER_SCRIPT_PATH")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")
MODEL = os.getenv("MODEL")

class MCPClient:
    def __init__(self, PF_loginCert = None):
        self.PF_loginCert = PF_loginCert
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    # methods will go here

    async def connect_to_mcp_server_stdio_transport(self):
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

    async def connect_to_mcp_server_streamable_http_transport(self):
        """Connect to an MCP serve
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        steamable_http_transport = await self.exit_stack.enter_async_context(
            streamablehttp_client(url=f"{MCP_SERVER_URL}/mcp", terminate_on_close=False)
        )
        receive_stream, send_stream, _ = steamable_http_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(receive_stream, send_stream, sampling_callback=self.sampling_callback)
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
    
    async def get_available_tools(self):
        response = await self.session.list_tools()
        tools = response.tools
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in tools
        ]

    async def process_antropic_query(self, messages) -> str:
        """Process a query using Claude and available tools"""
        messages_copy = copy.deepcopy(messages)
        available_tools = await self.get_available_tools()
        response = await self.send_request_to_antropic(messages_copy, available_tools)

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
                tool_args["PF_loginCert"] = self.PF_loginCert


                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                
                # Taking the first result content will only work if the tool returns a single result
                first_result_content = result.content[0].text
                is_json = self.is_string_json(first_result_content)
                if is_json:
                    return json.loads(first_result_content)
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
                    response = await self.send_request_to_antropic(messages_copy, available_tools)
                    final_text.append(response.content[0].text)
        return "\n".join(final_text)

    async def send_request_to_antropic(self, messages, available_tools: List[Dict[str, str]]=None):
        if available_tools:
            # Initial Claude API call
            response = self.anthropic.messages.create(
                model=MODEL,
                max_tokens=1000,
                messages=messages,
                tools=available_tools,
            )
        else:
            response = self.anthropic.messages.create(
                model=MODEL,
                max_tokens=1000,
                messages=messages,
            )
        return response
    
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

    @staticmethod
    def is_string_json(json_str: str) -> bool:
        return (json_str.startswith("{") and json_str.endswith("}")) or (json_str.startswith("[") and json_str.endswith("]"))

    

async def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python client.py <path_to_server_script>")
    #     sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_mcp_server_streamable_http_transport()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
