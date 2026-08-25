import asyncio

from email_generator.mcp_client import get_mcp_client


async def main():

    client = get_mcp_client()

    async with client:

        result = await client.call_tool(
            "get_email_guidelines",
            {
                "tone": "empathetic"
            }
        )

        print("\nMCP TOOL RESULT:")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())