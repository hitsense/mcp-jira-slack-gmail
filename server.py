# server.py
"""
Lightweight MCP server exposing tools for Jira, Gmail, and Slack.
Authentication is currently disabled for simplicity.
"""

from fastapi import FastAPI
from mcp import MCPServer
from mcp.transport.http import serve_http
from dotenv import load_dotenv


load_dotenv()


app = FastAPI()
mcp = MCPServer(name="jira-gmail-slack-mcp")


from providers import jira_tools as _jira_tools  # noqa: E402,F401
from providers import slack_tools as _slack_tools  # noqa: E402,F401
from providers import gmail_tools as _gmail_tools  # noqa: E402,F401


if __name__ == "__main__":
    serve_http(mcp)


if __name__ == "__main__":
    serve_http(mcp)
