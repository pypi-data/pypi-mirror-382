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


#########################################################
# Initialize the simple agent
#########################################################
def create_simple_agent(sub_agents: list[PocketAgent]):
    # MCP config for the simple agent to give it access to the utilities server's tools
    # Note: since the simple agent will have a sub-agent, it is not required to pass a mcp config
    simple_agent_mcp_config = {
        "mcpServers": {
            "utilities": {
                "transport": "stdio",
                "command": "python",
                "args": ["server.py"],
                "cwd": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "servers", "simple_utilities")
            }
        }
    }

    # Agent config for the simple agent
    simple_agent_config = AgentConfig(
        llm_model="gpt-5-nano",
        system_prompt="You are a helpful assistant who answers user questions and uses provided tools when applicable"
    )

    # Create and return the simple agent instance
    simple_agent = PocketAgent(
        agent_config=simple_agent_config,
        mcp_config=simple_agent_mcp_config,
        sub_agents=sub_agents
    )
    return simple_agent


async def main():

    # Create the agents
    weather_agent = create_weather_agent()
    simple_agent = create_simple_agent([weather_agent])

    # Run the simple agent
    await simple_agent.run("Hello! What is the weather in Tokyo?")
    await simple_agent.run("Get the 3 day forecast for tokyo, sydney and london and make them into a table")


if __name__ == "__main__":
    asyncio.run(main())