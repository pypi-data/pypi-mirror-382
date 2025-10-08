import asyncio
import os

from pocket_agent import PocketAgent, AgentConfig


#########################################################
# Initialize the weather agent
#########################################################
def create_weather_agent():
    # Agent config for the weather agent
    weather_agent_config = AgentConfig(
        llm_model="gpt-5-nano",
        name="Weather_Reporter",
        role_description="provide accurate weather information for cities",
        system_prompt="You are a weather reporter who answers user questions and uses the weather tools when applicable"
    )

    # MCP config for the weather agent
    weather_mcp_config = {
        "mcpServers": {
            "weather": {
                "transport": "stdio",
                "command": "python",
                "args": ["server.py"],
                "cwd": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "servers", "simple_weather")
            }
        }
    }

    # Create and return the weather agent instance
    weather_agent = PocketAgent(
        agent_config=weather_agent_config,
        mcp_config=weather_mcp_config
    )
    return weather_agent


if __name__ == "__main__":
    weather_agent = create_weather_agent()
    server = weather_agent.as_mcp_server()
    server.run(show_banner=False)