import json
from pathlib import Path

import uvicorn
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from mcp_server.email_service import generate_email as run_agent


mcp = FastMCP("Email Generator Server")


@mcp.tool()
def get_email_guidelines(tone: str) -> str:
    """Return professional email-writing guidelines for the requested tone."""
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
        "Use clear, professional, respectful, and concise language.",
    )


@mcp.tool()
async def generate_email(
    tone: str,
    context: str,
    data_points: list[str],
) -> dict:
    """Generate a professional email using the Email Generator Agent."""
    return await run_agent(tone=tone, context=context, data_points=data_points)


@mcp.tool()
async def approve_email(subject: str, email: str) -> str:
    """Approve and send the generated email."""
    return "Email has been sent."


@mcp.tool()
async def reject_email(subject: str, email: str) -> str:
    """Reject the generated email."""
    return "Email has been rejected."


@mcp.resource("ui://email-generator/app.html", mime_type="text/html")
def email_generator_ui() -> str:
    """Serve the Email Generator MCP App UI."""
    ui_path = Path(__file__).parent / "ui" / "dist" / "index.html"
    return ui_path.read_text(encoding="utf-8")


# --- REST bridge: React UI calls these, which invoke MCP tools ---

async def _call_tool(name: str, arguments: dict) -> dict:
    """Call an MCP tool by name and return the parsed result."""
    result = await mcp.call_tool(name, arguments)
    if result.structured_content:
        return result.structured_content
    if result.content:
        text = result.content[0].text
        try:
            return json.loads(text)
        except (json.JSONDecodeError, AttributeError):
            return {"message": text}
    return {}


async def handle_generate_email(request: Request):
    body = await request.json()
    try:
        result = await _call_tool(
            "generate_email",
            {
                "tone": body["tone"],
                "context": body["context"],
                "data_points": body["data_points"],
            },
        )
    except Exception as e:
        return JSONResponse(
            {"subject": "", "email": "", "error": str(e)},
            status_code=500,
        )
    return JSONResponse(result)


async def handle_approve_email(request: Request):
    body = await request.json()
    result = await _call_tool(
        "approve_email",
        {"subject": body["subject"], "email": body["email"]},
    )
    return JSONResponse(result)


async def handle_reject_email(request: Request):
    body = await request.json()
    result = await _call_tool(
        "reject_email",
        {"subject": body["subject"], "email": body["email"]},
    )
    return JSONResponse(result)


ui_dir = Path(__file__).parent / "ui" / "dist"

app = Starlette(
    routes=[
        Route("/api/generate-email", handle_generate_email, methods=["POST"]),
        Route("/api/approve-email", handle_approve_email, methods=["POST"]),
        Route("/api/reject-email", handle_reject_email, methods=["POST"]),
        Mount("/", app=StaticFiles(directory=str(ui_dir), html=True)),
    ],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)