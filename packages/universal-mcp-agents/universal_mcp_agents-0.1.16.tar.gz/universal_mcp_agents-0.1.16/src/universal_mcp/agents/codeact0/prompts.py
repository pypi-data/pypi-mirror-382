import inspect
import re
from collections.abc import Sequence

from langchain_core.tools import StructuredTool

from universal_mcp.agents.codeact0.utils import schema_to_signature

uneditable_prompt = """
You are **Wingmen**, an AI Assistant created by AgentR — a creative, straight-forward, and direct principal software engineer with access to tools.

## Responsibilities

- **Answer directly** if the task is simple (e.g. print, math, general knowledge).
- For any task requiring logic, execution, or data handling, use `execute_ipython_cell`.
- For writing or NLP tasks (summarizing, generating, extracting), always use AI functions via code — never respond directly.

## Tool vs. Function: Required Separation

You must clearly distinguish between tools (called via the tool calling API) and internal functions (used inside code blocks).

### Tools — Must Be Called via Tool Calling API

These must be called using **tool calling**, not from inside code blocks:

- `execute_ipython_cell` — For running any Python code or logic.
- `search_functions` — To discover available functions for a task.
- `load_functions` — To load a specific function by full ID.

**Do not attempt to call these inside `python` code.**
Use tool calling syntax for these operations.

### Functions — Must Be Used Inside Code Blocks

All other functions, including LLM functions, must always be used within code executed by `execute_ipython_cell`. These include:

- `smart_print()` — For inspecting unknown data structures before looping.
- `asyncio.run()` — For wrapping and executing asynchronous logic. You must not use await outside an async function. And the async function must be called by `asyncio.run()`.
- Any functions for applications loaded via `load_functions`.
- Any logic, data handling, writing, NLP, generation, summarization, or extraction functionality of LLMs.

These must be called **inside a Python code block**, and that block must be executed using `execute_ipython_cell`.

## Tool/Function Usage Policy

1. **Always Use Tools/Functions for Required Tasks**
   Any searching, loading, or executing must be done using a tool/function call. Never answer manually if a tool/function is appropriate.

2. **Use Existing Functions First**
   Use existing functions if available. Otherwise, use `search_functions` with a concise query describing the task.

3. **Load Only Relevant Tools**
   When calling `load_functions`, include only relevant function IDs.
   - Prefer connected applications over unconnected ones.
   - If multiple functions match (i.e. if none are connected, or multiple are connected), ask the user to choose.
   - After loading a tool, you do not need to import/declare it again. It can be called directly in further cells.

4. **Follow First Turn Process Strictly**
   On the **first turn**, do only **one** of the following:
   - Handle directly (if trivial)
   - Use a tool/function (`execute_ipython_cell`, `search_functions`, etc.)

   **Do not extend the conversation on the first message.**

## Coding Rules

- Use `smart_print()` to inspect unknown structures, especially those received from function outputs, before looping or branching.
- Validate logic with a single item before processing lists or large inputs.
- Try to achieve as much as possible in a single code block.
- Use only pre-installed Python libraries. Do import them once before using.
- Outer level functions, variables, classes, and imports declared previously can be used in later cells.
- For all functions, call using keyword arguments only. DO NOT use any positional arguments.

### **Async Function Usage — Critical**

When calling asynchronous functions:
- You must define or use an **inner async function**.
- Use `await` only **inside** that async function.
- Run it using `asyncio.run(<function_name>())` **without** `await` at the outer level.

**Wrong - Using `await` outside an async function**
```
result = await some_async_function()
```
**Wrong  - Attaching await before asyncio.run**.
`await asyncio.run(main())`
These will raise SyntaxError: 'await' outside async function
The correct method is the following-
```
import asyncio
async def some_async_function():
    ...

async def main():
    result = await some_async_function()
    print(result)

asyncio.run(main())
#or
result = asyncio.run(some_async_function(arg1 = <arg1>))
```
## Output Formatting
- All code results must be returned in **Markdown**.
- The user cannot see raw output, so format results clearly:
    - Use tables for structured data.
    - Provide links for files or images.
    - Be explicit in formatting to ensure readability.
"""


def make_safe_function_name(name: str) -> str:
    """Convert a tool name to a valid Python function name."""
    # Replace non-alphanumeric characters with underscores
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Ensure the name doesn't start with a digit
    if safe_name and safe_name[0].isdigit():
        safe_name = f"tool_{safe_name}"
    # Handle empty name edge case
    if not safe_name:
        safe_name = "unnamed_tool"
    return safe_name


def dedent(text):
    """Remove any common leading whitespace from every line in `text`.

    This can be used to make triple-quoted strings line up with the left
    edge of the display, while still presenting them in the source code
    in indented form.

    Note that tabs and spaces are both treated as whitespace, but they
    are not equal: the lines "  hello" and "\\thello" are
    considered to have no common leading whitespace.

    Entirely blank lines are normalized to a newline character.
    """
    # Look for the longest leading string of spaces and tabs common to
    # all lines.
    margin = None
    _whitespace_only_re = re.compile("^[ \t]+$", re.MULTILINE)
    _leading_whitespace_re = re.compile("(^[ \t]*)(?:[^ \t\n])", re.MULTILINE)
    text = _whitespace_only_re.sub("", text)
    indents = _leading_whitespace_re.findall(text)
    for indent in indents:
        if margin is None:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner is still on top).
        elif indent.startswith(margin):
            pass

        # Current line consistent with and no deeper than previous winner:
        # it's the new winner.
        elif margin.startswith(indent):
            margin = indent

        # Find the largest common whitespace between current line and previous
        # winner.
        else:
            for i, (x, y) in enumerate(zip(margin, indent)):
                if x != y:
                    margin = margin[:i]
                    break

    # sanity check (testing/debugging only)
    if 0 and margin:
        for line in text.split("\n"):
            assert not line or line.startswith(margin), f"line = {line!r}, margin = {margin!r}"

    if margin:
        text = re.sub(r"(?m)^" + margin, "", text)
    return text


def indent(text, prefix, predicate=None):
    """Adds 'prefix' to the beginning of selected lines in 'text'.

    If 'predicate' is provided, 'prefix' will only be added to the lines
    where 'predicate(line)' is True. If 'predicate' is not provided,
    it will default to adding 'prefix' to all non-empty lines that do not
    consist solely of whitespace characters.
    """
    if predicate is None:
        # str.splitlines(True) doesn't produce empty string.
        #  ''.splitlines(True) => []
        #  'foo\n'.splitlines(True) => ['foo\n']
        # So we can use just `not s.isspace()` here.
        def predicate(s):
            return not s.isspace()

    prefixed_lines = []
    for line in text.splitlines(True):
        if predicate(line):
            prefixed_lines.append(prefix)
        prefixed_lines.append(line)

    return "".join(prefixed_lines)


def create_default_prompt(
    tools: Sequence[StructuredTool],
    additional_tools: Sequence[StructuredTool],
    base_prompt: str | None = None,
):
    system_prompt = uneditable_prompt.strip() + (
        "\n\nIn addition to the Python Standard Library, you can use the following external functions:\n"
    )
    tools_context = {}
    for tool in tools:
        if hasattr(tool, "func") and tool.func is not None:
            tool_callable = tool.func
            is_async = False
        elif hasattr(tool, "coroutine") and tool.coroutine is not None:
            tool_callable = tool.coroutine
            is_async = True
        system_prompt += f'''{"async " if is_async else ""}{schema_to_signature(tool.args, tool.name)}:
    """{tool.description}"""
    ...
    '''
        safe_name = make_safe_function_name(tool.name)
        tools_context[safe_name] = tool_callable

    for tool in additional_tools:
        if hasattr(tool, "func") and tool.func is not None:
            tool_callable = tool.func
            is_async = False
        elif hasattr(tool, "coroutine") and tool.coroutine is not None:
            tool_callable = tool.coroutine
            is_async = True
        system_prompt += f'''{"async " if is_async else ""}def {tool.name} {str(inspect.signature(tool_callable))}:
    """{tool.description}"""
    ...
    '''
        safe_name = make_safe_function_name(tool.name)
        tools_context[safe_name] = tool_callable

    if base_prompt and base_prompt.strip():
        system_prompt += f"Your goal is to perform the following task:\n\n{base_prompt}"

    return system_prompt, tools_context
