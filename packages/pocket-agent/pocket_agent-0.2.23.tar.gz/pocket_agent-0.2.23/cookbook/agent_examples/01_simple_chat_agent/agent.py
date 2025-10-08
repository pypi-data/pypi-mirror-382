import asyncio
from pocket_agent import PocketAgent, AgentConfig
from typing import Dict, Any


async def main():
    import os

    mcp_config = {
        "mcpServers": {
            "weather": {
                "transport": "stdio",
                "command": "python",
                "args": ["server.py"],
                "cwd": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "servers", "simple_weather")
            }
        }
    }
    # Configure agent  
    config = AgentConfig(
        llm_model="gpt-5-nano",
        system_prompt="You are a helpful assistant who answers user questions and uses provided tools when applicable"
    )
    # Create and run agent
    agent = PocketAgent(
        agent_config=config,
        mcp_config=mcp_config
    )
    
    await agent.run("Hello! What is the weather in Tokyo?")
    await agent.run("Get the 3 day forecast for tokyo, sydney and london and make them into a table")

if __name__ == "__main__":
    asyncio.run(main())