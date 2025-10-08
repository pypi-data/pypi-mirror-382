import asyncio
from pocket_agent import PocketAgent, AgentConfig



async def main():
    import os

    mcp_config = {
        "mcpServers": {
            "RAG_server": {
                "transport": "stdio",
                "command": "python",
                "args": ["server.py"],
                "cwd": os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "servers", "llama_index_rag_server"),
                "env": {
                    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
                }
            }
        }
    }
    # Configure agent  
    config = AgentConfig(
        llm_model="gpt-5-nano",
        system_prompt="You are a helpful assistant who answers user questions about the Nike 2023 Annual Report.\
            You have access to a query tool to retrieve relevant context from the Nike 2023 Annual Report.\
            The query tool accepts a `query` argument which is the string you want to find semantically similar results for from the Nike 2023 Annual Report."
    )
    # Create and run agent
    agent = PocketAgent(
        agent_config=config,
        mcp_config=mcp_config
    )
    
    await agent.run("How many shoe factories were operated as of May 31, 2023?")

if __name__ == "__main__":
    asyncio.run(main())