from langgraph.graph import StateGraph, START, END

from .state import EmailState, EmailOutput
from .llm import llm
from .prompts import EMAIL_GENERATOR_PROMPT
from .mcp_client import get_mcp_client


def validate_input(state: EmailState):
    """
    Validate that all required user inputs are present.
    """

    missing = []

    if not state.get("tone", "").strip():
        missing.append("tone")

    if not state.get("context", "").strip():
        missing.append("context")

    if not state.get("data_points"):
        missing.append("data_points")

    if missing:
        questions = {
            "tone": "What tone would you like for the email? (e.g., formal, friendly, empathetic, assertive)",
            "context": "Could you provide the context or purpose of this email?",
            "data_points": "What are the key data points or facts to include in the email?",
        }
        parts = [questions[f] for f in missing]
        return {
            "error": "I need a bit more information to generate your email: " + " | ".join(parts)
        }

    return {
        "error": ""
    }


def validation_router(state: EmailState):
    """
    Decide whether the graph should continue
    or stop because of invalid input.
    """

    if state.get("error"):
        return "error"

    return "continue"


async def get_mcp_guidelines(state: EmailState):
    """
    Get tone-specific writing guidelines from the MCP server.
    """

    client = get_mcp_client()

    async with client:

        result = await client.call_tool(
            "get_email_guidelines",
            {
                "tone": state["tone"]
            }
        )

    return {
        "mcp_guidelines": result.content[0].text
    }


def build_prompt(state: EmailState):
    """
    Build the dynamic prompt using user input
    and MCP-provided guidelines.
    """

    data_points = "\n".join(
        f"- {item}"
        for item in state["data_points"]
    )

    prompt = EMAIL_GENERATOR_PROMPT.format(
        tone=state["tone"],
        context=state["context"],
        data_points=data_points,
        mcp_guidelines=state["mcp_guidelines"],
    )

    return {
        "prompt": prompt
    }


def generate_email(state: EmailState):
    """
    Generate a structured email using the LLM.
    """

    structured_llm = llm.with_structured_output(
        EmailOutput
    )

    response = structured_llm.invoke(
        state["prompt"]
    )

    return {
        "subject": response.subject,
        "email": response.email
    }


builder = StateGraph(EmailState)


builder.add_node(
    "validate_input",
    validate_input
)

builder.add_node(
    "get_mcp_guidelines",
    get_mcp_guidelines
)

builder.add_node(
    "build_prompt",
    build_prompt
)

builder.add_node(
    "generate_email",
    generate_email
)


builder.add_edge(
    START,
    "validate_input"
)

builder.add_conditional_edges(
    "validate_input",
    validation_router,
    {
        "continue": "get_mcp_guidelines",
        "error": END
    }
)

builder.add_edge(
    "get_mcp_guidelines",
    "build_prompt"
)

builder.add_edge(
    "build_prompt",
    "generate_email"
)

builder.add_edge(
    "generate_email",
    END
)


graph = builder.compile()