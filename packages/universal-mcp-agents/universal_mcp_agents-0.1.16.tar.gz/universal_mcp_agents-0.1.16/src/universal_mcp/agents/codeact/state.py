from langgraph.graph import MessagesState
from pydantic import Field


class CodeActState(MessagesState):
    """State for CodeAct agent."""

    script: str | None = Field(default=None, description="The Python code script to be executed.")
    sandbox_output: str | None = Field(default=None, description="The output of the Python code script execution.")
    syntax_error: str | None = Field(default=None, description="The syntax error from the last script validation.")
    task_complete: bool = Field(default=False, description="Whether the task is complete.")
