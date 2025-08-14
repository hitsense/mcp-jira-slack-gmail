"""
Lightweight MCP server exposing tools for Jira, Gmail, and Slack.
Authentication is currently disabled for simplicity.
"""

from dotenv import load_dotenv
from fastmcp import FastMCP


load_dotenv()


mcp = FastMCP("jira-gmail-slack-mcp")


from providers import jira_tools as _jira_tools  # noqa: E402
from providers import slack_tools as _slack_tools  # noqa: E402
from providers import gmail_tools as _gmail_tools  # noqa: E402


# Register all provider tools with this server instance
_jira_tools.register(mcp)
_slack_tools.register(mcp)
_gmail_tools.register(mcp)


if __name__ == "__main__":
    # Expose over SSE (HTTP) so clients can connect to http://host:8000/sse
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
