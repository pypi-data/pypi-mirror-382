import ast
from collections.abc import Callable

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field
from universal_mcp.logger import logger
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.codeact.models import SandboxOutput
from universal_mcp.agents.codeact.prompts import (
    create_default_prompt,
    make_safe_function_name,
)
from universal_mcp.agents.codeact.sandbox import eval_unsafe
from universal_mcp.agents.codeact.state import CodeActState
from universal_mcp.agents.llm import load_chat_model


class StructuredCodeResponse(BaseModel):
    """Structured response for the CodeAct agent."""

    reasoning: str = Field(..., description="The reasoning behind the generated script.")
    script: str | None = Field(default=None, description="The Python script to be executed.")
    task_complete: bool = Field(..., description="Whether the task is complete.")


class CodeActAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str,
        memory: BaseCheckpointSaver | None = None,
        tools: ToolConfig | None = None,
        registry: ToolRegistry | None = None,
        sandbox_timeout: int = 20,
        **kwargs,
    ):
        super().__init__(
            name=name,
            instructions=instructions,
            model=model,
            memory=memory,
            **kwargs,
        )
        self.model_instance = load_chat_model(model)
        self.tools_config = tools or {}
        self.registry = registry
        self.eval_fn = eval_unsafe
        self.sandbox_timeout = sandbox_timeout
        self.processed_tools: dict[str, Callable] = {}

    async def _build_graph(self):
        if self.tools_config:
            if not self.registry:
                raise ValueError("Tools are configured but no registry is provided")
            # Load native tools, these are python functions
            exported_tools = await self.registry.export_tools(self.tools_config, ToolFormat.NATIVE)
            for tool in exported_tools:
                name = tool.__name__
                safe_name = make_safe_function_name(name)
                if name != safe_name:
                    logger.warning(f"Tool name {name} is not safe, using {safe_name} instead")
                    raise ValueError(f"Tool name {name} is not safe, using {safe_name} instead")
                self.processed_tools[safe_name] = tool

        self.instructions = create_default_prompt(self.processed_tools, self.instructions)

        agent = StateGraph(CodeActState)
        agent.add_node("call_model", self.call_model)
        agent.add_node("validate_code", self.validate_code)
        agent.add_node("sandbox", self.sandbox)
        agent.add_node("final_answer", self.final_answer)

        agent.add_edge(START, "call_model")

        return agent.compile(checkpointer=self.memory)

    async def call_model(self, state: CodeActState) -> Command:
        logger.debug(f"Calling model with state: {state}")
        model = self.model_instance.with_structured_output(StructuredCodeResponse)

        # Find the last script and its output in the message history
        previous_script = state.get("script", "")
        sandbox_output = state.get("sandbox_output", "")
        syntax_error = state.get("syntax_error", "")

        logger.debug(f"Previous script:\n {previous_script}")
        logger.debug(f"Sandbox output:\n {sandbox_output}")
        logger.debug(f"Syntax error:\n {syntax_error}")

        prompt_messages = [
            {"role": "system", "content": self.instructions},
            *state["messages"],
        ]
        if previous_script:
            feedback_message = (
                f"Here is the script you generated in the last turn:\n\n```python\n{previous_script}\n```\n\n"
            )
            if syntax_error:
                feedback_message += (
                    f"When parsing the script, it produced the following syntax error:\n\n```\n{syntax_error}\n```\n\n"
                    "Please fix the syntax and generate a new, correct script."
                )
            elif sandbox_output:
                feedback_message += (
                    f"When executed, it produced the following output:\n\n```\n{sandbox_output}\n```\n\n"
                )
                feedback_message += "Based on this output, decide if the task is complete. If it is, respond the final answer to the user in clean and readable Markdown format. Important: set `task_complete` to `True` and no need to provide script. If the task is not complete, generate a new script to get closer to the solution."

            prompt_messages.append({"role": "user", "content": feedback_message})

        response: StructuredCodeResponse = await model.ainvoke(prompt_messages)

        # We add the reasoning as the AI message content
        ai_message = AIMessage(content=response.reasoning)

        if response.task_complete:
            return Command(
                goto="final_answer",
                update={
                    "messages": [ai_message],
                    "script": response.script,
                    "task_complete": response.task_complete,
                    "sandbox_output": sandbox_output,
                    "syntax_error": None,
                },
            )
        else:
            return Command(
                goto="validate_code",
                update={
                    "messages": [ai_message],
                    "script": response.script,
                    "task_complete": response.task_complete,
                    "sandbox_output": None,
                    "syntax_error": None,
                },
            )

    async def validate_code(self, state: CodeActState) -> Command:
        logger.debug(f"Validating code with script:\n {state['script']}")
        script = state.get("script")

        if not script:
            return Command(
                goto="call_model",
                update={
                    "syntax_error": "Model did not provide a script but task is not complete. Please provide a script or set task_complete to True."
                },
            )

        try:
            ast.parse(script)
            logger.debug("AST parsing successful.")
            return Command(
                goto="sandbox",
                update={
                    "syntax_error": None,
                },
            )
        except SyntaxError as e:
            logger.warning(f"AST parsing failed: {e}")
            return Command(
                goto="call_model",
                update={
                    "syntax_error": f"Syntax Error: {e}",
                },
            )

    async def sandbox(self, state: CodeActState) -> Command:
        logger.debug(f"Running sandbox with script:\n {state['script']}")
        tools_context = {}
        for tool_name, tool_callable in self.processed_tools.items():
            tools_context[tool_name] = tool_callable

        output: SandboxOutput
        output, _ = await self.eval_fn(state["script"], tools_context, self.sandbox_timeout)

        # Format the output for the agent
        formatted_output = "Code executed.\n\n"
        MAX_OUTPUT_LEN = 20000  # Maximum number of characters to show for stdout/stderr

        def truncate_output(text, max_len=MAX_OUTPUT_LEN):
            if text is None:
                return ""
            text = text.strip()
            if len(text) > max_len:
                return text[:max_len] + "\n... (more output hidden)"
            return text

        if output.stdout:
            truncated_stdout = truncate_output(output.stdout)
            formatted_output += f"STDOUT:\n```\n{truncated_stdout}\n```\n\n"
        if output.error:
            truncated_stderr = truncate_output(output.error)
            formatted_output += f"STDERR / ERROR:\n```\n{truncated_stderr}\n```\n"
        if output.return_value is not None:
            formatted_output += f"RETURN VALUE:\n```\n{repr(output.return_value)}\n```\n"

        logger.debug(f"Sandbox output: {formatted_output}")
        return Command(
            goto="call_model",
            update={"sandbox_output": formatted_output.strip()},
        )

    async def final_answer(self, state: CodeActState) -> Command:
        logger.debug("Formatting final answer using LLM for markdown formatting.")

        # Extract the original user prompt
        user_prompt = ""
        for msg in state["messages"]:
            if isinstance(msg, HumanMessage):
                user_prompt = msg.content
                break

        # Compose a prompt for the LLM to generate a concise, markdown-formatted answer
        llm_prompt = (
            "Given the following task and answer, write a concise, well-formatted markdown response suitable for a user.\n\n"
            f"Task:\n{user_prompt}\n\n"
            f"Answer:\n{state['sandbox_output']}\n\n"
            "Respond only with the markdown-formatted answer."
        )

        # Use the model to generate the final formatted answer
        response = await self.model_instance.ainvoke([{"role": "user", "content": llm_prompt}])
        markdown_answer = response.content if hasattr(response, "content") else str(response)
        logger.debug(f"Final answer:\n {markdown_answer}")

        return Command(
            goto=END,
            update={
                "messages": [AIMessage(content=markdown_answer)],
            },
        )
