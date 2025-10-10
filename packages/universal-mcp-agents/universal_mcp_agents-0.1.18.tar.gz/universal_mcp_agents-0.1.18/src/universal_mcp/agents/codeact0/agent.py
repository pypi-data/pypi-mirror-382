import inspect
from collections.abc import Callable
from typing import Literal, cast

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langchain_core.tools import tool as create_tool
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import START, StateGraph
from langgraph.types import Command, RetryPolicy
from universal_mcp.tools.registry import ToolRegistry
from universal_mcp.types import ToolConfig, ToolFormat

from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.codeact0.llm_tool import ai_classify, call_llm, data_extractor, smart_print
from universal_mcp.agents.codeact0.prompts import (
    create_default_prompt,
)
from universal_mcp.agents.codeact0.sandbox import eval_unsafe, execute_ipython_cell
from universal_mcp.agents.codeact0.state import CodeActState
from universal_mcp.agents.codeact0.utils import inject_context, smart_truncate
from universal_mcp.agents.llm import load_chat_model
from universal_mcp.agents.utils import filter_retry_on


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
        self.model_instance = load_chat_model(model, thinking=True)
        self.tools_config = tools or {}
        self.registry = registry
        self.eval_fn = eval_unsafe
        self.sandbox_timeout = sandbox_timeout
        self.processed_tools: list[StructuredTool | Callable] = []

        # TODO(manoj): Use toolformat native instead of langchain
        # TODO(manoj, later): Add better sandboxing
        # Old Nishant TODO s:
        # - Make codeact faster by calling upto API call (this done but should be tested)
        # - Add support for async eval_fn
        # - Throw Error if code snippet is too long (> 1000 characters) and suggest to split it into smaller parts
        # - Multiple models from config

    async def _build_graph(self):
        exported_tools = []
        if self.tools_config:
            if not self.registry:
                raise ValueError("Tools are configured but no registry is provided")
            # Langchain tools are fine
            exported_tools = await self.registry.export_tools(self.tools_config, ToolFormat.LANGCHAIN)
        additional_tools = [smart_print, data_extractor, ai_classify, call_llm]
        additional_tools = [t if isinstance(t, StructuredTool) else create_tool(t) for t in additional_tools]
        self.instructions, self.tools_context = create_default_prompt(
            exported_tools, additional_tools, self.instructions
        )

        def call_model(state: CodeActState) -> Command[Literal["sandbox"]]:
            messages = [{"role": "system", "content": self.instructions}] + state["messages"]

            # Run the model and potentially loop for reflection
            model_with_tools = self.model_instance.bind_tools(tools=[execute_ipython_cell], tool_choice="auto")
            response = cast(AIMessage, model_with_tools.invoke(messages))

            if response.tool_calls:
                if len(response.tool_calls) > 1:
                    raise Exception("Not possible in Claude with llm.bind_tools(tools=tools, tool_choice='auto')")
                if response.tool_calls[0]["name"] != "execute_ipython_cell":
                    raise Exception(
                        f"Unexpected tool call: {response.tool_calls[0]['name']}. Expected 'execute_ipython_cell'."
                    )
                if (
                    response.tool_calls[0]["args"].get("snippet") is None
                    or not response.tool_calls[0]["args"]["snippet"].strip()
                ):
                    raise Exception("Tool call 'execute_ipython_cell' requires a non-empty 'snippet' argument.")
                return Command(goto="sandbox", update={"messages": [response]})
            else:
                return Command(update={"messages": [response]})

        # If eval_fn is a async, we define async node function.
        if inspect.iscoroutinefunction(self.eval_fn):
            raise ValueError("eval_fn must be a synchronous function, not a coroutine.")
            # async def sandbox(state: StateSchema):
            #     existing_context = state.get("context", {})
            #     context = {**existing_context, **tools_context}
            #     # Execute the script in the sandbox
            #     output, new_vars = await eval_fn(state["script"], context)
            #     new_context = {**existing_context, **new_vars}
            #     return {
            #         "messages": [{"role": "user", "content": output}],
            #         "context": new_context,
            #     }
        else:

            def sandbox(state: CodeActState) -> Command[Literal["call_model"]]:
                tool_call = state["messages"][-1].tool_calls[0]  # type: ignore
                code = tool_call["args"]["snippet"]
                previous_add_context = state.get("add_context", {})
                add_context = inject_context(previous_add_context, self.tools_context)
                existing_context = state.get("context", {})
                context = {**existing_context, **add_context}
                # Execute the script in the sandbox

                output, new_context, new_add_context = self.eval_fn(
                    code, context, previous_add_context, 180
                )  # default timeout 3 min
                output = smart_truncate(output)

                return Command(
                    goto="call_model",
                    update={
                        "messages": [
                            ToolMessage(
                                content=output,
                                name=tool_call["name"],
                                tool_call_id=tool_call["id"],
                            )
                        ],
                        "context": new_context,
                        "add_context": new_add_context,
                    },
                )

        agent = StateGraph(state_schema=CodeActState)
        agent.add_node(call_model, retry_policy=RetryPolicy(max_attempts=3, retry_on=filter_retry_on))
        agent.add_node(sandbox)
        agent.add_edge(START, "call_model")
        return agent.compile(checkpointer=self.memory)
