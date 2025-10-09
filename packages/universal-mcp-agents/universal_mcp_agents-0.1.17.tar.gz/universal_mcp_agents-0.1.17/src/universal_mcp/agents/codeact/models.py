from typing import Any

from pydantic import BaseModel


class SandboxOutput(BaseModel):
    """Structured output from the code sandbox."""

    stdout: str
    error: str | None = None
    return_value: Any | None = None
