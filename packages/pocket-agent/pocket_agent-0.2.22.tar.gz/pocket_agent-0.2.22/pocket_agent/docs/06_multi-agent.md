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
