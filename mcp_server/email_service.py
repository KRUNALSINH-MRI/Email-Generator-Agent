from email_generator.graph import graph


async def generate_email(
    tone: str,
    context: str,
    data_points: list[str],
) -> dict:
    """
    Generate a professional email using the existing
    Email Generator LangGraph.
    """

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
        return {
            "subject": "",
            "email": "",
            "error": result["error"],
        }

    return {
        "subject": result.get("subject", ""),
        "email": result.get("email", ""),
        "error": "",
    }