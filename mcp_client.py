import asyncio
from mcp.client.stdio import StdioServer
from mcp.client.session import ClientSession

async def main():
    server = await StdioServer.from_command(["python","mcp_server.py"])
    async with server:
        async with ClientSession(server) as s:
            tools = await s.list_tools()
            print("TOOLS:", [t.name for t in tools])
            res = await s.call_tool("sumar", {"x":2,"y":3})
            print("RESULT:", res.content[0].text)

asyncio.run(main())
