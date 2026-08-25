import asyncio

from fastmcp import Client


async def main():

    client = Client("http://localhost:8000/mcp")

    async with client:

        result = await client.call_tool(
            "get_email_guidelines",
            {
                "tone": "empathetic"
            }
        )

        print("\nMCP HTTP TOOL RESULT:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())