import inspect
import re
from collections.abc import Callable


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


def create_default_prompt(
    tools: dict[str, Callable],
    base_prompt: str | None = None,
):
    """Create default prompt for the CodeAct agent."""
    prompt = f"{base_prompt}\n\n" if base_prompt else ""
    prompt += """You are a Python programmer. You will be given a task to perform.
Your goal is to write a self-contained Python script to accomplish the task.

In each turn, you will generate a complete Python script. The script will be executed in a fresh, stateless environment.
You will be given the previous script you generated and the output it produced.
Your task is to analyze the output to find errors or opportunities for improvement, and then generate a new, improved script.
You must take the previous script as a starting point and replace it with a new one that moves closer to the final solution.
Your final script must be a single, complete piece of code that can be executed independently.

The script must follow this structure:
1. All necessary imports at the top.
2. An `async def main():` function containing the core logic.
3. Do NOT include any code outside of the `async def main()` function, and do NOT call it. The execution environment handles this.

Any output you want to see from the code should be printed to the console from within the `main` function.
Code should be output in a fenced code block (e.g. ```python ... ```).

If you need to ask for more information or provide the final answer, you can output text to be shown directly to the user.

In addition to the Python Standard Library, you can use the following functions:"""

    for tool_name, tool_callable in tools.items():
        # Determine if it's an async function
        is_async = inspect.iscoroutinefunction(tool_callable)
        # Add appropriate function definition
        prompt += f'''\n{"async " if is_async else ""}def {tool_name}{str(inspect.signature(tool_callable))}:
    """{tool_callable.__doc__}"""
    ...
'''

    prompt += """\n\n\nAlways use print() statements to explore data structures and function outputs. Simply returning values will not display them back to you for inspection. For example, use print(result) instead of just 'result'.

As you don't know the output schema of the additional Python functions you have access to, start from exploring their contents before building a final solution.

IMPORTANT CODING STRATEGY:
1. All your code must be inside an `async def main()` function.
2. Do NOT import `asyncio` or call `main()`. The execution environment handles this.
3. Since many of the provided tools are async, you must use `await` to call them from within `main()`.
4. Write code up to the point where you make an API call/tool usage with an output.
5. Print the type/shape and a sample entry of this output, and using that knowledge proceed to write the further code.
6. The maximum number of characters that can be printed is 5000. Remove any unnecessary print statements.

This means:
- Write code that makes the API call or tool usage
- Print the result with type information: print(f"Type: {type(result)}")
- Print the shape/structure: print(f"Shape/Keys: {result.keys() if isinstance(result, dict) else len(result) if isinstance(result, (list, tuple)) else 'N/A'}")
- Print a sample entry: print(f"Sample: {result[0] if isinstance(result, (list, tuple)) and len(result) > 0 else result}")
- Then, based on this knowledge, write the code to process/use this data

Reminder: use Python code snippets to call tools

When you have completely finished the task, present the final result from your script to the user in a clean and readable Markdown format. Do not just summarize what you did; provide the actual output. For example, if you were asked to find unsubscribe links and your script found them, your final response should be a Markdown-formatted list of those links.


Important:
After you have provided the final output, you MUST set `task_complete` to `True` in your response.
"""
    return prompt
