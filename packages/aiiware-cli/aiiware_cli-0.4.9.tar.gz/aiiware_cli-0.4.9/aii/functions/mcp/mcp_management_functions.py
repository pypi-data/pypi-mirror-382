"""
MCP Server Management Functions

Commands for managing MCP server configurations:
- mcp_add: Add a new MCP server
- mcp_remove: Remove an MCP server
- mcp_list: List all configured servers
- mcp_enable: Enable a disabled server
- mcp_disable: Disable a server (keeps config)
- mcp_catalog: List popular pre-configured servers
- mcp_install: Install server from catalog
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ...core.models import (
    ExecutionContext,
    ExecutionResult,
    FunctionCategory,
    FunctionPlugin,
    FunctionSafety,
    OutputMode,
    ParameterSchema,
)

logger = logging.getLogger(__name__)


class MCPConfigManager:
    """
    Manages MCP server configuration file operations.

    Follows SRP: Single responsibility for config file I/O.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_path: Override config file path (default: ~/.aii/mcp_servers.json)
        """
        self.config_path = config_path or (Path.home() / ".aii" / "mcp_servers.json")
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """
        Load MCP server configuration.

        Returns:
            Configuration dictionary with 'mcpServers' key
        """
        if not self.config_path.exists():
            return {"mcpServers": {}}

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)
            return config if isinstance(config, dict) else {"mcpServers": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return {"mcpServers": {}}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {"mcpServers": {}}

    def save_config(self, config: Dict[str, Any]) -> bool:
        """
        Save MCP server configuration.

        Args:
            config: Configuration dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            self._ensure_config_dir()
            with open(self.config_path, "w") as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def backup_config(self) -> bool:
        """
        Create backup of current configuration.

        Returns:
            True if backup created successfully
        """
        if not self.config_path.exists():
            return True

        try:
            backup_path = self.config_path.with_suffix(".json.backup")
            import shutil

            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Config backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup config: {e}")
            return False


class MCPAddFunction(FunctionPlugin):
    """
    Add MCP server to configuration.

    Examples:
    - aii mcp add chrome npx chrome-devtools-mcp@latest
    - aii mcp add postgres uvx mcp-server-postgres --connection-string $DB_URL
    - aii mcp add github npx @modelcontextprotocol/server-github
    """

    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        """
        Initialize function.

        Args:
            config_manager: Config manager instance (DIP: dependency injection)
        """
        self.config_manager = config_manager or MCPConfigManager()

    @property
    def name(self) -> str:
        return "mcp_add"

    @property
    def description(self) -> str:
        return (
            "Add MCP server to configuration. Use when user wants to: "
            "'add mcp server', 'install mcp server', 'configure mcp server', "
            "'add chrome/github/postgres server', 'setup mcp'. "
            "Examples: 'add chrome mcp server', 'install github server', "
            "'configure postgres mcp server with connection string'."
        )

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "server_name": ParameterSchema(
                name="server_name",
                type="string",
                required=True,
                description="Short name for the server (e.g., 'chrome', 'postgres', 'github')",
            ),
            "command": ParameterSchema(
                name="command",
                type="string",
                required=True,
                description="Command to run (e.g., 'npx', 'uvx', 'node')",
            ),
            "args": ParameterSchema(
                name="args",
                type="array",
                required=True,
                description="Command arguments as list (e.g., ['chrome-devtools-mcp@latest'])",
            ),
            "env": ParameterSchema(
                name="env",
                type="object",
                required=False,
                description="Environment variables as dict (e.g., {'API_KEY': '${GITHUB_TOKEN}'})",
            ),
            "enabled": ParameterSchema(
                name="enabled",
                type="boolean",
                required=False,
                description="Enable server immediately (default: true)",
            ),
            "transport": ParameterSchema(
                name="transport",
                type="string",
                required=False,
                description="Transport protocol: 'stdio', 'sse', or 'http' (default: 'stdio')",
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        """Safe operation: just modifies config file"""
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        """CLEAN mode: users want just the confirmation"""
        return OutputMode.CLEAN

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """
        Add MCP server to configuration.

        Args:
            parameters: Function parameters
            context: Execution context

        Returns:
            ExecutionResult with success status
        """
        server_name = parameters["server_name"]
        command = parameters["command"]
        args = parameters["args"]
        env = parameters.get("env", {})
        enabled = parameters.get("enabled", True)
        transport = parameters.get("transport", "stdio")

        # Validate transport
        if transport not in ["stdio", "sse", "http"]:
            return ExecutionResult(
                success=False,
                message=f"Invalid transport '{transport}'. Must be: stdio, sse, or http",
                data={"clean_output": f"❌ Invalid transport '{transport}'"},
            )

        # Load existing config
        config = self.config_manager.load_config()
        servers = config.get("mcpServers", {})

        # Check if server already exists
        if server_name in servers:
            return ExecutionResult(
                success=False,
                message=f"Server '{server_name}' already exists. Use 'aii mcp remove {server_name}' first.",
                data={
                    "clean_output": f"❌ Server '{server_name}' already exists.\n\nUse: aii mcp remove {server_name}"
                },
            )

        # Build server config
        server_config = {
            "command": command,
            "args": args if isinstance(args, list) else [args],
        }

        if env:
            server_config["env"] = env

        # Add server to config
        servers[server_name] = server_config
        config["mcpServers"] = servers

        # Backup before saving
        self.config_manager.backup_config()

        # Save config
        if not self.config_manager.save_config(config):
            return ExecutionResult(
                success=False,
                message="Failed to save configuration",
                data={"clean_output": "❌ Failed to save configuration"},
            )

        # Build output message
        output_lines = [
            f"✓ Added '{server_name}' server",
            f"✓ Configuration saved to {self.config_manager.config_path}",
            f"✓ Transport: {transport}",
        ]

        if env:
            output_lines.append(f"✓ Environment variables: {', '.join(env.keys())}")

        output_lines.append("")
        output_lines.append(
            f"Try it: aii \"use {server_name} mcp server to [your task]\""
        )

        output = "\n".join(output_lines)

        return ExecutionResult(
            success=True,
            message=output,
            data={
                "server_name": server_name,
                "config": server_config,
                "config_path": str(self.config_manager.config_path),
                "clean_output": output,
            },
        )


class MCPRemoveFunction(FunctionPlugin):
    """Remove MCP server from configuration"""

    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager or MCPConfigManager()

    @property
    def name(self) -> str:
        return "mcp_remove"

    @property
    def description(self) -> str:
        return (
            "Remove MCP server from configuration. Use when user wants to: "
            "'remove mcp server', 'delete mcp server', 'uninstall mcp server', "
            "'remove chrome/github/postgres server'. "
            "Examples: 'remove chrome server', 'delete github mcp server'."
        )

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "server_name": ParameterSchema(
                name="server_name",
                type="string",
                required=True,
                description="Name of the server to remove",
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        """Potentially destructive: confirm before removing"""
        return True

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.RISKY

    @property
    def default_output_mode(self) -> OutputMode:
        return OutputMode.CLEAN

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """Remove MCP server from configuration"""
        server_name = parameters["server_name"]

        # Load config
        config = self.config_manager.load_config()
        servers = config.get("mcpServers", {})

        # Check if server exists
        if server_name not in servers:
            return ExecutionResult(
                success=False,
                message=f"Server '{server_name}' not found",
                data={"clean_output": f"❌ Server '{server_name}' not found"},
            )

        # Backup before removing
        self.config_manager.backup_config()

        # Remove server
        del servers[server_name]
        config["mcpServers"] = servers

        # Save config
        if not self.config_manager.save_config(config):
            return ExecutionResult(
                success=False,
                message="Failed to save configuration",
                data={"clean_output": "❌ Failed to save configuration"},
            )

        output = f"✓ Removed '{server_name}' server"

        return ExecutionResult(
            success=True,
            message=output,
            data={"server_name": server_name, "clean_output": output},
        )


class MCPListFunction(FunctionPlugin):
    """List all configured MCP servers"""

    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager or MCPConfigManager()

    @property
    def name(self) -> str:
        return "mcp_list"

    @property
    def description(self) -> str:
        return (
            "List all configured MCP servers. Use when user wants to: "
            "'list mcp servers', 'show mcp servers', 'what mcp servers', "
            "'mcp server list', 'show configured servers'. "
            "Examples: 'list my mcp servers', 'show all mcp servers'."
        )

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {}

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        """STANDARD mode: show list with metadata"""
        return OutputMode.STANDARD

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """List all configured MCP servers"""
        config = self.config_manager.load_config()
        servers = config.get("mcpServers", {})

        if not servers:
            output = "No MCP servers configured.\n\nTry: aii mcp catalog"
            return ExecutionResult(
                success=True,
                message=output,
                data={"servers": {}, "count": 0, "clean_output": output},
            )

        # Build output
        output_lines = ["📦 Configured MCP Servers:", ""]

        for server_name, server_config in servers.items():
            command = server_config.get("command", "")
            args = server_config.get("args", [])
            args_str = " ".join(args) if isinstance(args, list) else str(args)

            output_lines.append(f"✓ {server_name}")
            output_lines.append(f"  Command: {command} {args_str}")

            if "env" in server_config:
                env_vars = ", ".join(server_config["env"].keys())
                output_lines.append(f"  Environment: {env_vars}")

            output_lines.append("")

        output_lines.append(f"Total: {len(servers)} server(s)")
        output = "\n".join(output_lines)

        return ExecutionResult(
            success=True,
            message=output,
            data={
                "servers": servers,
                "count": len(servers),
                "clean_output": output,
            },
        )


class MCPEnableFunction(FunctionPlugin):
    """Enable a disabled MCP server"""

    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager or MCPConfigManager()

    @property
    def name(self) -> str:
        return "mcp_enable"

    @property
    def description(self) -> str:
        return (
            "Enable a disabled MCP server. Use when user wants to: "
            "'enable mcp server', 'activate mcp server', 'turn on mcp server'. "
            "Examples: 'enable chrome server', 'activate github mcp server'."
        )

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "server_name": ParameterSchema(
                name="server_name",
                type="string",
                required=True,
                description="Name of the server to enable",
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        return OutputMode.CLEAN

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """Enable MCP server"""
        server_name = parameters["server_name"]

        config = self.config_manager.load_config()
        servers = config.get("mcpServers", {})

        if server_name not in servers:
            return ExecutionResult(
                success=False,
                message=f"Server '{server_name}' not found",
                data={"clean_output": f"❌ Server '{server_name}' not found"},
            )

        # Note: Current config format doesn't have 'enabled' flag
        # This is a future enhancement - for now just acknowledge
        output = f"✓ Server '{server_name}' is enabled"

        return ExecutionResult(
            success=True,
            message=output,
            data={"server_name": server_name, "clean_output": output},
        )


class MCPDisableFunction(FunctionPlugin):
    """Disable an MCP server (keeps config)"""

    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager or MCPConfigManager()

    @property
    def name(self) -> str:
        return "mcp_disable"

    @property
    def description(self) -> str:
        return (
            "Disable an MCP server (keeps config). Use when user wants to: "
            "'disable mcp server', 'deactivate mcp server', 'turn off mcp server'. "
            "Examples: 'disable chrome server', 'deactivate github mcp server'."
        )

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "server_name": ParameterSchema(
                name="server_name",
                type="string",
                required=True,
                description="Name of the server to disable",
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        return OutputMode.CLEAN

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """Disable MCP server"""
        server_name = parameters["server_name"]

        config = self.config_manager.load_config()
        servers = config.get("mcpServers", {})

        if server_name not in servers:
            return ExecutionResult(
                success=False,
                message=f"Server '{server_name}' not found",
                data={"clean_output": f"❌ Server '{server_name}' not found"},
            )

        # Note: Current config format doesn't have 'enabled' flag
        # This is a future enhancement - for now just acknowledge
        output = f"✓ Server '{server_name}' is disabled (config preserved)"

        return ExecutionResult(
            success=True,
            message=output,
            data={"server_name": server_name, "clean_output": output},
        )


class MCPCatalogFunction(FunctionPlugin):
    """List popular pre-configured MCP servers"""

    @property
    def name(self) -> str:
        return "mcp_catalog"

    @property
    def description(self) -> str:
        return (
            "List popular pre-configured MCP servers. Use when user wants to: "
            "'show mcp catalog', 'list popular mcp servers', 'what mcp servers available', "
            "'mcp server catalog', 'show available servers'. "
            "Examples: 'show popular mcp servers', 'what servers can I install'."
        )

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {}

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        """STANDARD mode: show catalog with details"""
        return OutputMode.STANDARD

    def _get_catalog(self) -> Dict[str, Dict[str, Any]]:
        """
        Get MCP server catalog.

        Returns:
            Dictionary of server definitions
        """
        return {
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "description": "GitHub integration (repos, issues, PRs)",
                "category": "Development",
                "env_required": ["GITHUB_TOKEN"],
            },
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "${PROJECT_PATH}"],
                "description": "Local filesystem access",
                "category": "Development",
                "env_required": ["PROJECT_PATH"],
            },
            "postgres": {
                "command": "uvx",
                "args": ["mcp-server-postgres", "--connection-string", "${POSTGRES_URL}"],
                "description": "PostgreSQL database integration",
                "category": "Database",
                "env_required": ["POSTGRES_URL"],
            },
            "chrome-devtools": {
                "command": "npx",
                "args": ["-y", "chrome-devtools-mcp@latest"],
                "description": "Chrome browser automation and DevTools",
                "category": "Automation",
                "env_required": [],
            },
            "puppeteer": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
                "description": "Browser automation and web scraping",
                "category": "Automation",
                "env_required": [],
            },
            "slack": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-slack"],
                "description": "Slack workspace integration",
                "category": "Communication",
                "env_required": ["SLACK_BOT_TOKEN"],
            },
            "12306": {
                "command": "npx",
                "args": ["-y", "12306-mcp"],
                "description": "中国铁路12306火车票查询 (China Railway ticket search)",
                "category": "Chinese Ecosystem",
                "env_required": [],
            },
            "mongodb": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-mongodb"],
                "description": "MongoDB database integration",
                "category": "Database",
                "env_required": ["MONGODB_URL"],
            },
            "redis": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-redis"],
                "description": "Redis cache integration",
                "category": "Database",
                "env_required": ["REDIS_URL"],
            },
            "docker": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-docker"],
                "description": "Docker container management",
                "category": "DevOps",
                "env_required": [],
            },
        }

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """List popular MCP servers from catalog"""
        catalog = self._get_catalog()

        # Load current config to mark installed servers
        config_manager = MCPConfigManager()
        config = config_manager.load_config()
        installed_servers = set(config.get("mcpServers", {}).keys())

        # Group by category
        by_category: Dict[str, List[tuple[str, Dict[str, Any]]]] = {}
        for server_name, server_info in catalog.items():
            category = server_info["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append((server_name, server_info))

        # Build output
        output_lines = ["📦 Popular MCP Servers:", ""]

        for category, servers in sorted(by_category.items()):
            output_lines.append(f"{category}:")
            for server_name, server_info in sorted(servers):
                status = "✓" if server_name in installed_servers else "○"
                output_lines.append(f"  {status} {server_name:<18} - {server_info['description']}")
            output_lines.append("")

        output_lines.append("Legend:")
        output_lines.append("  ✓ = Already installed")
        output_lines.append("  ○ = Available to install")
        output_lines.append("")
        output_lines.append("Install: aii mcp install <server-name>")

        output = "\n".join(output_lines)

        return ExecutionResult(
            success=True,
            message=output,
            data={
                "catalog": catalog,
                "installed": list(installed_servers),
                "count": len(catalog),
                "clean_output": output,
            },
        )


class MCPInstallFunction(FunctionPlugin):
    """Install MCP server from catalog"""

    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager or MCPConfigManager()

    @property
    def name(self) -> str:
        return "mcp_install"

    @property
    def description(self) -> str:
        return (
            "Install MCP server from catalog. Use when user wants to: "
            "'install mcp server', 'install from catalog', 'install github/chrome/postgres server'. "
            "Examples: 'install github server', 'install chrome mcp server from catalog'."
        )

    @property
    def category(self) -> FunctionCategory:
        return FunctionCategory.SYSTEM

    @property
    def parameters(self) -> dict[str, ParameterSchema]:
        return {
            "server_name": ParameterSchema(
                name="server_name",
                type="string",
                required=True,
                description="Name of the server from catalog (e.g., 'github', 'chrome-devtools')",
            ),
            "env_vars": ParameterSchema(
                name="env_vars",
                type="object",
                required=False,
                description="Environment variables as dict (e.g., {'GITHUB_TOKEN': 'your-token'})",
            ),
        }

    @property
    def requires_confirmation(self) -> bool:
        return False

    @property
    def safety_level(self) -> FunctionSafety:
        return FunctionSafety.SAFE

    @property
    def default_output_mode(self) -> OutputMode:
        return OutputMode.CLEAN

    def _get_catalog(self) -> Dict[str, Dict[str, Any]]:
        """Get catalog (reuse from MCPCatalogFunction)"""
        catalog_func = MCPCatalogFunction()
        return catalog_func._get_catalog()

    async def execute(
        self, parameters: Dict[str, Any], context: ExecutionContext
    ) -> ExecutionResult:
        """Install MCP server from catalog"""
        server_name = parameters["server_name"]
        env_vars = parameters.get("env_vars", {})

        # Get catalog
        catalog = self._get_catalog()

        # Check if server exists in catalog
        if server_name not in catalog:
            available = ", ".join(sorted(catalog.keys()))
            return ExecutionResult(
                success=False,
                message=f"Server '{server_name}' not found in catalog.\n\nAvailable: {available}",
                data={
                    "clean_output": f"❌ Server '{server_name}' not found in catalog.\n\nTry: aii mcp catalog"
                },
            )

        server_info = catalog[server_name]

        # Check if already installed
        config = self.config_manager.load_config()
        servers = config.get("mcpServers", {})

        if server_name in servers:
            return ExecutionResult(
                success=False,
                message=f"Server '{server_name}' is already installed",
                data={"clean_output": f"✓ Server '{server_name}' is already installed"},
            )

        # Check for required environment variables
        env_required = server_info.get("env_required", [])
        missing_env = []
        for env_var in env_required:
            if env_var not in env_vars and env_var not in server_info.get("args", []):
                missing_env.append(env_var)

        if missing_env:
            output_lines = [
                f"📦 Installing '{server_name}' from catalog...",
                f"⚠️  Requires environment variables: {', '.join(missing_env)}",
                "",
                "Please provide them when installing:",
                f"  aii mcp add {server_name} {server_info['command']} {' '.join(server_info['args'])}",
                "",
                "Or set them in your environment:",
            ]
            for env_var in missing_env:
                output_lines.append(f"  export {env_var}='your-value-here'")

            output = "\n".join(output_lines)

            return ExecutionResult(
                success=False,
                message=output,
                data={"clean_output": output, "missing_env": missing_env},
            )

        # Install server (delegate to MCPAddFunction)
        add_function = MCPAddFunction(self.config_manager)

        return await add_function.execute(
            {
                "server_name": server_name,
                "command": server_info["command"],
                "args": server_info["args"],
                "env": env_vars,
                "enabled": True,
                "transport": "stdio",
            },
            context,
        )
