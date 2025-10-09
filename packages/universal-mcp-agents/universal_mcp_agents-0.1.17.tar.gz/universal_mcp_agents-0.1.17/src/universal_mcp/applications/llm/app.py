import json
from typing import Any, Literal, cast

from langchain.chat_models import init_chat_model
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel, Field
from universal_mcp.applications.application import BaseApplication

MAX_RETRIES = 3


def _get_context_as_string(source: Any | list[Any] | dict[str, Any]) -> str:
    """Converts context to a string representation.

    Args:
        source: The source data to be converted. Can be a single value, a list of values, or a dictionary.

    Returns:
        A string representation of the source data, formatted with XML-like tags for dictionaries.
    """

    if not isinstance(source, dict):
        if isinstance(source, list):
            source = {f"doc_{i + 1}": str(doc) for i, doc in enumerate(source)}
        else:
            source = {"content": str(source)}

    return "\n".join(f"<{k}>\n{str(v)}\n</{k}>" for k, v in source.items())


class LLMApp(BaseApplication):
    """
    An application for leveraging Large Language Models (LLMs) for advanced text processing tasks.
    """

    def __init__(self, **kwargs):
        """Initialize the LLMApp."""
        super().__init__(name="llm")

    def generate_text(
        self,
        task: str,
        context: Any | list[Any] | dict[str, Any],
        tone: str = "normal",
        output_format: Literal["markdown", "html", "plain"] = "markdown",
        length: Literal["very-short", "concise", "normal", "long"] = "concise",
    ) -> str:
        """
        Generates well-written text for a high-level task using the provided context.

        Use this function for creative writing, summarization, and other text generation tasks.

        Args:
            task: The main writing task or directive.
            context: A single string, list of strings, or dictionary mapping labels to content.
            tone: The desired tone of the output (e.g., "formal", "casual", "technical").
            output_format: The desired output format ('markdown', 'html', 'plain').
            length: The desired length of the output ('very-short', 'concise', 'normal', 'long').

        Returns:
            The generated text as a string.
        """
        context_str = _get_context_as_string(context)

        prompt = f"{task.strip()}\n\n"
        if output_format == "markdown":
            prompt += "Please write in Markdown format.\n\n"
        elif output_format == "html":
            prompt += "Please write in HTML format.\n\n"
        else:
            prompt += "Please write in plain text format. Do not use markdown or HTML.\n\n"

        if tone not in ["normal", "default", ""]:
            prompt = f"{prompt} (Tone instructions: {tone})"

        if length not in ["normal", "default", ""]:
            prompt = f"{prompt} (Length instructions: {length})"

        full_prompt = f"{prompt}\n\nContext:\n{context_str}\n\n"

        model = AzureChatOpenAI(model="gpt-4o", temperature=0.7)
        response = model.with_retry(stop_after_attempt=MAX_RETRIES).invoke(full_prompt)
        return str(response.content)

    def classify_data(
        self,
        task: str,
        context: Any | list[Any] | dict[str, Any],
        class_descriptions: dict[str, str],
    ) -> dict[str, Any]:
        """
        Classifies data into one of several categories based on a given task and context.

        Args:
            task: The classification question and any specific rules or requirements.
            context: The data to be classified, provided as a string, list, or dictionary.
            class_descriptions: A dictionary mapping class names to their descriptions.

        Returns:
            A dictionary containing the classification probabilities, the reasoning, and the top class.
        """
        context_str = _get_context_as_string(context)

        prompt = (
            f"{task}\n\n"
            f"This is a classification task.\nPossible classes and descriptions:\n"
            f"{json.dumps(class_descriptions, indent=2)}\n\n"
            f"Context:\n{context_str}\n\n"
            "Return ONLY a valid JSON object, no extra text."
        )

        model = init_chat_model(model="claude-4-sonnet-20250514", temperature=0)

        class ClassificationResult(BaseModel):
            probabilities: dict[str, float] = Field(..., description="The probabilities for each class.")
            reason: str = Field(..., description="The reasoning behind the classification.")
            top_class: str = Field(..., description="The class with the highest probability.")

        response = (
            model.with_structured_output(schema=ClassificationResult, method="json_mode")
            .with_retry(stop_after_attempt=MAX_RETRIES)
            .invoke(prompt)
        )
        return cast(dict[str, Any], response)

    def extract_data(
        self,
        task: str,
        source: Any | list[Any] | dict[str, Any],
        output_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Extracts structured data from unstructured text based on a provided JSON schema.

        Args:
            task: A description of the data to be extracted.
            source: The unstructured data to extract from (e.g., document, webpage content).
            output_schema: A valid JSON schema with a 'title' and 'description'.

        Returns:
            A dictionary containing the extracted data, matching the provided schema.
        """
        context_str = _get_context_as_string(source)

        prompt = (
            f"{task}\n\n"
            f"Context:\n{context_str}\n\n"
            "Return ONLY a valid JSON object that conforms to the provided schema, with no extra text."
        )

        model = init_chat_model(model="claude-4-sonnet-20250514", temperature=0)

        response = (
            model.with_structured_output(schema=output_schema, method="json_mode")
            .with_retry(stop_after_attempt=MAX_RETRIES)
            .invoke(prompt)
        )
        return cast(dict[str, Any], response)
