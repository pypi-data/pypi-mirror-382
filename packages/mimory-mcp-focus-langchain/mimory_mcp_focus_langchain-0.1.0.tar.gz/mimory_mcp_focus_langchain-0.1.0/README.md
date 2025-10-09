# mimory-mcp-focus-langchain

[![PyPI version](https://badge.fury.io/py/mimory-mcp-focus-langchain.svg)](https://badge.fury.io/py/mimory-mcp-focus-langchain)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

LangChain integration for [mimory-mcp-focus](https://github.com/mimoryinc/mimory-mcp-focus), providing focus capabilities to your LangChain MCP implementations.

## Overview

`mimory-mcp-focus-langchain` extends LangChain's MCP (Model Context Protocol) integration with powerful focus capabilities. It allows you to:

- **Restrict tool access** to specific MCP tools
- **Control parameter values** with whitelists and ranges
- **Apply composite focus** for complex tool-specific restrictions
- **Integrate seamlessly** with LangChain's tool ecosystem

## Installation

```bash
pip install mimory-mcp-focus-langchain
```

### Dependencies

This package requires:
- Python 3.10+
- [mimory-mcp-focus](https://github.com/mimoryinc/mimory-mcp-focus) - Core focus functionality
- [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) - LangChain MCP integration
- [langchain-core](https://github.com/langchain-ai/langchain) - LangChain core functionality

## Quick Start

### Basic Usage with FocusMultiServerMCPClient

```python
import asyncio
from mim_mcp_focus_langchain import FocusMultiServerMCPClient
from langchain_mcp_adapters.sessions import Connection

async def main():
    # Define MCP server connections
    connections = {
        "everything": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-everything"]
        },
        "time": {
            "transport": "stdio", 
            "command": "python",
            "args": ["-m", "mcp_server_time"]
        }
    }
    
    # Configure focus restrictions
    focus_configs = {
        "everything": {
            "focus_tools": ["echo", "add"],  # Only allow these tools
            "focus_params": {
                "message": ["hello", "world"],  # Restrict message values
                "a": ["range:1-10"]  # Restrict 'a' parameter to 1-10
            }
        },
        "time": {
            "focus_tools": ["get_current_time"],  # Only allow time tool
            "focus_params": {
                "timezone": ["America/New_York", "Europe/London"]  # Restrict timezones
            }
        }
    }
    
    # Create focus-enabled client
    client = FocusMultiServerMCPClient(connections, focus_configs)
    
    # Get tools with focus applied
    tools = await client.get_tools()
    
    # Use tools in your LangChain application
    for tool in tools:
        print(f"Tool: {tool.name} - {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Core FocusClient with LangChain

```python
import asyncio
from mimory_mcp_focus import focus_client_simple, focus_client_composite
from langchain_mcp_adapters.sessions import Connection, create_session
from langchain_mcp_adapters.tools import load_mcp_tools

async def main():
    # Create MCP connection
    connection = {
        "transport": "stdio",
        "command": "npx", 
        "args": ["-y", "@modelcontextprotocol/server-everything"]
    }
    
    # Create focus-enabled session
    async with create_session(connection) as session:
        await session.initialize()
        
        # Apply focus restrictions using simple focus
        focus_session = focus_client_simple(
            session,
            focus_tools=["echo", "add"],
            focus_params={
                "message": ["hello", "world"],
                "a": ["range:1-10"]
            },
            strict=False
        )
        
        # Load tools with focus applied
        tools = await load_mcp_tools(focus_session)
        
        # Use tools in LangChain
        for tool in tools:
            print(f"Tool: {tool.name}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Focus Configuration

### Simple Focus

Restrict tools and parameters globally:

```python
focus_config = {
    "focus_tools": ["tool1", "tool2"],  # Allowed tools
    "focus_params": {
        "param1": ["value1", "value2"],  # Allowed values
        "param2": ["range:1-100"]  # Numeric range
    },
    "focus_type": "simple",  # How the focus params are encoded
    "strict": False  # Whether to enforce strict mode
}
```

### Composite Focus

Apply different restrictions per tool:

```python
focus_config = {
    "focus": {
        "tool1": {
            "param1": ["value1", "value2"],
            "param2": ["range:1-10"]
        },
        "tool2": {
            "param3": ["value3", "value4"],
            "param4": ["value5"]
        }
    },
    "focus_type": "composite",  # How the focus params are encoded
    "strict": True
}
```

### Focus Configuration Structure

The `focus_config` dictionary supports the following structure:

**For Simple Focus (`focus_type: "simple"`):**
- `focus_tools`: List of allowed tool names (use `["*"]` to allow all tools)
- `focus_params`: Dictionary mapping parameter names to allowed values
- `focus_type`: Must be `"simple"`
- `strict`: Boolean indicating whether to enforce strict mode

**For Composite Focus (`focus_type: "composite"`):**
- `focus`: Dictionary mapping tool names to their parameter restrictions
- `focus_type`: Must be `"composite"`
- `strict`: Boolean indicating whether to enforce strict mode

**Parameter Value Formats:**
- Exact values: `["value1", "value2"]`
- Numeric ranges: `["range:1-100"]` (inclusive)
- Wildcard: `["*"]` (allows any value)

## API Reference

### FocusMultiServerMCPClient

Main class for focus-enabled multi-server MCP operations.

#### Constructor

```python
FocusMultiServerMCPClient(
    connections: Optional[Dict[str, Connection]] = None,
    focus_configs: Optional[Dict[str, Dict[str, Any]]] = None
)
```

**Parameters:**
- `connections`: Dictionary mapping server names to connection configurations
- `focus_configs`: Dictionary mapping server names to focus configurations

#### Methods

##### `async get_tools(server_name: Optional[str] = None) -> List[BaseTool]`

Get LangChain tools with focus restrictions applied.

**Parameters:**
- `server_name`: Optional name of specific server. If None, returns tools from all servers.

**Returns:**
- List of LangChain tools with focus applied

##### `async session(server_name: str, *, auto_initialize: bool = True) -> AsyncIterator[ClientSession]`

Create a focus-enabled MCP session.

**Parameters:**
- `server_name`: Name of the server to connect to
- `auto_initialize`: Whether to automatically initialize the session

**Returns:**
- Async context manager yielding a focus-enabled ClientSession

## Examples

### Example 1: Basic Tool Restriction

```python
# examples/basic_restriction.py
import asyncio
from mim_mcp_focus_langchain import FocusMultiServerMCPClient

async def main():
    connections = {
        "everything": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-everything"]
        }
    }
    
    focus_configs = {
        "everything": {
            "focus_tools": ["echo"],  # Only allow echo tool
            "focus_params": {
                "message": ["hello", "world", "test"]  # Restrict message values
            },
            "focus_type": "simple",
            "strict": False
        }
    }
    
    client = FocusMultiServerMCPClient(connections, focus_configs)
    tools = await client.get_tools()
    
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Multi-Server with Composite Focus

```python
# examples/multi_server_composite.py
import asyncio
from mim_mcp_focus_langchain import FocusMultiServerMCPClient

async def main():
    connections = {
        "everything": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-everything"]
        },
        "time": {
            "transport": "stdio",
            "command": "python", 
            "args": ["-m", "mcp_server_time"]
        }
    }
    
    focus_configs = {
        "everything": {
            "focus": {
                "echo": {
                    "message": ["hello", "world"]
                },
                "add": {
                    "a": ["range:1-5"],
                    "b": ["range:1-5"]
                }
            },
            "focus_type": "composite",
            "strict": False
        },
        "time": {
            "focus_tools": ["get_current_time"],
            "focus_params": {
                "timezone": ["America/New_York", "Europe/London"]
            },
            "focus_type": "simple",
            "strict": False
        }
    }
    
    client = FocusMultiServerMCPClient(connections, focus_configs)
    tools = await client.get_tools()
    
    print("Available tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 3: Using with LangChain Agents

```python
# examples/langchain_agent.py
import asyncio
from mim_mcp_focus_langchain import FocusMultiServerMCPClient
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI

async def main():
    # Setup MCP connections with focus
    connections = {
        "everything": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-everything"]
        }
    }
    
    focus_configs = {
        "everything": {
            "focus_tools": ["echo", "add"],
            "focus_params": {
                "message": ["hello", "world", "test"],
                "a": ["range:1-10"],
                "b": ["range:1-10"]
            },
            "focus_type": "simple",
            "strict": False
        }
    }
    
    # Create focus-enabled client
    client = FocusMultiServerMCPClient(connections, focus_configs)
    
    # Get tools
    tools = await client.get_tools()
    
    # Create LangChain agent
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    agent = create_tool_calling_agent(llm, tools, "You are a helpful assistant with access to focused MCP tools.")
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Run agent
    result = await agent_executor.ainvoke({"input": "Echo 'hello' and add 5 + 3"})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Error Handling

The library uses standard Python exceptions for error handling. Focus-related errors will be raised as appropriate exceptions that you can catch and handle as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [LangChain Python SDK](https://github.com/langchain-ai/langchain)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [mimory-mcp-focus](https://github.com/mimoryinc/mimory-mcp-focus)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## Author

**Travis McQueen** - [oss@mimory.io](mailto:oss@mimory.io)

## Support

For support, please open an issue on [GitHub](https://github.com/mimoryinc/mimory-mcp-focus-langchain/issues).
