"""
Tool invocation tracking for proper Task/subagent identification.

This module provides functionality to track tool invocations in Claude conversation
logs and identify Task/subagent results for proper display formatting.

Example usage:
    tracker = ToolInvocationTracker()
    tracker.track_tool_use(entry)
    tool_info = tracker.get_tool_info(tool_use_id)
"""

from typing import Any

################################################################################

class ToolInvocationTracker:
    """Tracks tool invocations to properly identify Task/subagent results."""

    ################################################################################

    def __init__(self) -> None:
        """
        Initialize the tracker.

        Initializes the internal dictionary to track tool invocations
        by their unique tool_use_id.
        """
        # Map tool_use_id to tool invocation details
        self.tool_invocations: dict[str, dict[str, Any]] = {}

    ################################################################################

    def track_tool_use(self, entry: dict[str, Any]) -> None:
        """
        Track a tool invocation from an assistant message.

        Extracts tool use information from assistant messages and stores
        it for later lookup when processing tool results.

        Args:
            entry: Parsed log entry containing assistant message with tool uses
        """
        # Check if this is an assistant message with tool use
        if entry.get("type") != "assistant":
            return

        message = entry.get("message", {})
        if not isinstance(message, dict):
            return

        content = message.get("content", [])
        if not isinstance(content, list):
            return

        # Look for tool_use items in content
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                tool_id = item.get("id")
                if tool_id:
                    # Store tool invocation details
                    self.tool_invocations[tool_id] = {
                        "name"         : item.get("name", "Unknown"),
                        "input"        : item.get("input", {}),
                        "timestamp"    : entry.get("timestamp"),
                        "uuid"         : entry.get("uuid"),
                        "isSidechain"  : entry.get("isSidechain", False),
                    }

                    # For Task invocations, store subagent type
                    if item.get("name") == "Task":
                        input_data = item.get("input", {})
                        if isinstance(input_data, dict):
                            self.tool_invocations[tool_id]["subagent_type"] = input_data.get(
                                "subagent_type", "unknown"
                            )
                            self.tool_invocations[tool_id]["description"] = input_data.get(
                                "description", ""
                            )

    ################################################################################

    def get_tool_info(self, tool_use_id: str) -> dict[str, Any] | None:
        """
        Get tool invocation info for a given tool_use_id.

        Args:
            tool_use_id: The tool use ID to look up

        Returns:
            Tool invocation details or None if not found
        """
        return self.tool_invocations.get(tool_use_id)

    ################################################################################

    def is_tool_result(self, entry: dict[str, Any]) -> bool:
        """
        Check if an entry is any kind of tool result.

        Args:
            entry: Parsed log entry

        Returns:
            True if this is a tool result, False otherwise
        """
        # Must be a user type entry
        if entry.get("type") != "user":
            return False

        # Check for toolUseResult field (any tool result)
        if entry.get("toolUseResult") is not None:
            return True

        # Also check message content for tool_result
        message = entry.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict) and first_item.get("type") == "tool_result":
                    return True

        return False

    ################################################################################

    def is_task_result(self, entry: dict[str, Any]) -> bool:
        """
        Check if an entry is specifically a Task/subagent result.

        Args:
            entry: Parsed log entry

        Returns:
            True if this is a Task result, False otherwise
        """
        if not self.is_tool_result(entry):
            return False

        # Check for toolUseResult with content field (Task signature)
        tool_result = entry.get("toolUseResult", {})
        if isinstance(tool_result, dict) and "content" in tool_result:
            return True

        # Also check message content for tool_result with array content
        message = entry.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if (
                    isinstance(first_item, dict)
                    and first_item.get("type") == "tool_result"
                    and isinstance(first_item.get("content"), list)
                ):
                    return True

        return False

    ################################################################################

    def get_tool_info_for_entry(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        """
        Get tool info for any tool_result entry.

        Args:
            entry: Parsed log entry (should be a user type with tool_result)

        Returns:
            Tool invocation details or None if not a tool result
        """
        if not self.is_tool_result(entry):
            return None

        # Try to extract tool_use_id from the entry
        tool_use_id = None

        # First check message content for tool_result with tool_use_id
        message = entry.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict):
                    tool_use_id = first_item.get("tool_use_id")

        # If no tool_use_id found, check for toolUseID field (older format)
        if not tool_use_id:
            tool_use_id = entry.get("toolUseID")

        if tool_use_id:
            return self.get_tool_info(tool_use_id)

        return None

    ################################################################################

    def get_task_info_for_entry(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        """
        Get Task info for a tool_result entry.

        Args:
            entry: Parsed log entry (should be a user type with tool_result)

        Returns:
            Task invocation details or None if not a Task result
        """
        if not self.is_task_result(entry):
            return None

        # Extract tool_use_id from the entry
        message = entry.get("message", {})
        if isinstance(message, dict):
            content = message.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict):
                    tool_use_id = first_item.get("tool_use_id")
                    if tool_use_id:
                        return self.get_tool_info(tool_use_id)

        return None
