from typing import Any


class AgentConnector:
    def __init__(self, config: dict):
        self.config = config

    def chat(self, messages: list[dict]) -> dict:
        raise NotImplementedError

    @property
    def tools(self) -> list[dict]:
        from app.agents.demo import DEMO_TOOLS
        return DEMO_TOOLS
