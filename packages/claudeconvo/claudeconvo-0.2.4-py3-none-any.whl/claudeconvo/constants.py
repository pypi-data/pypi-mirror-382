"""
Constants for claudeconvo.

This module defines all constants used throughout the claudeconvo application,
including file size limits, display formatting constants, parser limits,
terminal constraints, and default paths.

All constants are organized into logical groups for maintainability.
"""

import os

################################################################################
# File size limits
BYTES_PER_KB     = 1024
BYTES_PER_MB     = BYTES_PER_KB * 1024
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE    = MAX_FILE_SIZE_MB * BYTES_PER_MB

# Display formatting
UUID_DISPLAY_LENGTH        = 8
FILENAME_DISPLAY_WIDTH     = 44
SEPARATOR_WIDTH            = 70
LIST_ITEM_NUMBER_WIDTH     = 3
SEPARATOR_CHAR             = "-"
HEADER_SEPARATOR_CHAR      = "="
THEME_LIST_SEPARATOR_WIDTH = 40
THEME_NAME_DISPLAY_WIDTH   = 16

# Parser limits
MAX_RECURSION_DEPTH = 20
MAX_LINE_SIZE = 10 * BYTES_PER_MB  # 10MB per line to prevent memory exhaustion

# Terminal and input constants
ESC_KEY_CODE          = 27
WATCH_POLL_INTERVAL   = 0.5
MAX_FILE_INDEX_DIGITS = 10  # No reasonable index would be > 10 digits

# Terminal width constraints
MIN_TOOL_WIDTH          = 20
MAX_TOOL_WIDTH          = 60
TOOL_WIDTH_DIVISOR      = 3  # term_width // 3 for min width
TOOL_WIDTH_HALF_DIVISOR = 2  # term_width // 2 for max width

# Truncation limits (these can be overridden by ShowOptions)
DEFAULT_TRUNCATION_LIMITS = {
    "tool_param"   : 200,
    "tool_result"  : 500,
    "default"      : 500,
    "error"        : 1000,
    "error_short"  : 500,
}
DEFAULT_MAX_LENGTH = 500  # Default text truncation length

# Terminal display constants
DEFAULT_FALLBACK_WIDTH = 80  # Fallback when terminal width can't be detected
MIN_WRAP_WIDTH = 20  # Minimum width for text wrapping
ELLIPSIS_LENGTH = 3  # Length of "..." for truncation

# Display limits for diagnostics
MAX_PARSE_ERRORS_DISPLAY   = 10
MAX_FIELD_PATTERNS_DISPLAY = 20
MAX_TYPE_COUNTS_DISPLAY    = 20

# Default paths
# Allow overriding the Claude projects directory via environment variable
_env_projects_dir = os.environ.get("CLAUDE_PROJECTS_DIR", ".claude/projects")

# Validate the path for safety
def _validate_projects_dir(path_str: str) -> str:
    """Validate and normalize the projects directory path.

    Returns the path if valid, otherwise returns the default.
    """
    from pathlib import Path

    default_path = ".claude/projects"

    if not path_str:
        return default_path

    try:
        # Normalize the path to resolve any relative components
        path = Path(path_str).expanduser()

        # If it's an absolute path, ensure it's under the user's home directory
        if path.is_absolute():
            home = Path.home()
            try:
                # Check if the path is under the home directory
                path.relative_to(home)
            except ValueError:
                # Path is not under home directory - use default
                return default_path

        # Check for any remaining dangerous patterns after normalization
        path_str_normalized = str(path)
        if ".." in path_str_normalized:
            return default_path

        return path_str

    except (ValueError, OSError):
        # Invalid path - use default
        return default_path

CLAUDE_PROJECTS_DIR = _validate_projects_dir(_env_projects_dir)

# Configuration file path
CONFIG_FILE_PATH = os.path.expanduser("~/.claudeconvorc")
