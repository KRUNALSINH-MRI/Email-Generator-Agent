from fastmcp import FastMCP


mcp = FastMCP("Email Guidelines Server")


@mcp.tool()
def get_email_guidelines(tone: str) -> str:
    """
    Return professional email-writing guidelines
    for the requested tone.
    """

    guidelines = {
        "formal": (
            "Use professional language, clear structure, "
            "and avoid casual expressions."
        ),

        "empathetic": (
            "Acknowledge the recipient's concerns, "
            "show understanding, and use reassuring language."
        ),

        "assertive": (
            "Use direct and confident language. "
            "Clearly communicate the requested action "
            "without sounding aggressive."
        ),

        "friendly": (
            "Use warm, approachable and conversational "
            "professional language."
        ),
    }

    return guidelines.get(
        tone.lower(),
        (
            "Use clear, professional, respectful, "
            "and concise language."
        )
    )


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
    )