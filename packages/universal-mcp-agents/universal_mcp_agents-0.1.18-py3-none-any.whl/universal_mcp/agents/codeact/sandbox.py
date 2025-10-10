import asyncio
import contextlib
import io
from collections.abc import Callable
from typing import Any

from loguru import logger

from .models import SandboxOutput

# Define a whitelist of safe built-in functions
SAFE_BUILTINS = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "callable": callable,
    "chr": chr,
    "dict": dict,
    "divmod": divmod,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "getattr": getattr,
    "hasattr": hasattr,
    "hash": hash,
    "id": id,
    "int": int,
    "isinstance": isinstance,
    "iter": iter,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "next": next,
    "ord": ord,
    "pow": pow,
    "print": print,
    "range": range,
    "repr": repr,
    "reversed": reversed,
    "round": round,
    "set": set,
    "slice": slice,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "type": type,
    "zip": zip,
}


async def eval_unsafe(
    code: str, _locals: dict[str, Callable], timeout: int = 10
) -> tuple[SandboxOutput, dict[str, Any]]:
    """Executes a string of Python code in a sandboxed environment."""
    original_keys = set(_locals.keys())
    execution_context = _locals.copy()
    execution_context["__builtins__"] = __builtins__  # TODO: Use SAFE_BUILTINS instead of __builtins__

    stdout_capture = io.StringIO()
    output = SandboxOutput(stdout="")

    try:
        logger.debug(f"Executing code with timeout {timeout}")
        with contextlib.redirect_stdout(stdout_capture):
            exec(code, execution_context)

            if "main" in execution_context and asyncio.iscoroutinefunction(execution_context["main"]):
                return_val = await asyncio.wait_for(execution_context["main"](), timeout=timeout)
                output.return_value = return_val
            else:
                output.error = "No `async def main()` function found in the script."

        output.stdout = stdout_capture.getvalue()

    except Exception as e:
        output.error = f"{type(e).__name__}: {e}"
        output.stdout = stdout_capture.getvalue()

    new_keys = set(execution_context.keys()) - original_keys - {"__builtins__"}
    new_vars = {key: execution_context[key] for key in new_keys}

    return output, new_vars
