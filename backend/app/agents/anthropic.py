import json
import logging

import httpx

from app.agents.base import AgentConnector

logger = logging.getLogger(__name__)


class AnthropicConnector(AgentConnector):
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "claude-sonnet-4-20250514")
        self.system_prompt = config.get("system_prompt", None)

    def chat(self, messages: list[dict]) -> dict:
        if not self.api_key:
            raise ValueError("[Error: No API key provided]")

        try:
            with httpx.Client(timeout=30) as client:
                body = {
                    "model": self.model,
                    "max_tokens": 1024,
                    "messages": messages,
                }
                if self.system_prompt:
                    body["system"] = self.system_prompt

                resp = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json",
                    },
                    json=body,
                )
                resp.raise_for_status()
                data = resp.json()

                content = ""
                tool_calls = []
                for block in data.get("content", []):
                    if block["type"] == "text":
                        content += block["text"]
                    elif block["type"] == "tool_use":
                        tool_calls.append({
                            "id": block["id"],
                            "type": "function",
                            "function": {
                                "name": block["name"],
                                "arguments": json.dumps(block["input"]),
                            },
                        })

                result = {"role": "assistant", "content": content or None}
                if tool_calls:
                    result["tool_calls"] = tool_calls
                return result
        except Exception as e:
            logger.error(f"Anthropic API error: {e}", exc_info=True)
            return {"role": "assistant", "content": "[API Error: The request failed. Check server logs for details.]"}
