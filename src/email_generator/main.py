import asyncio

from .graph import graph


async def main():

    print("\n=== Professional Email Generator ===\n")

    tone = input("Enter the email tone: ").strip()

    context = input("Enter the email context: ").strip()

    print("\nEnter data points one by one.")
    print("Type 'done' when finished.\n")

    data_points = []

    while True:
        data_point = input("Data point: ").strip()

        if data_point.lower() == "done":
            break

        if data_point:
            data_points.append(data_point)

    result = await graph.ainvoke(
        {
            "tone": tone,
            "context": context,
            "data_points": data_points,

            "mcp_guidelines": "",
            "prompt": "",
            "subject": "",
            "email": "",
            "error": "",
        }
    )

    if result.get("error"):
        print("\n❌ Input Error:")
        print(result["error"])
        return

    print("\n" + "=" * 60)
    print("GENERATED EMAIL")
    print("=" * 60)

    print("\nSubject:")
    print(result["subject"])

    print("\nEmail:")
    print(result["email"])

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())