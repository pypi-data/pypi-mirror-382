# Design Decisions and Learnings

This section documents the key architectural decisions and learnings guiding the evolution of the `UnifiedAgent`. It will be updated continuously as the project progresses.

## Core Design Shift: Embracing a Hybrid, Code-Centric Architecture

Our primary design decision is to evolve the `UnifiedAgent` from a rigid, structured tool-calling system into a powerful hybrid agent. This new architecture combines the dynamic tool management of the original `UnifiedAgent` with the expressive, direct code execution model pioneered by `smolagents`.

### Clarification: `execute_ipython_cell` vs. Direct Code Execution

It's important to clarify the distinction between the current `execute_ipython_cell` tool and the proposed direct code execution model. Both execute code, but the architectural difference is profound:

-   **Current Model (Structured Call):** The LLM's native output is a structured command (a JSON object) to call the `execute_ipython_cell` tool. The code to be executed is merely a *string argument* within that command. This creates a layer of indirection and treats code execution as just another rigid tool.
-   **Proposed Model (Direct Output):** The LLM's native output *is the code itself*. The agent's framework is responsible for parsing this code directly from the response and executing it. This makes code the agent's primary mode of expression.

The key shift is to move from treating code execution as a constrained, structured tool call to making it the **agent's native output**. This is the foundation for unlocking greater power and statefulness.

### Why We Are Moving to a Code-Centric Approach

The initial structured-call model is safe and predictable but severely limits the agent's capabilities. By shifting to a model where the LLM's primary output is a Python code snippet, we unlock several key advantages that are critical for a general-purpose agent:

1.  **Unlocks True Power and Composability:** Direct code output allows the agent to write scripts that use loops, conditionals, variables, and error handling. It can chain multiple tool calls together in a single, logical action, which is impossible with a one-tool-per-turn structured model. This moves the agent from a simple "tool caller" to a true "problem solver."

2.  **Increases Efficiency and Reduces Cost:** By accomplishing more in a single turn, the agent requires fewer back-and-forth interactions with the LLM. This directly translates to lower latency (faster task completion) and reduced operational costs (fewer API calls).

3.  **Enables On-the-Fly Data Manipulation:** An agent that thinks in code can process and transform data between tool calls without needing an extra LLM turn. It can reformat strings, perform calculations, and filter lists as part of a single, coherent script.

4.  **Leverages the Core Strengths of Modern LLMs:** State-of-the-art models are exceptionally proficient at code generation. This approach allows the agent to "think" in Python, a language it excels at, rather than constraining it to a rigid JSON schema.

### The Hybrid "Planner-Executor" Model and the Role of a Stateful Executor

The goal is a hybrid "Planner-Executor" model. The Planner (the `UnifiedAgent`'s graph) sets high-level strategic goals, and the Executor (`smolagents`-style code generation) writes powerful scripts to accomplish each goal.

This model **only works** if the execution environment is **stateful**. A variable or function defined in one Executor script (to complete step 1 of the plan) *must* be available to the next Executor script (to complete step 2).

This is why **Step 4 and 5** of the plan are critical. We will replace the current stateless `Sandbox` with the **stateful `LocalPythonExecutor`** from `smolagents`. This executor acts like a persistent Python session, maintaining its memory across multiple turns of the Planner's graph. It is the glue that connects the Planner's strategic steps, allowing the agent to build complex solutions over time.

### The Hybrid Toolset: Achieving Efficiency and Generality via Prompting

A key challenge is balancing the power of dynamic tool discovery with the efficiency needed for simple tasks. A pure "Search, Load, Execute" workflow is too slow for common requests (e.g., "What is 2+2?").

**Our Solution:** We will implement a **hybrid toolset** model, controlled entirely through prompting to keep the architecture simple.

1.  **Pre-loaded Default Tools:** The agent will start with a small set of essential, always-available tools (e.g., `execute_ipython_cell`, `web_search`). These will be pre-loaded into the executor's environment.

2.  **Prompt-Driven Logic:** The system prompt will be structured to guide the LLM's reasoning. It will instruct the agent to **always attempt to solve the task using the default tools first**.

3.  **Fallback to Discovery:** The prompt will specify that the agent should **only use the `search_tools` meta-tool if it determines its default toolkit is insufficient** for the task at hand.

This creates an efficient "fast path" for the majority of tasks while retaining the full power of dynamic tool discovery for specialized requests, all without adding complexity to the agent's graph architecture.

---

# Comparison: Unified Agent vs. Smolagents' CodeAgent

This document outlines the major differences, pros, and cons between the `unified` agent and the `CodeAgent` from the `smolagents` library.

## 1. Core Architecture

### Unified Agent
- **Architecture:** State machine implemented with `langgraph`.
- **Execution Model:** Relies on predefined tool calls (`search_tools`, `load_tools`, `execute_ipython_cell`). The LLM's output is a structured tool call.
- **Flexibility:** Less flexible. The agent is constrained to the predefined tools and the logic of the graph.

### Smolagents' CodeAgent
- **Architecture:** ReAct-style loop (Reason, Act, Observe).
- **Execution Model:** The LLM generates Python code directly, which is then executed in a `PythonExecutor`. This is a more direct and powerful approach.
- **Flexibility:** Highly flexible. The agent can generate any Python code, allowing it to perform complex computations, define functions, and chain operations without being limited to a predefined set of tools.

## 2. Prompting

### Unified Agent
- **Prompting:** A single, monolithic prompt that instructs the LLM on how to use the available tools.
- **Few-shot Examples:** Lacks few-shot examples, which can make it harder for the LLM to understand the expected output format.

### Smolagents' CodeAgent
- **Prompting:** Uses a YAML file for prompts, which is cleaner and easier to manage.
- **Few-shot Examples:** Incorporates few-shot examples to guide the LLM, which generally improves the quality and reliability of the generated code.

## 3. Code Execution

### Unified Agent
- **Sandbox:** Uses a simple `Sandbox` to execute Python code snippets via `execute_ipython_cell`.
- **State Management:** State is managed within the `langgraph` state, but the code execution environment is stateless between `execute_ipython_cell` calls unless explicitly handled.

### Smolagents' CodeAgent
- **Executor:** Uses a more advanced `PythonExecutor` that can be local, or remote (Docker, E2B).
- **State Management:** The `PythonExecutor` maintains state between code executions, allowing the agent to define variables and functions that persist across turns.

## 4. Pros and Cons

### Unified Agent
**Pros:**
- **Structured:** The state machine provides a clear and predictable execution flow.
- **Safe:** The agent is limited to a predefined set of tools, which can be seen as a safety feature.

**Cons:**
- **Rigid:** The predefined toolset and graph structure make it less flexible.
- **Complex:** The `langgraph` implementation can be complex to understand and modify.
- **Less Powerful:** The agent's capabilities are limited by the available tools.

### Smolagents' CodeAgent
**Pros:**
- **Flexible:** The code-centric approach allows the agent to solve a wider range of tasks.
- **Powerful:** The agent can leverage the full power of Python, including defining functions, classes, and using third-party libraries.
- **Extensible:** Easy to add new tools by simply making them available in the Python execution environment.

**Cons:**
- **Less Structured:** The ReAct loop is less structured than a state machine, which can make it harder to debug.
- **Security:** Executing arbitrary code from an LLM is a security risk, although this is mitigated by the use of sandboxed environments.

## TODO: A Multi-Step Plan for a Hybrid Agent

This plan outlines a series of small, atomic changes to evolve the `UnifiedAgent` into a more powerful hybrid agent that combines the structured, dynamic tool management of `langgraph` with the expressive code execution of `smolagents`.

### Phase 1: Foundational Changes - Shifting to Code Generation

- [x] **1. Externalize Prompting:**
    - [x] Create a `prompts.yaml` file in `src/universal_mcp/agents/unified/`.
    - [x] Move the `SYSTEM_PROMPT` from `prompts.py` into `prompts.yaml`.
    - [x] Update `UnifiedAgent` in `agent.py` to load its system prompt from the new YAML file. This separates configuration from code and aligns with `smolagents` best practices.

- [x] **2. Introduce a Code-Centric Prompt:**
    - [x] In `prompts.yaml`, modify the system prompt to instruct the LLM to output Python code directly, using Markdown syntax for code blocks (e.g., ` ```python ... ``` `).
    - [x] Add one or two few-shot examples to the prompt, demonstrating how to call a meta-tool (like `web_search`) directly within a code block.

- [ ] **3. Adapt Graph for Direct Code Output:**
    - [ ] In `graph.py`, modify the `agent_node` to parse the Python code block from the LLM's raw text response instead of expecting a structured `tool_calls` attribute.
    - [ ] The output of the `agent_node` should now be the extracted code snippet (as a string).
    - [ ] Update the `execute_tools_node` to wrap this code snippet into a call to the `execute_ipython_cell` tool. This maintains the existing execution logic while adapting to the new code-centric output from the LLM.

### Phase 2: Integrating a More Powerful and Stateful Executor

- [ ] **4. Replace Sandbox with `LocalPythonExecutor`:**
    - [ ] Integrate `smolagents.local_python_executor.LocalPythonExecutor` into the `UnifiedAgent`.
    - [ ] In `agent.py`, replace the `Sandbox` instance with a persistent `LocalPythonExecutor` instance.
    - [ ] In `graph.py`, modify the `execute_tools_node` to call the `python_executor` directly with the code snippet.
    - [ ] Remove the `execute_ipython_cell` meta-tool, as the executor now handles code execution directly.

- [ ] **5. Enable Stateful Execution Across Turns:**
    - [ ] Ensure the `LocalPythonExecutor` instance on the `UnifiedAgent` is the same one used across all steps in the graph.
    - [ ] Verify that variables, functions, and imports defined in one turn are accessible in subsequent turns within the same `invoke` session.

### Phase 3: Enhancing Tool Management and Workflow

- [ ] **6. Dynamic Tool Injection into the Executor:**
    - [ ] Modify the `load_tools` logic in `graph.py`. When a tool is loaded, inject it directly into the `python_executor`'s namespace (both static and custom tools).
    - [ ] Update the system prompt in `prompts.yaml` to dynamically list the function signatures of the currently available tools in the executor's environment, making the LLM aware of what it can call.

- [ ] **7. Simplify the Graph (Optional but Recommended):**
    - [ ] Evaluate the necessity of the `validate_code_node`. Since `LocalPythonExecutor` can catch and report syntax errors, this validation might be redundant. Consider removing it and handling errors directly in the `execute_tools_node`.
    - [ ] Consider merging the `format_final_answer_node`'s logic into the main agent prompt, instructing the agent to provide a user-friendly summary before calling `finish()`.

- [ ] **8. Integrate Optional Planning:**
    - [ ] Add a `planning_interval` parameter to the `UnifiedAgent`.
    - [ ] Introduce a new `planning_node` in the graph that generates or updates a high-level plan.
    - [ ] Add a conditional edge that routes the graph to the `planning_node` every N steps, injecting the plan back into the agent's state.