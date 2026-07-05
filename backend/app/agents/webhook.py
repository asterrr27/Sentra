import logging
from urllib.parse import urlparse

import httpx

from app.agents.base import AgentConnector
from app.config import settings

logger = logging.getLogger(__name__)

BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "[::1]", "::1"}
BLOCKED_PREFIXES = ("169.254.", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "192.168.")


def _is_blocked(url: str) -> bool:
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if host in BLOCKED_HOSTS:
            return True
        for prefix in BLOCKED_PREFIXES:
            if host.startswith(prefix):
                return True
        if parsed.scheme not in ("http", "https"):
            return True
        return False
    except Exception:
        return True


class WebhookConnector(AgentConnector):
    def __init__(self, config: dict):
        super().__init__(config)
        self.url = config.get("url", "")

    def chat(self, messages: list[dict]) -> dict:
        if not self.url:
            return {"role": "assistant", "content": "[Error: No webhook URL provided]"}

        if _is_blocked(self.url):
            logger.warning(f"Blocked webhook URL targeting internal network: {self.url}")
            return {"role": "assistant", "content": "[Error: Webhook URL targeting internal networks is not allowed]"}

        try:
            headers = {"Content-Type": "application/json"}

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
            logger.error(f"Webhook error for {self.url}: {e}", exc_info=True)
            return {"role": "assistant", "content": "[Webhook Error: The request failed. Check server logs for details.]"}
