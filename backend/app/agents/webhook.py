import httpx

from app.agents.base import AgentConnector
from app.config import settings


class WebhookConnector(AgentConnector):
    def __init__(self, config: dict):
        super().__init__(config)
        self.url = config.get("url", "")
        self.auth_header = config.get("auth_header", "")

    def chat(self, messages: list[dict]) -> dict:
        if not self.url:
            return {"role": "assistant", "content": "[Error: No webhook URL provided]"}

        try:
            headers = {"Content-Type": "application/json"}
            if self.auth_header:
                headers["Authorization"] = self.auth_header

            with httpx.Client(timeout=settings.CUSTOM_AGENT_TIMEOUT) as client:
                resp = client.post(
                    self.url,
                    headers=headers,
                    json={"messages": messages},
                )
                resp.raise_for_status()
                data = resp.json()

                if isinstance(data, dict):
                    return {
                        "role": "assistant",
                        "content": data.get("content", str(data)),
                        "tool_calls": data.get("tool_calls", []),
                    }
                return {"role": "assistant", "content": str(data), "tool_calls": []}
        except Exception as e:
            return {"role": "assistant", "content": f"[Webhook Error: {e}]"}
