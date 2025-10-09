"""
Cursor integration utilities for MCP
"""

import logging
import os
from typing import Any, Dict

from mcpm.clients.base import JSONClientManager

logger = logging.getLogger(__name__)


class CursorManager(JSONClientManager):
    """Manages Cursor MCP server configurations"""

    # Client information
    client_key = "cursor"
    display_name = "Cursor"
    download_url = "https://cursor.sh/download"

    def __init__(self, config_path_override: str | None = None):
        """Initialize the Cursor client manager

        Args:
            config_path_override: Optional path to override the default config file location
        """
        super().__init__(config_path_override=config_path_override)

        if config_path_override:
            self.config_path = config_path_override
        else:
            # Set config path based on detected platform
            if self._system == "Windows":
                self.config_path = os.path.join(os.environ.get("USERPROFILE", ""), ".cursor", "mcp.json")
            else:
                # MacOS or Linux
                self.config_path = os.path.expanduser("~/.cursor/mcp.json")

    def _get_empty_config(self) -> Dict[str, Any]:
        """Get empty config structure for Cursor"""
        return {"mcpServers": {}}
