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
