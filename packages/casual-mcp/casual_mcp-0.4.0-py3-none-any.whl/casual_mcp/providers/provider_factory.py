import os
from typing import TypeAlias

import mcp
from fastmcp import Client

from casual_mcp.logging import get_logger
from casual_mcp.models.model_config import ModelConfig
from casual_mcp.providers.ollama_provider import OllamaProvider
from casual_mcp.providers.openai_provider import OpenAiProvider

logger = get_logger("providers.factory")

LLMProvider: TypeAlias = OpenAiProvider | OllamaProvider

class ProviderFactory:
    providers: dict[str, LLMProvider] = {}
    tools: list[mcp.Tool] = None

    def __init__(self, mcp_client: Client):
        self.mcp_client = mcp_client


    def set_tools(self, tools: list[mcp.Tool]):
        self.tools = tools


    async def get_provider(self, name: str, config: ModelConfig) -> LLMProvider:
        if not self.tools:
            async with self.mcp_client:
                self.tools = await self.mcp_client.list_tools()

        if self.providers.get(name):
            return self.providers.get(name)

        match config.provider:
            case "ollama":
                logger.info(f"Creating Ollama provider for {config.model} at {config.endpoint}")
                provider = OllamaProvider(config.model, endpoint=config.endpoint.__str__())

            case "openai":
                endpoint = None
                if config.endpoint:
                    endpoint = config.endpoint.__str__()

                logger.info(f"Creating OpenAI provider for {config.model} at {endpoint}")
                api_key = os.getenv("OPEN_AI_API_KEY")
                provider = OpenAiProvider(
                    config.model,
                    api_key,
                    self.tools,
                    endpoint=endpoint,
                )

        self.providers[name] = provider
        return provider
