# Documentation of Pocket Agent

**Pocket Agent Version:** v0.2.1  
**Generated on:** 2025-09-19 13:19:26  
**Total Files:** 9

## 📋 Table of Contents

### 📖 Documentation

- 📖 [Index](#docs-00-index-md) *(47 lines)*
- 📖 [Getting Started](#docs-01-getting-started-md) *(64 lines)*
- 📖 [Core Concepts](#docs-02-core-concepts-md) *(90 lines)*
- 📖 [Hooks And Events](#docs-03-hooks-and-events-md) *(95 lines)*
- 📖 [Multi Model Support](#docs-04-multi-model-support-md) *(46 lines)*
- 📖 [Client](#docs-05-client-md) *(78 lines)*
- 📖 [Multi Agent](#docs-06-multi-agent-md) *(92 lines)*
- 📖 [Agent As A Server](#docs-07-agent-as-a-server-md) *(19 lines)*
- 📖 [Testing](#docs-08-testing-md) *(22 lines)*

**📊 Total Content:** 553 lines, 20,945 characters

---

# 📖 Documentation

## 📖 Index

**File:** `docs/00_index.md`  
**Stats:** 47 lines, 1,500 characters

# Pocket-Agent Documentation

Welcome to the comprehensive documentation for the Pocket-Agent framework! This documentation is organized into focused sections to help you find the information you need quickly.

## 📚 Documentation Sections

### [Getting Started](01_getting-started.md)
- Quick start guide for creating your first Pocket-Agent
- Basic examples and configuration
- Essential concepts for beginners

### [Core Concepts](02_core-concepts.md)
- PocketAgent base class and parameters
- The step method and execution flow
- Message management and conversation history

### [Hooks and Events](03_hooks-and-events.md)
- Hook system for customizing agent behavior
- Event system for frontend integration
- Custom hook implementations

### [Multi-Model Support](04_multi-model-support.md)
- Working with different LLM providers
- LiteLLM Router integration
- Model configuration and switching

### [PocketAgentClient](05_client.md)
- Client wrapper for MCP protocol
- Custom query parameters
- Tool error handling and custom parsers
- Server-initiated events

### [Multi-Agent Systems](06_multi-agent.md)
- Building complex multi-agent architectures
- Sub-agent tool integration
- Orchestrating multiple specialized agents

### [Agent-as-a-Server](07_agent-as-a-server.md)
- Using Pocket-Agent as an MCP server
- Integration with external frameworks
- Server setup and configuration

### [Testing](08_testing.md)
- Test suite overview
- Running tests with different options
- Coverage reporting


---

## 📖 Getting Started

**File:** `docs/01_getting-started.md`  
**Stats:** 64 lines, 2,049 characters

# Getting Started with Pocket-Agent

## Out of the Box Behavior

You can use PocketAgent's default behavior in 3 steps:

1. Configure the agent:
    ```python
    from pocket_agent import AgentConfig

    # Configure and run
    config = AgentConfig(
        llm_model="gpt-4",
        system_prompt="You are a helpful assistant."
    )

2. Define the [JSON MCP config](https://gofastmcp.com/integrations/mcp-json-configuration) to add mcp servers which the agent can access:
    ```python
    servers = {
        "mcpServers": {
            "weather_tools": {
                "transport": "stdio",
                "command": "python",
                "args": ["server.py"],
                "cwd": "path/to/server.py
            }
        }
    }
    ```

3. Initialize and run the agent:
    ```python
    import asyncio
    from pocket_agent import PocketAgent

    agent = PocketAgent(agent_config=config, mcp_config=servers)

    agent_final_answer = await agent.run("What's the weather fo London?")
    ```

In the above example, the `run` method will add the input as a user message, and then run in a loop generating new messages and running any tools called by the configured LLM until the configured LLM generates a response which does not have any tool calls.


## Creating Your First Custom Pocket-Agent (Quick Start)

The `run` method is intended to be reimplemented or extended for more complex use cases. For example, we can add a method to continually run the agent on user input until the user inputs `"quit"`:

```python
class SimpleAgent(PocketAgent):
    async def execute_user_input_loop(self):
        while True:
            user_input = input("Your input ('quit' to stop): ")
            if user_input.lower() == 'quit':
                break

            agent_result = await self.run(user_input)
```

This agent can be initialized in the following way (using the AgentConfig and MCP config from above):
```python
    agent = PocketAgent(agent_config=config, mcp_config=servers)
    await agent.execute_user_input_loop()
```


---

## 📖 Core Concepts

**File:** `docs/02_core-concepts.md`  
**Stats:** 90 lines, 3,309 characters

# Core Concepts

## 🏗️ **PocketAgent Base Class**

The `PocketAgent` is an abstract base class that provides the foundation for building custom agents. You inherit from this class and implement the `run()` method to define your agent's behavior.

```python
class MyAgent(PocketAgent):
    async def run(self, input: str) -> Union[FastMCPToolResult, dict, str]:
        # Your agent logic here
```

### PocketAgent Parameters:
```python
agent = PocketAgent(
    agent_config,   # Required: (AgentConfig) Instance of the AgentConfig class
    mcp_config,     # Optional (if sub_agents provided; Required otherwise): (dict or FastMCP) MCP Server or JSON MCP server configuration to pass tools to the agent
    router,         # Optional: A LiteLLM router instance to manage llm rate limits
    logger,         # Optional: A logger instance to capture logs
    hooks,          # Optional: (AgentHooks) optionally define custom behavior at common junction points
    sub_agents      # Optional: (list[PocketAgent]) list of Pocket-Agent's to be used as sub_agents
    **client_kwargs # Optional: additional kwargs passed to the PocketAgentClient

)
```

### AgentConfig Parameters:

```python
config = AgentConfig(
    llm_model="gpt-4",                    # Required: LLM model to use
    system_prompt="You are helpful...",   # Optional: System prompt for the agent
    agent_id="my-agent-123",              # Optional: Custom context ID
    allow_images=False,                   # Optional: Enable image input support (default: False)
    messages=[],                          # Optional: Initial conversation history (default: [])
    completion_kwargs={                   # Optional: Additional LLM parameters (default: {"tool_choice": "auto"})
        "tool_choice": "auto",
        "temperature": 0.7
    }
)
```

## 🔄 **The Step Method**

The `step()` method is the core execution unit that:
1. Gets an LLM response with available tools
2. Executes any tool calls in parallel
3. Updates conversation history

The output of calling the `step()` method is the StepResult
```python
@dataclass
class StepResult:
    llm_message: LitellmMessage                                 # The message generated by the llm including str content, tool calls, images, etc.
    tool_execution_results: Optional[list[ToolResult]] = None   # Results of any executed tools 
```

```python
# Single step execution
step_result = await agent.step()

# continue until no more tool calls
while step_result.llm_message.tool_calls is not None:
    step_result = await agent.step()
```

### Step Result Structure:
```python
{
    "llm_message": LitellmMessage,           # The LLM response
    "tool_execution_results": [ToolResult]   # Results from tool calls (if any)
}
```

## 💬 **Message Management**

Pocket Agent automatically adds llm generated messages and tool result messages in the `step()` function.
Input provided by a user can easily be managed using `add_user_message()` and should be done before calling the `step()` method:

```python
class Agent(PocketAgent)
    async def run(self):
        # Add user messages (with optional images)
        await agent.add_user_message("Hello!", image_base64s=["base64_image_data"])
        await self.step()

# Clear all messages except the system prompt
agent.reset_messages()
```


---

## 📖 Hooks And Events

**File:** `docs/03_hooks-and-events.md`  
**Stats:** 95 lines, 3,351 characters

# Hooks and Events

## 🪝 **Hook System**

Customize agent behavior at key execution points:

```python
@dataclass
class HookContext:
    """Context object passed to all hooks"""
    agent: 'PocketAgent'                                    # provides hooks access to the Agent instance
    metadata: Dict[str, Any] = field(default_factory=dict)  # additional metadata (default is empty)

class CustomHooks(AgentHooks):
    async def pre_step(self, context: HookContext):
        # executed before the llm response is generated in the step() method
        print("About to execute step")
    
    async def post_step(self, context: HookContext):
        # executed after all tool results (if any) are retrieved; This runs even if tool calling results in an error
        print("Step completed")
    
    async def pre_tool_call(self, context: HookContext, tool_call):
        # executed right before a tool is run
        print(f"Calling tool: {tool_call.name}")
        # Return modified tool_call or None
    
    async def post_tool_call(self, context: HookContext, tool_call, result):
        # executed right after a tool call result is retrieved from the PocketAgentClient
        print(f"Tool {tool_call.name} completed")
        return result  # Return modified result
    
    async def on_llm_response(self, context: HookContext, response):
        # executed right after a response message has been generated by the llm
        print("Got LLM response")
    
    async def on_event(self, event: AgentEvent):
        # Custom publishing of events useful for frontend integration

    async def on_tool_error(self, context: HookContext, tool_call: MCPCallToolRequestParams, error: Exception) -> Union[str, False]:
        # custom error handling described in more detail in PocketAgentClient docs 

    ####
    # PocketAgent uses a default result parser which will be replaced by this implementation if implemented
    ####
    async def on_tool_result(self, context: HookContext, tool_call: ChatCompletionMessageToolCall, tool_result: FastMCPCallToolResult) -> ToolResult:
        # custom parser for tool results described in more detail in PocketAgentClient docs

# Use custom hooks
agent = MyAgent(
    agent_config=config,
    mcp_config=mcp_config,
    hooks=CustomHooks()
)
```

By Default, the HookContext is created with the Agent instance and empty metadata but this behavior can be customized by implementing the `_create_hook_context` method in your custom agent:
```python
class Agent(PocketAgent):
    async def _create_hook_context(self) -> HookContext:
        return HookContext(
            agent=self,
            metadata={
                # custom metadata
            }
        )

```

## 📡 **Event System**

PocketAgent includes an AgentEvent type:

```python
@dataclass
class AgentEvent:
    event_type: str  # e.g., "new_message"
    data: dict       # Event-specific data
```

By default, events are automatically emitted when any new message is added to the message history:
- llm message
- tool result message
- user message

You can easily add `on_event` calls with custom AgentEvents in other hooks if necessary:
```python
class CustomHooks(AgentHooks):
    async def pre_tool_call(self, context, tool_call):
        event = AgentEvent(
            event_type="tool_call",
            data=tool_call
        )
```


---

## 📖 Multi Model Support

**File:** `docs/04_multi-model-support.md`  
**Stats:** 46 lines, 1,008 characters

# Multi-Model Support

## 🔧 **Multi-Model Support**

Works seamlessly with any LiteLLM-supported model:

```python
# OpenAI
config = AgentConfig(llm_model="gpt-4")

# Anthropic
config = AgentConfig(llm_model="anthropic/claude-3-sonnet-20240229")

# Local models
config = AgentConfig(llm_model="ollama/llama2")

# Azure OpenAI
config = AgentConfig(llm_model="azure/gpt-4")
```

## 🚏 **LiteLLM Router Integration**
To easily set rate limits or implement load balancing with multiple LLM API providers you can pass a [LiteLLM Router](https://docs.litellm.ai/docs/routing) instance to PocketAgent:

```python
from litellm import Router
router_info = {
    "models": [
        {
            "model_name": "gpt-5-nano",
            "litellm_params": {
                "model": "gpt-5-nano",
                "tpm": 3000000,
                "rpm": 5000
            }
        }
    ]
}

litellm_router = Router(model_list=router_info["models"])

agent = PocketAgent(
    router=litellm_router,
    # other args
)
```


---

## 📖 Client

**File:** `docs/05_client.md`  
**Stats:** 78 lines, 4,726 characters

# PocketAgentClient

Each PocketAgent instance initializes a PocketAgentClient which acts as a wrapper for the [FastMCP Client](https://gofastmcp.com/clients/client) to implement the standard mcp protocol features and some additional features.

## Custom Query Params

- Sending metadata such as a custom id to MCP servers is not handled well by the protocol (until [this](https://github.com/modelcontextprotocol/python-sdk/pull/1231) is merged). For now a workaround is to send metadata via query params to mcp servers using an http transport.

    ```python
    agent = PocketAgent(
        mcp_server_query_params = {
            "context_id": "1111"    # context_id will automatically be added to the server endpoint when sending a request
        }
    )
    ```

    *Note: Query params must use custom MCP middleware to be interpreted by servers*

## on_tool_error (hook)

- If a tool call fails and is not handled within the tool itself, it will result in a ToolError result. You can add custom handling of such errors using the `on_tool_error` hook method in `AgentHooks`. Any custom functionality should either return a `string` or `False`. If the method returns a `string`, the contents will be sent to the agent as the tool result, if the method returns `False` the ToolError will be raised an execution of the agent will stop.
The following handler is implemented by default to handle a common scenario where LLMs pass invalid parameters to tools resulting in an error:

    ```python
    class AgentHooks:
        async def on_tool_error(self, context: HookContext, tool_call: MCPCallToolRequestParams, error: Exception) -> Union[str, False]:
            if "unexpected_keyword_argument" in str(error):
                tool_call_name = tool_call.name
                tool_format = await context.agent.mcp_client.get_tool_input_format(tool_call_name)
                return "You supplied an unexpected keyword argument to the tool. \
                    Try again with the correct arguments as specified in expected format: \n" + tool_format
            return False
    ```

## tool_result_handler (hook)

- When a tool is called successfully it results in a [CallToolResult](https://github.com/jlowin/fastmcp/blob/09ae8f5cfdc62e6ac0bb7e6cc8ade621e9ebbf3e/src/fastmcp/client/client.py#L935). Most of the time, you will likely just want to parse the content which is a list of MCP content objects (i.e. [TextContent, ImageContent, etc](https://github.com/modelcontextprotocol/python-sdk/blob/c3717e7ad333a234c11d084c047804999a88706e/src/mcp/types.py#L662)). For this reason, the `PocketAgentClient` uses its default parser to parse these objects into content that can directly be fed to the agent as a message. Specifically, the default parser will return a ToolResult object:

    ```python
    return ToolResult(
        tool_call_id=tool_call.id,                              # ID of the original tool call (needed by most apis when passing tool results)
        tool_call_name=tool_call.name,                          # Name of the tool which the result is for
        tool_result_content=tool_result_content,                # Tool result content compatible with LiteLLM message format
        _extra={
            "tool_result_raw_content": tool_result_raw_content  # Unprocessed MCP tool result (unused by default)
        }
    )
    ```

    However, in some cases you may want to specifically parse structured content from a known tool in which case you can override the default parser by implementing the `on_tool_result` hook method in `AgentHooks`:

    ```python
    class CustomHooks(AgentHooks):
        async def on_tool_result(self, context: HookContext, tool_call: ChatCompletionMessageToolCall, tool_result: FastMCPCallToolResult) -> ToolResult:
            # your custom tool result parsing
    ```

## Server-initiated Events
- The MCP protocol implements numerous server-initiated events which should be handled by MCP clients. Each of these are documented here:
     - [Elicitation](https://gofastmcp.com/clients/elicitation)
     - [Logging](https://gofastmcp.com/clients/logging)
     - [Progress](https://gofastmcp.com/clients/progress)
     - [Sampling](https://gofastmcp.com/clients/sampling)
     - [Messages](https://gofastmcp.com/clients/messages)

By default, PocketAgent only implements the logging handler.

To define custom behavior for any other server initiated events they can be passed as additional arguments to the agent:
```python
agent = PocketAgent(
    elicitation_handler=your_elicitation_handler,
    log_handler=your_log_handler,
    progress_handler=your_progress_handler,
    sampling_handler=your_sampling_handler,
    message_handler=your_message_handler
)
```


---

## 📖 Multi Agent

**File:** `docs/06_multi-agent.md`  
**Stats:** 92 lines, 3,730 characters

# Multi-Agent Systems

PocketAgent natively supports multi-agent architectures where you can compose agents by passing other PocketAgent instances as sub-agents. Sub-agents are automatically converted to MCP tools that the main agent can call.

## Basic Multi-Agent Setup

```python
from pocket_agent import PocketAgent, AgentConfig

# Create a sub-agent with specialized capabilities
sub_agent_config = AgentConfig(
    llm_model="gpt-3.5-turbo",
    name="MathAgent", 
    role_description="A specialized agent for mathematical calculations",
    system_prompt="You are an expert mathematician. Solve mathematical problems step by step."
)

math_agent = PocketAgent(
    agent_config=sub_agent_config,
    mcp_config=math_mcp_config  # MCP config with math tools
)

# Create main agent with the sub-agent
main_config = AgentConfig(
    llm_model="gpt-4",
    name="MainAgent",
    system_prompt="You are a helpful assistant. Use the MathAgent when you need to solve math problems."
)

main_agent = PocketAgent(
    agent_config=main_config,
    mcp_config=main_mcp_config,  # Optional: main agent can have its own tools too
    sub_agents=[math_agent]      # Pass sub-agents as a list
)
```

## Multiple Sub-Agents

You can create complex multi-agent systems with multiple specialized sub-agents:

```python
# Create specialized sub-agents
research_agent = PocketAgent(
    agent_config=AgentConfig(
        llm_model="gpt-3.5-turbo",
        name="ResearchAgent",
        role_description="Specialized in web research and information gathering",
        system_prompt="You are a research specialist. Find and analyze information from web sources."
    ),
    mcp_config=research_mcp_config
)

analysis_agent = PocketAgent(
    agent_config=AgentConfig(
        llm_model="gpt-3.5-turbo", 
        name="AnalysisAgent",
        role_description="Specialized in data analysis and visualization",
        system_prompt="You are a data analyst. Analyze data and create visualizations."
    ),
    mcp_config=analysis_mcp_config
)

# Main orchestrator agent with multiple sub-agents
orchestrator = PocketAgent(
    agent_config=AgentConfig(
        llm_model="gpt-4",
        name="Orchestrator",
        system_prompt="You coordinate between specialized agents to complete complex tasks."
    ),
    sub_agents=[research_agent, analysis_agent],
    mcp_config=None            # mcp_config can be none if sub_agents are being used and the main agent doesn't need its own tools
)
```

## Sub-Agent Tool Integration

When you add sub-agents to a main agent, they are automatically exposed as tools with names formatted as `{agent_name}-message` with a single `message: str` argument. The main agent can call these tools to interact with sub-agents.

When a sub-agent tool is called, it will execute the agent's `run` method with the `message` tool call argument.
Therefore, **the `run` method of a sub-agent must accept one argument as an input message and return.**
Additionally, the `run` method must return either `None` or one of these types:
 - `str`
 - `dict`
 - Instance of [FastMCP's ToolResult](https://github.com/jlowin/fastmcp/blob/39a1e59bfd9a665fd961d18418c5addde94c3019/src/fastmcp/tools/tool.py#L66C7-L66C17)


## Sub-agent Execution Lock

In some cases the primary agent may invoke parallel calls to the same sub-agent. To avoid unexpected behavior in these scenarios, the sub-agent's `run` method is executed within a lock (i.e. only one invocation of a single agent's `run` method can execute at a time).

If the sub-agent is able to handle multiple tasks at once, a simple workaround to avoid bottlenecks due to synchronous execution of parallel tool calls to a sub-agent is to instruct the parent agent to combine


---

## 📖 Agent As A Server

**File:** `docs/07_agent-as-a-server.md`  
**Stats:** 19 lines, 705 characters

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


---

## 📖 Testing

**File:** `docs/08_testing.md`  
**Stats:** 22 lines, 567 characters

# Testing

Pocket Agent includes a comprehensive test suite covering all core functionality. The tests are designed to be fast and reliable using in-memory FastMCP servers and mocked LLM responses.

## Running Tests

The easiest way to run tests is using the provided test runner script:

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run with coverage reporting (Coverage reports are generated in `htmlcov/`)
python run_tests.py --coverage

# Run quick subset for development
python run_tests.py --quick
```


---

## 📊 Complete Dump Summary

### 📋 **Content Overview:**
- **📖 Documentation Files:** 9 files ✓
- **🔧 Source Code Files:** 0 files (excluded)
- **📏 Total Content:** 553 lines (20,945 characters)

### 🏗️ **Framework Architecture:**
- **🤖 Core Agent (`agent.py`)** - Main orchestration and lifecycle management
- **🔌 Client Layer (`client.py`)** - MCP server communication and tool execution  
- **🛠️ Utilities** - Logging and console formatting for developer experience
- **📦 Public API (`__init__.py`)** - Clean, simple imports for end users
- **⚙️ CLI Tools** - Documentation and source code dumping utilities

### 🚀 **Key Features:**
- Multi-agent orchestration and sub-agent support
- Async/await throughout for performance
- Comprehensive error handling and logging
- Hook system for extensibility
- Clean separation of concerns
- Complete documentation and examples

---

*This complete dump was generated by `pocket-dump` - documentation and source code dumping utility.*

**Need another dump?** Run: `pocket-dump <filename>`  
**Just source?** Run: `pocket-dump --source-only <filename>`  
**Just docs?** Run: `pocket-dump --docs-only <filename>`
