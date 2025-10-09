"""Focus-enabled MCP clients for LangChain integration."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ValidationError

from langchain_core.tools import BaseTool, ToolException
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import Connection, create_session
from langchain_mcp_adapters.tools import load_mcp_tools, _convert_call_tool_result

from mcp import ClientSession
from mcp.types import CallToolResult, TextContent

from mimory_mcp_focus import SimpleFocus, CompositeFocus, FocusedClientSession, focus_client_simple, focus_client_composite, check_tool_args_focus

async def _load_mcp_tools_with_focus(
    session: ClientSession | None,
    *,
    connection: Connection,
    server_name: str | None = None,
    focus_config: Dict[str, Any]
) -> List[BaseTool]:
    """Load MCP tools with focus restrictions applied.
    
    This is a custom version of load_mcp_tools that creates focus-enabled sessions
    for each tool call, ensuring that focus restrictions are properly applied.
    """
    from langchain_mcp_adapters.tools import _list_all_tools
    
    # Create a temporary session to list tools
    async with create_session(connection) as temp_session:
        await temp_session.initialize()

        # Get the focus type
        focus_type = focus_config.get('focus_type', 'simple')

        # Enforce focus on the temporary session
        if focus_type == 'composite':
            focus_session = focus_client_composite(
                temp_session,
                focus=focus_config.get('focus'),
                strict=focus_config.get('strict', False)
            )
        else:
            focus_session = focus_client_simple(
                temp_session,
                focus_tools=focus_config.get('focus_tools'),
                focus_params=focus_config.get('focus_params'),
                strict=focus_config.get('strict', False)
            )        
        tools = await _list_all_tools(focus_session)
    
    # Create focus-enabled tools
    focus_tools_list = []
    for tool in tools:
        # Create a custom tool that uses focus-enabled sessions
        focus_tool = _create_focus_tool(
            session=None,
            tool=tool,
            connection=connection,
            server_name=server_name, 
            focus_config=focus_config
        )
        focus_tools_list.append(focus_tool)
    
    return focus_tools_list


def _create_focus_tool(
    session: ClientSession | None,
    *,
    tool,
    connection: Connection,
    server_name: str | None = None,
    focus_config: Dict[str, Any]
) -> BaseTool:
    """Create a LangChain tool that uses focus-enabled sessions."""
    from langchain_core.tools import StructuredTool
    from langchain_mcp_adapters.tools import _convert_call_tool_result, convert_mcp_tool_to_langchain_tool

    if session is None and connection is None:
        msg = "Either a session or a connection config must be provided"
        raise ValueError(msg)

    # Convert the MCP tool to a LangChain tool
    mcp_tool = convert_mcp_tool_to_langchain_tool(
        session=session,
        tool=tool,
        connection=connection,
    )

    # Now that we have the structured tool, we need to make sure a focus session is used for each tool call
    async def focus_enabled_coroutine(**arguments: Dict[str, Any]) -> tuple[str | list[str], list | None]:
        # Set up a call tool result for the tool call
        call_tool_result = CallToolResult(
            content=[TextContent(type="text", text="Tool call result")],
            isError=False
        )

        print(f"Checking arguments with focus restrictions for tool {mcp_tool.name}")
        print(f"Arguments: {arguments}")
        
        # Check arguments with focus restrictions
        try:
            check_tool_args_focus(mcp_tool.name, arguments or {}, focus_config, focus_config.get('focus_type', 'simple'))
        except Exception as e:
            call_tool_result.isError = True
            call_tool_result.content = [TextContent(type="text", text=repr(e))]

        # Checks passed so call the original coroutine
        if not call_tool_result.isError:
            return await mcp_tool.coroutine(**arguments)
        
        # Checks failed so return the error result
        return _convert_call_tool_result(call_tool_result)
    
    meta = tool.meta if hasattr(tool, "meta") else None
    base = tool.annotations.model_dump() if tool.annotations is not None else {}
    meta = {"_meta": meta} if meta is not None else {}
    metadata = {**base, **meta} or None
    
    return StructuredTool(
        name=mcp_tool.name,
        description=mcp_tool.description or "",
        args_schema=mcp_tool.args_schema,
        coroutine=focus_enabled_coroutine,
        response_format=mcp_tool.response_format,
        metadata=mcp_tool.metadata,
    )


class FocusMultiServerMCPClient:
    """Focus-enabled wrapper around MultiServerMCPClient.
    
    This class wraps the standard MultiServerMCPClient and adds focus capabilities
    to tool calls while proxying all other functionality.
    """
    
    def __init__(
        self,
        connections: Optional[Dict[str, Connection]] = None,
        focus_configs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        """Initialize the focus-enabled multi-server MCP client.
        
        Args:
            connections: Dictionary mapping server names to connection configurations
            focus_configs: Dictionary mapping server URIs to focus configurations.
                          Each config can contain:
                          - 'focus_tools': List of allowed tools
                          - 'focus_params': Dict of parameter restrictions
                          - 'focus': Composite focus dict (alternative to above)
                          - 'focus_type': Type of focus to use (simple or composite)
                          - 'strict': Whether to use strict mode
        """
        self._base_client = MultiServerMCPClient(connections)

        if focus_configs is not None:
            # Validate each focus_config and ensure all connections have a config
            self.focus_configs = self._validate_and_complete_focus_configs(focus_configs)
        else:
            # If no focus configs are passed, create a default config for each server with all tools and parameters allowed
            self.focus_configs = {server_name: {
                "focus_tools": ["*"],
                "focus_params": {},
                "focus_type": "simple",
                "strict": False
            } for server_name in self._base_client.connections.keys()}
    
    def _validate_and_complete_focus_configs(self, focus_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Validate each focus_config against the appropriate schema and ensure all connections have a config.
        
        Args:
            focus_configs: Dictionary mapping server names to focus configurations
            
        Returns:
            Complete focus_configs dictionary with validated configs and defaults for missing connections
            
        Raises:
            ValueError: If any focus_config fails validation
        """
        validated_configs = {}
        
        # Validate provided focus configs
        for server_name, focus_config in focus_configs.items():
            try:
                # Get the focus type, defaulting to 'simple' if not specified
                focus_type = focus_config.get('focus_type', 'simple')
                
                # Validate against the appropriate schema
                if focus_type == 'simple':
                    # For simple focus, validate using SimpleFocus schema
                    SimpleFocus(**focus_config)
                elif focus_type == 'composite':
                    # For composite focus, validate using CompositeFocus schema
                    CompositeFocus(**focus_config)
                else:
                    raise ValueError(f"Invalid focus_type '{focus_type}' for server '{server_name}'. Must be 'simple' or 'composite'.")
                
                # If validation passes, add to validated configs
                validated_configs[server_name] = focus_config
                
            except ValidationError as e:
                # Re-raise with more context about which server failed
                raise ValueError(f"Focus config validation failed for server '{server_name}': {e}")
            except Exception as e:
                # Handle any other validation errors
                raise ValueError(f"Focus config validation failed for server '{server_name}': {e}")
        
        # Create default broad permissions config
        default_config = {
            "focus_tools": ["*"],
            "focus_params": {},
            "focus_type": "simple",
            "strict": False
        }
        
        # Add default config for any connections that don't have a focus config
        for server_name in self._base_client.connections.keys():
            if server_name not in validated_configs:
                validated_configs[server_name] = default_config.copy()
        
        return validated_configs
    
    def __getattr__(self, name: str) -> Any:
        """Proxy all other method calls to the base MultiServerMCPClient."""
        return getattr(self._base_client, name)
    
    @asynccontextmanager
    async def session(
        self,
        server_name: str,
        *,
        auto_initialize: bool = True,
    ) -> AsyncIterator[ClientSession]:
        """Connect to an MCP server and initialize a focus-enabled session.
        
        Args:
            server_name: Name to identify this server connection
            auto_initialize: Whether to automatically initialize the session
            
        Yields:
            A focus-enabled ClientSession
        """
        async with self._base_client.session(server_name, auto_initialize=auto_initialize) as base_session:
            # Get focus config for this server
            focus_config = self._get_focus_config_for_server(server_name)
            
            if focus_config:
                # Create focus-enabled session
                focus_session = self._create_focus_session(base_session, focus_config)
                yield focus_session
            else:
                # No focus config, create a focus-enabled session with all tools and parameters allowed
                # Focus configs should exist for each server as we create a default config for each server with all tools and parameters allowed
                # However, just in case, we'll protect against the case where no focus config exists
                focus_session = focus_client_simple(
                    base_session,
                    focus_tools=["*"],
                    focus_params={},
                    strict=focus_config.get('strict', False)
                )
                yield focus_session
    
    def _get_focus_config_for_server(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get focus configuration for a server.
        
        Args:
            server_name: Name of the server
            
        Returns:
            Focus configuration dict or None
        """
        # First try direct server name match
        if server_name in self.focus_configs:
            return self.focus_configs[server_name]
        
        # Try to match by server URI if available
        if server_name in self._base_client.connections:
            connection = self._base_client.connections[server_name]
            # Try to construct a URI-like key
            if hasattr(connection, 'get') and 'url' in connection:
                uri_key = connection['url']
                if uri_key in self.focus_configs:
                    return self.focus_configs[uri_key]
        
        return None
    
    def _create_focus_session(
        self, 
        base_session: ClientSession, 
        focus_config: Dict[str, Any]
    ) -> FocusedClientSession:
        """Create a focus-enabled session from base session and config.
        
        Args:
            base_session: The base MCP session
            focus_config: Focus configuration
            focus_type: Type of focus to use

        Returns:
            Focus-enabled session
        """
        strict = focus_config.get('strict', False)
        focus_type = focus_config.get('focus_type', 'simple')
        
        # Check if using composite focus format
        if focus_type == 'composite':
            # Effectively not focused
            broad_focus = {
                "*": {
                    "*" : ["*"]
                }
            }

            return focus_client_composite(
                base_session,
                focus=focus_config.get('focus', broad_focus),
                strict=strict
            )
        elif focus_type == 'simple':
            # Use standard focus format
            # If not provided, use default simple focus
            focus_tools = focus_config.get('focus_tools', ['*'])
            focus_params = focus_config.get('focus_params', {})
            
            return focus_client_simple(
                base_session,
                focus_tools=focus_tools,
                focus_params=focus_params,
                strict=strict
            )
        else:
            raise ValueError(f"Invalid focus type: {focus_type}")
    
    async def get_tools(self, *, server_name: Optional[str] = None) -> List[BaseTool]:
        """Get a list of all tools from connected servers with focus applied.
        
        Args:
            server_name: Optional name of the server to get tools from.
                        If None, all tools from all servers will be returned.
                        
        Returns:
            A list of LangChain tools with focus applied
        """
        if server_name is not None:
            return await self._get_tools_for_server(server_name)
        
        # Get tools from all servers
        all_tools: List[BaseTool] = []
        load_tool_tasks = []
        
        for server_name in self._base_client.connections.keys():
            load_tool_task = asyncio.create_task(
                self._get_tools_for_server(server_name)
            )
            load_tool_tasks.append(load_tool_task)
        
        tools_list = await asyncio.gather(*load_tool_tasks)
        for tools in tools_list:
            all_tools.extend(tools)
        
        return all_tools
    
    async def _get_tools_for_server(self, server_name: str) -> List[BaseTool]:
        """Get tools for a specific server with focus applied.
        
        Args:
            server_name: Name of the server
            
        Returns:
            List of LangChain tools
            
        """
        # Get connection for this server
        base_connection = self._base_client.connections[server_name]
        focus_config = self._get_focus_config_for_server(server_name)
        
        if focus_config:
            # Use our custom focus-enabled tool loader
            return await _load_mcp_tools_with_focus(
                None,
                connection=base_connection,
                server_name=server_name,
                focus_config=focus_config
            )
        else:
            # No focus config, use standard loader
            # Shouldn't happen as we create a focus session for each server
            # However, just in case, we'll return the tools from the base client
            return await load_mcp_tools(
                    None,
                    connection=base_connection,
                )
