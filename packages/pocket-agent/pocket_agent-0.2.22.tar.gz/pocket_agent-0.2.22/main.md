## MCP
Model Context Protocol (MCP) is a standard protocol to give LLM agent access to various toolboxes (MCP servers).

# LLM Agents
LLM agents are simply defined as some operation loop in which an LLM is used at each step to decide the next operation.
Because the LLM agent should not need to care how tools are being called, agents should be implemented separately from MCP clients/servers.

## What the LLM Agent should implement
The LLM agent should be defined by:
 - The model used to drive the agent
 - The system prompt (instructions) for the agent
 - The message history (context) for the agent
 - The tools which the agent has access to
 - The process by which the agent functions:
     - Simple tool calling loop until some end loop tool is used or N-steps are reached
     - A more complex orchestrated process

Therefore implementation of the agent should include:
 - Formatting of messages to be fed to the agent
 - Use of an MCP client
 - Verification that tool calls and results are formatted correctly
 - The stepping process which the agent should follow


# MCP Clients
MCP clients are the mechanism with which LLM agents connect to MCP servers and use their tools. This is where the details of how tools are called matters.

## What the Client should implement
The Client must handle the tool calls passed from the agent to the MCP servers as well as the tool results passed from the MCP servers to the agent.
Therefore Clients should implement the following:
 - Creation of an MCP client object which connects to the appropriate servers [as documented here](https://gofastmcp.com/clients/client)
 - Conversion of tool calling structures
     - Most LLMs use the Openai tool calling structure which needs to be converted to the mcp structure before being sent to mcp servers.
     - litellm has an implementation of such conversion: 
        ```python
        from litellm.experimental_mcp_client.tools import (
                transform_mcp_tool_to_openai_tool,
                transform_openai_tool_call_request_to_mcp_tool_call_request,
            )
        ```
 - Calling tools
    
 - Handling tool calling errors
     - If a tool call fails


### Connection Protocol
Various protocols are allowed for cnnection to MCP servers (STDIO, Streamable-http, etc.)


# MCP Servers

## Building Servers
### Error Handling
In most cases you want to handle errors which occur during a tool 

### Using Structured Tool Responses