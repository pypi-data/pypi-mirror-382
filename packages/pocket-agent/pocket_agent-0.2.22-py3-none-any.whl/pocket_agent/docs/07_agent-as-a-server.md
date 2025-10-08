# Pocket Agent as an MCP Server

Any Pocket Agent instance can be used as a standalone MCP server to be integrated with external frameworks.

This example shows how to set up a Pocket Agent as a FastMCP server:

```python
agent = PocketAgent(
    agent_config= # AgentConfig,
    mcp_config= # MCP server config
    )

mcp_server = agent.as_mcp_server() # returns an instance of FastMCP
```

The MCP server generated in the above example will have a single `{agent_name}-message` tool. See [Multi-Agent Systems - Sub-Agent Tool Integration](multi-agent.md#sub-agent-tool-integration) for more details on the `message` tool as it is the same.

*Note: Even agents with sub-agents can be run as MCP Servers*
