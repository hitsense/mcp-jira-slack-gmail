"""Slack MCP tools."""

import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', '')
slack_client = WebClient(token=SLACK_BOT_TOKEN) if SLACK_BOT_TOKEN else None


def post_slack_message(channel: str, text: str, thread_ts: str | None = None):
    """Post a message to Slack using bot token from env."""
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        resp = slack_client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
        return {
            'ok': resp.get('ok', False),
            'ts': resp.get('ts'),
            'channel': resp.get('channel')
        }
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def list_slack_channels(types: str = 'public_channel'):
    """List Slack conversations by types (comma-separated)."""
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        resp = slack_client.conversations_list(types=types)
        channels = []
        for ch in resp.get('channels', []):
            channels.append({
                'id': ch.get('id'),
                'name': ch.get('name'),
                'is_private': ch.get('is_private'),
                'is_archived': ch.get('is_archived')
            })
        return {'ok': True, 'channels': channels}
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def register(mcp):
    """Bind this module's tools to a FastMCP server instance."""
    mcp.tool(post_slack_message)
    mcp.tool(list_slack_channels)
