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
