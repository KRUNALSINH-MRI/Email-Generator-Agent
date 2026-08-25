from typing import TypedDict

from pydantic import BaseModel, Field


class EmailState(TypedDict):
    tone: str
    context: str
    data_points: list[str]

    mcp_guidelines: str

    prompt: str

    subject: str
    email: str

    error: str


class EmailOutput(BaseModel):
    subject: str = Field(
        description="A concise and professional email subject line."
    )

    email: str = Field(
        description="The complete professional email body."
    )