from app.agents.base import AgentConnector
from app.agents.openai import OpenAIConnector
from app.agents.anthropic import AnthropicConnector
from app.agents.webhook import WebhookConnector
from app.agents.demo import DemoConnector, DEMO_TOOLS


def get_connector(provider: str, config: dict) -> AgentConnector:
    if provider == "openai":
        return OpenAIConnector(config)
    if provider == "anthropic":
        return AnthropicConnector(config)
    if provider == "webhook":
        return WebhookConnector(config)
    if provider == "demo":
        return DemoConnector(config)
    raise ValueError(f"Unknown provider: {provider}")
