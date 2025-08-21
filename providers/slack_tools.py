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


def get_channel_history(
    channel: str,
    limit: int = 50,
    oldest: str | None = None,
    latest: str | None = None,
    inclusive: bool = False,
    cursor: str | None = None
):
    """Get message history for a channel.

    Args:
        channel: Channel ID (e.g., 'C123...').
        limit: Max number of messages to return (default 50).
        oldest: Start time (ts) to include messages after.
        latest: End time (ts) to include messages before.
        inclusive: Include messages with oldest/latest timestamps.
        cursor: Pagination cursor from previous call.
    """
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        resp = slack_client.conversations_history(
            channel=channel,
            limit=limit,
            oldest=oldest,
            latest=latest,
            inclusive=inclusive,
            cursor=cursor
        )
        messages = resp.get('messages', [])
        metadata = resp.get('response_metadata', {}) or {}
        return {
            'ok': True,
            'messages': messages,
            'has_more': resp.get('has_more', False),
            'next_cursor': metadata.get('next_cursor')
        }
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def list_users(limit: int = 200, cursor: str | None = None):
    """List users in the workspace."""
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        resp = slack_client.users_list(limit=limit, cursor=cursor)
        members = []
        for m in resp.get('members', []):
            members.append({
                'id': m.get('id'),
                'name': m.get('name'),
                'real_name': m.get('real_name'),
                'is_bot': m.get('is_bot'),
                'deleted': m.get('deleted'),
            })
        metadata = resp.get('response_metadata', {}) or {}
        return {
            'ok': True,
            'members': members,
            'next_cursor': metadata.get('next_cursor')
        }
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def create_channel(name: str, is_private: bool = False):
    """Create a new channel."""
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        resp = slack_client.conversations_create(
            name=name,
            is_private=is_private
        )
        channel = resp.get('channel', {}) or {}
        return {
            'ok': True,
            'channel': {
                'id': channel.get('id'),
                'name': channel.get('name')
            }
        }
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def archive_channel(channel: str):
    """Archive a channel by ID."""
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        slack_client.conversations_archive(channel=channel)
        return {'ok': True}
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def join_channel(channel: str):
    """Join a channel by ID."""
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        resp = slack_client.conversations_join(channel=channel)
        ch = resp.get('channel', {}) or {}
        return {
            'ok': True,
            'channel': {
                'id': ch.get('id'),
                'name': ch.get('name')
            }
        }
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def add_reaction(channel: str, timestamp: str, name: str):
    """Add a reaction to a message.

    Args:
        channel: Channel ID containing the message.
        timestamp: Message ts to react to.
        name: Emoji name without colons, e.g., 'thumbsup'.
    """
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    try:
        slack_client.reactions_add(
            channel=channel,
            timestamp=timestamp,
            name=name
        )
        return {'ok': True}
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def upload_file(
    channels: str | list[str],
    filepath: str,
    title: str | None = None,
    initial_comment: str | None = None,
    thread_ts: str | None = None
):
    """Upload a file to one or more channels.

    For SDKs supporting files_upload_v2, a single channel is used. If a list of
    channels is provided, the first is used with v2. Otherwise falls back to
    files_upload which supports multiple channels (comma-separated).
    """
    if not slack_client:
        return {'ok': False, 'error': 'Slack not configured'}
    # Resolve and validate file path to avoid unsafe reads
    realpath = os.path.realpath(filepath)
    if not os.path.exists(realpath) or not os.path.isfile(realpath):
        return {'ok': False, 'error': 'File not found'}
    try:
        # Prefer files_upload_v2 if available
        if hasattr(slack_client, 'files_upload_v2'):
            channel_id = None
            if isinstance(channels, list):
                channel_id = channels[0] if channels else None
            else:
                channel_id = channels
            if not channel_id:
                return {'ok': False, 'error': 'Channel is required'}
            with open(realpath, 'rb') as f:
                resp = slack_client.files_upload_v2(
                    channel=channel_id,
                    file=f,
                    filename=os.path.basename(realpath),
                    title=title,
                    initial_comment=initial_comment,
                    thread_ts=thread_ts
                )
        else:
            if isinstance(channels, list):
                channel_str = ','.join(channels)
            else:
                channel_str = channels
            with open(realpath, 'rb') as f:
                resp = slack_client.files_upload(
                    channels=channel_str,
                    file=f,
                    filename=os.path.basename(realpath),
                    title=title,
                    initial_comment=initial_comment,
                    thread_ts=thread_ts
                )
        file_obj = resp.get('file')
        if not file_obj:
            files_list = resp.get('files') or []
            file_obj = files_list[0] if files_list else {}
        return {
            'ok': True,
            'file': {
                'id': file_obj.get('id'),
                'name': file_obj.get('name') or file_obj.get('title'),
                'title': file_obj.get('title')
            }
        }
    except SlackApiError as e:
        return {'ok': False, 'error': e.response.get('error')}


def register(mcp):
    """Bind this module's tools to a FastMCP server instance."""
    mcp.tool(post_slack_message)
    mcp.tool(list_slack_channels)
    mcp.tool(get_channel_history)
    mcp.tool(list_users)
    mcp.tool(create_channel)
    mcp.tool(archive_channel)
    mcp.tool(join_channel)
    mcp.tool(add_reaction)
    mcp.tool(upload_file)
