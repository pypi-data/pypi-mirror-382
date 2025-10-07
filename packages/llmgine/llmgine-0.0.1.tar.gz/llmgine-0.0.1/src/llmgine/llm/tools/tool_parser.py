"""Tool parsing for LLMs.

This module provides a way to parse tools into a format that can be used by
any LLM.
"""

from abc import abstractmethod
from typing import Any

from llmgine.llm import ModelFormattedDictTool
from llmgine.llm.tools.tool import Tool


class ToolParser:
    @abstractmethod
    def parse_tool(self, tool: Tool) -> ModelFormattedDictTool:
        """Parse a tool into a format that can be used by any LLM."""
        pass


def create_required_and_properties(tool: Tool) -> tuple[list[str], dict[str, Any]]:
    required: list[str] = []
    properties: dict[str, Any] = {}
    for param in tool.parameters:
        properties[param.name] = {
            "type": param.type,
            "description": param.description,
        }
        if param.required:
            required.append(param.name)

    return required, properties


class OpenAIToolParser(ToolParser):
    """A parser for tools that can be used by OpenAI."""

    def parse_tool(self, tool: Tool) -> ModelFormattedDictTool:
        """Parse a tool into a format that can be used by OpenAI.

        Args:
            tool: The tool to be parsed.

        Returns:
            A dictionary containing the tool's name, description, and parameters.
        """

        # parameters that are required
        required, properties = create_required_and_properties(tool)

        return ModelFormattedDictTool({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        })


class ClaudeToolParser(ToolParser):
    """A parser for tools that can be used by Claude."""

    def parse_tool(self, tool: Tool) -> ModelFormattedDictTool:
        """Parse a tool into a format that can be used by Claude.

        Args:
            tool: The tool to be parsed.

        Returns:
            A dictionary containing the tool's name, description, and parameters.
        """

        # parameters that are required
        required, properties = create_required_and_properties(tool)

        return ModelFormattedDictTool({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        })


class DeepSeekToolParser(ToolParser):
    """A parser for tools that can be used by DeepSeek."""

    def parse_tool(self, tool: Tool) -> ModelFormattedDictTool:
        """Parse a tool into a format that can be used by DeepSeek.

        Args:
            tool: The tool to be parsed.

        Returns:
            A dictionary containing the tool's name, description, and parameters.
        """

        # parameters that are required
        required, properties = create_required_and_properties(tool)

        return ModelFormattedDictTool({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        })
