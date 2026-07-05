import logging

import httpx

from app.agents.base import AgentConnector

logger = logging.getLogger(__name__)


class OpenAIConnector(AgentConnector):
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-4o-mini")
        self.system_prompt = config.get("system_prompt", None)

    def chat(self, messages: list[dict]) -> dict:
        if not self.api_key:
            raise ValueError("[Error: No API key provided]")

        full_messages = []
        if self.system_prompt:
            full_messages.append({"role": "system", "content": self.system_prompt})
        full_messages.extend(messages)

        try:
            with httpx.Client(timeout=30) as client:
                body = {
                    "model": self.model,
                    "messages": full_messages,
                }
                if self.tools:
                    body["tools"] = self.tools
                    body["tool_choice"] = "auto"

                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                resp.raise_for_status()
                return resp.json()["choices"][0]["message"]
        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return {"role": "assistant", "content": "[API Error: The request failed. Check server logs for details.]"}
