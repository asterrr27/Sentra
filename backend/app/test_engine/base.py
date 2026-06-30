from abc import ABC, abstractmethod
from typing import Any


class Scenario(ABC):
    name: str = ""
    description: str = ""
    owasp_category: str = ""
    payloads: list[Any] = []

    @abstractmethod
    def build_conversation(self, payload: Any) -> list[dict]:
        pass

    @abstractmethod
    def evaluate(self, agent_responses: list[dict], tool_results: list[dict]) -> bool:
        pass
