"""
MCP Client Manager

Manages connections to multiple MCP servers and provides unified access
to tools, resources, and prompts across all connected servers.

Features:
- Multi-server connection management
- Tool/resource/prompt discovery and aggregation
- Tool invocation routing
- Session lifecycle management
- Error handling and graceful degradation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from aii.data.integrations.mcp.config_loader import MCPConfigLoader, ServerConfig
from aii.data.integrations.mcp.models import (
    MCPTool,
    MCPResource,
    MCPPrompt,
    ServerConnection,
    ConnectionState,
    ToolCallResult
)

logger = logging.getLogger(__name__)


class MCPClientManager:
    """
    Manages connections to multiple MCP servers.

    This is the core component that:
    1. Connects to all configured MCP servers
    2. Discovers capabilities (tools/resources/prompts)
    3. Routes requests to appropriate servers
    4. Manages session lifecycle
    """

    def __init__(self, config_loader: Optional[MCPConfigLoader] = None):
        """
        Initialize MCP Client Manager.

        Args:
            config_loader: Optional config loader (creates default if None)
        """
        self.config_loader = config_loader or MCPConfigLoader()
        self.connections: Dict[str, ServerConnection] = {}
        self._tool_cache: Dict[str, List[MCPTool]] = {}
        self._cache_ttl = 300  # 5 minutes
        self._initialized = False
        self._entered = False

    async def __aenter__(self):
        """
        Enter async context - connect to all MCP servers.

        This must be called to establish connections. All operations
        (tool calls, etc.) happen within this context.
        """
        if self._entered:
            raise RuntimeError("MCPClientManager is already entered")

        await self.initialize()
        self._entered = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit async context - disconnect from all MCP servers.

        Properly closes all connections and cleans up resources.
        """
        await self.shutdown()
        self._entered = False
        return False

    async def initialize(self):
        """
        Initialize the client manager.

        Loads configurations and discovers available tools.
        Note: With per-request connections, we only discover tools during init,
        not create persistent connections.
        """
        if self._initialized:
            logger.debug("MCP Client Manager already initialized")
            return

        logger.info("Initializing MCP Client Manager")

        # Load configurations
        servers = self.config_loader.load_configurations()
        logger.info(f"Loaded {len(servers)} server configurations")

        # Discover tools from all servers (creates temporary connections)
        await self.connect_all_servers()

        self._initialized = True
        logger.info(f"MCP Client Manager initialized with {len(self.connections)} servers")

    async def connect_all_servers(self):
        """
        Discover tools from all configured MCP servers.

        Creates temporary connections to each server to discover available
        tools, then cleanly closes the connections.
        """
        servers = self.config_loader.servers

        # Discover tools from servers in parallel
        tasks = [
            self.discover_server_tools(server_name, server_config)
            for server_name, server_config in servers.items()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful
        logger.info(f"Tool discovery: {successful} successful, {failed} failed")

    async def discover_server_tools(self, server_name: str, config: ServerConfig) -> bool:
        """
        Discover tools from a server using a temporary connection.

        Args:
            server_name: Name of the server
            config: Server configuration

        Returns:
            True if discovery successful, False otherwise
        """
        logger.info(f"Discovering tools from server: {server_name}")

        # Create connection metadata object
        connection = ServerConnection(
            name=server_name,
            state=ConnectionState.CONNECTING
        )
        self.connections[server_name] = connection

        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env or {}
            )

            # Use temporary connection for discovery
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize
                    await session.initialize()

                    # Discover tools
                    tools_response = await session.list_tools()
                    connection.tools = [
                        MCPTool(
                            name=tool.name,
                            description=tool.description or "",
                            input_schema=tool.inputSchema,
                            server_name=server_name
                        )
                        for tool in tools_response.tools
                    ]
                    logger.info(f"Discovered {len(connection.tools)} tools from {server_name}")

                    # Discover resources (optional)
                    try:
                        resources_response = await session.list_resources()
                        connection.resources = [
                            MCPResource(
                                uri=resource.uri,
                                name=resource.name,
                                description=resource.description,
                                mime_type=resource.mimeType,
                                server_name=server_name
                            )
                            for resource in resources_response.resources
                        ]
                        logger.info(f"Discovered {len(connection.resources)} resources from {server_name}")
                    except Exception as e:
                        logger.debug(f"No resources from {server_name}: {e}")

                    # Discover prompts (optional)
                    try:
                        prompts_response = await session.list_prompts()
                        connection.prompts = [
                            MCPPrompt(
                                name=prompt.name,
                                description=prompt.description,
                                arguments=prompt.arguments,
                                server_name=server_name
                            )
                            for prompt in prompts_response.prompts
                        ]
                        logger.info(f"Discovered {len(connection.prompts)} prompts from {server_name}")
                    except Exception as e:
                        logger.debug(f"No prompts from {server_name}: {e}")

            # Connection closed cleanly - mark as available
            connection.state = ConnectionState.CONNECTED
            return True

        except Exception as e:
            logger.error(f"Failed to discover tools from {server_name}: {e}")
            connection.state = ConnectionState.ERROR
            connection.error = str(e)
            return False

    async def connect_server(self, server_name: str, config: ServerConfig) -> bool:
        """
        DEPRECATED: Use discover_server_tools() instead.

        This method attempted to maintain persistent connections but fails
        due to async context manager lifecycle issues. Use per-request
        connections via call_tool() instead.

        Args:
            server_name: Name of the server
            config: Server configuration

        Returns:
            True if connected successfully, False otherwise
        """
        logger.info(f"Connecting to server: {server_name}")

        # Create connection object
        connection = ServerConnection(
            name=server_name,
            state=ConnectionState.CONNECTING
        )
        self.connections[server_name] = connection

        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env or {}
            )

            # Connect to server using stdio transport
            # Use proper nested async with to ensure correct lifecycle
            stdio_ctx = stdio_client(server_params)
            read, write = await stdio_ctx.__aenter__()
            connection.stdio_context = stdio_ctx

            # Create and enter session context
            session_ctx = ClientSession(read, write)
            await session_ctx.__aenter__()
            connection.session = session_ctx

            # Initialize the session
            await session_ctx.initialize()

            # Update connection state
            connection.state = ConnectionState.CONNECTED
            logger.info(f"Successfully connected to {server_name}")

            # Discover capabilities
            await self._discover_capabilities(server_name, connection)

            return True

        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {e}")
            connection.state = ConnectionState.ERROR
            connection.error = str(e)

            # Clean up on error
            if connection.session:
                try:
                    await connection.session.__aexit__(type(e), e, e.__traceback__)
                except:
                    pass
            if connection.stdio_context:
                try:
                    await connection.stdio_context.__aexit__(type(e), e, e.__traceback__)
                except:
                    pass

            return False

    async def _discover_capabilities(self, server_name: str, connection: ServerConnection):
        """
        Discover capabilities (tools/resources/prompts) from a server.

        Args:
            server_name: Name of the server
            connection: Server connection object
        """
        if not connection.session:
            return

        try:
            # Discover tools
            tools_response = await connection.session.list_tools()
            connection.tools = [
                MCPTool(
                    name=tool.name,
                    description=tool.description or "",
                    input_schema=tool.inputSchema,
                    server_name=server_name
                )
                for tool in tools_response.tools
            ]
            logger.info(f"Discovered {len(connection.tools)} tools from {server_name}")

            # Discover resources
            try:
                resources_response = await connection.session.list_resources()
                connection.resources = [
                    MCPResource(
                        uri=resource.uri,
                        name=resource.name,
                        description=resource.description,
                        mime_type=resource.mimeType,
                        server_name=server_name
                    )
                    for resource in resources_response.resources
                ]
                logger.info(f"Discovered {len(connection.resources)} resources from {server_name}")
            except Exception as e:
                logger.debug(f"No resources from {server_name}: {e}")

            # Discover prompts
            try:
                prompts_response = await connection.session.list_prompts()
                connection.prompts = [
                    MCPPrompt(
                        name=prompt.name,
                        description=prompt.description,
                        arguments=prompt.arguments,
                        server_name=server_name
                    )
                    for prompt in prompts_response.prompts
                ]
                logger.info(f"Discovered {len(connection.prompts)} prompts from {server_name}")
            except Exception as e:
                logger.debug(f"No prompts from {server_name}: {e}")

        except Exception as e:
            logger.error(f"Failed to discover capabilities from {server_name}: {e}")

    async def discover_all_tools(self) -> List[MCPTool]:
        """
        Discover and aggregate tools from all connected servers.

        Returns:
            List of all available tools across all servers
        """
        # Lazy initialization
        if not self._initialized:
            await self.initialize()

        all_tools = []

        for server_name, connection in self.connections.items():
            if connection.state == ConnectionState.CONNECTED:
                all_tools.extend(connection.tools)

        logger.info(f"Total tools available: {len(all_tools)}")
        return all_tools

    async def discover_all_resources(self) -> List[MCPResource]:
        """
        Discover and aggregate resources from all connected servers.

        Returns:
            List of all available resources across all servers
        """
        # Lazy initialization
        if not self._initialized:
            await self.initialize()

        all_resources = []

        for server_name, connection in self.connections.items():
            if connection.state == ConnectionState.CONNECTED:
                all_resources.extend(connection.resources)

        logger.info(f"Total resources available: {len(all_resources)}")
        return all_resources

    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """
        Get a specific tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            MCPTool if found, None otherwise
        """
        for connection in self.connections.values():
            for tool in connection.tools:
                if tool.name == tool_name:
                    return tool
        return None

    def find_server_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Find which server provides a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Server name if found, None otherwise
        """
        tool = self.get_tool(tool_name)
        return tool.server_name if tool else None

    async def call_tool(
        self,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> ToolCallResult:
        """
        Call a tool by routing to the appropriate server.

        Uses per-request connection pattern: creates a fresh connection,
        calls the tool, and cleanly exits. This ensures proper async
        lifecycle management.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            ToolCallResult with the result
        """
        # Lazy initialization (for tool discovery only)
        if not self._initialized:
            await self.initialize()

        # Find which server provides this tool
        server_name = self.find_server_for_tool(tool_name)

        if not server_name:
            return ToolCallResult(
                success=False,
                content=None,
                error=f"Tool '{tool_name}' not found in any server",
                is_error=True
            )

        # Get server config
        server_config = self.config_loader.get_server(server_name)
        if not server_config:
            return ToolCallResult(
                success=False,
                content=None,
                error=f"Server '{server_name}' configuration not found",
                server_name=server_name,
                is_error=True
            )

        # Per-request connection: create fresh connection for this call
        try:
            logger.info(f"Calling tool '{tool_name}' on server '{server_name}' (per-request connection)")

            # Create server parameters
            server_params = StdioServerParameters(
                command=server_config.command,
                args=server_config.args,
                env=server_config.env or {}
            )

            # Use proper nested async with - everything in one task
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()

                    # Call the tool
                    result = await session.call_tool(
                        tool_name,
                        arguments=arguments or {}
                    )

                    return ToolCallResult(
                        success=not result.isError if hasattr(result, 'isError') else True,
                        content=result.content,
                        error=None,
                        server_name=server_name,
                        is_error=result.isError if hasattr(result, 'isError') else False
                    )
            # Clean exit - all context managers exit in same task ✅

        except Exception as e:
            # Extract more detailed error information
            error_msg = str(e)

            # For ExceptionGroup/TaskGroup errors, try to extract the underlying exception
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg = f"{error_msg} (caused by: {e.__cause__})"
            if hasattr(e, 'exceptions'):
                # ExceptionGroup - extract first exception and drill down to root cause
                def extract_deepest_error(ex):
                    """Recursively extract the deepest error message"""
                    if hasattr(ex, 'exceptions') and ex.exceptions:
                        # Nested ExceptionGroup - go deeper
                        return extract_deepest_error(ex.exceptions[0])
                    return str(ex)

                # Get the deepest error from the first exception
                deepest_error = extract_deepest_error(e.exceptions[0])

                # Check if it's a GitHub validation error and make it more readable
                if "Validation Failed" in deepest_error or "Validation Error" in deepest_error:
                    # Extract just the meaningful part
                    query_str = str(arguments.get("query", "")) if isinstance(arguments, dict) else ""
                    if "user:@" in query_str and "user:@me" not in query_str:
                        error_msg = (
                            f"❌ GitHub API Validation Error\n\n"
                            f"{deepest_error}\n\n"
                            f"💡 Tip: Use 'user:username' not 'user:@username'\n"
                            f"   - For authenticated user: user:@me\n"
                            f"   - For other users: user:ttware (no @ symbol)"
                        )
                    else:
                        error_msg = f"❌ GitHub API Validation Error\n\n{deepest_error}"
                else:
                    error_msg = deepest_error

            logger.error(f"Error calling tool '{tool_name}': {error_msg}", exc_info=True)

            return ToolCallResult(
                success=False,
                content=None,
                error=error_msg,
                server_name=server_name,
                is_error=True
            )

    async def shutdown(self):
        """
        Shutdown the client manager.

        Note: With per-request connections, there are no persistent
        connections to close. This method is kept for API compatibility.
        """
        logger.info("Shutting down MCP Client Manager")

        # Mark all connections as disconnected
        for server_name, connection in self.connections.items():
            connection.state = ConnectionState.DISCONNECTED
            logger.debug(f"Marked {server_name} as disconnected")

        logger.info("MCP Client Manager shutdown complete")

    def is_connected(self) -> bool:
        """Check if any servers are connected"""
        return any(
            conn.state == ConnectionState.CONNECTED
            for conn in self.connections.values()
        )

    def get_connection_status(self) -> Dict[str, str]:
        """Get connection status for all servers"""
        return {
            name: conn.state.value
            for name, conn in self.connections.items()
        }
