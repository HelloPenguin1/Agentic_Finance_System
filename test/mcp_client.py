import asyncio
import os
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

server_params = StdioServerParameters(
    command="python",
    args=["-m", "sec_edgar_mcp.server"],
    env={
        "SEC_EDGAR_USER_AGENT": os.getenv("SEC_EDGAR_USER_AGENT")
    }
)

#up until now Client only has launch instructions

async def main():
    async with stdio_client(server_params) as (read, write): #instantiate a connection pipe between server and me
        async with ClientSession(read, write) as session: #creates the MCP protocol layer

            await session.initialize()  #mcp handshake

        
            #mcp server exposes capabilites
            tools_response = await session.list_tools()  


            print("\nAvailable tools:")
            for tool in tools_response.tools:
                print(tool.name)
                print(tool.description)
                print(tool.inputSchema)
                print("-" * 50)
                
                

asyncio.run(main())

