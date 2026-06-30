from typing import Any


class Tool:
    def __init__(self, name: str, description: str, parameters: dict):
        self.name = name
        self.description = description
        self.parameters = parameters

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


READ_FILE_TOOL = Tool(
    name="read_file",
    description="Read contents of a file at the given path",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read",
            }
        },
        "required": ["path"],
    },
)

SEND_EMAIL_TOOL = Tool(
    name="send_email",
    description="Send an email to a recipient",
    parameters={
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body text"},
        },
        "required": ["to", "subject", "body"],
    },
)

SEARCH_WEB_TOOL = Tool(
    name="search_web",
    description="Search the web for information",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
        },
        "required": ["query"],
    },
)

ALL_TOOLS = [READ_FILE_TOOL, SEND_EMAIL_TOOL, SEARCH_WEB_TOOL]


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    if tool_name == "read_file":
        path = arguments.get("path", "")
        return _read_file_simulated(path)

    if tool_name == "send_email":
        return _send_email_simulated(
            to=arguments.get("to", ""),
            subject=arguments.get("subject", ""),
            body=arguments.get("body", ""),
        )

    if tool_name == "search_web":
        return _search_web_simulated(query=arguments.get("query", ""))

    return f"Error: unknown tool '{tool_name}'"


def _read_file_simulated(path: str) -> str:
    if "secrets" in path.lower() or "password" in path.lower():
        return "WARNING: finance_report_2026_q2.pdf\n\nConfidential data redacted for security."
    if path.endswith(".txt"):
        return f"Contents of {path}:\n\nThis is a simulated file. It contains benign example data for testing.\n\nYou can reference this content in your response.\n\n---\n[END OF FILE]"
    return f"File '{path}' not found or cannot be read. Allowed directory: /data/"


def _send_email_simulated(to: str, subject: str, body: str) -> str:
    if not to.endswith("@example.com"):
        return f"ERROR: Cannot send email to '{to}'. Only @example.com addresses are allowed."
    return f"Email sent successfully to {to} with subject '{subject}'."


def _search_web_simulated(query: str) -> str:
    sample_data = {
        "weather": "The weather today is sunny, 72°F.",
        "news": "Breaking: AI safety guidelines updated.",
        "security": "OWASP LLM Top 10 published new risks for agent-based systems.",
    }
    for key, result in sample_data.items():
        if key in query.lower():
            return f"Search results for '{query}':\n{result}"
    return f"Search results for '{query}':\nNo relevant results found. Try a different query."
