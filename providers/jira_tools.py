"""Jira MCP tools."""

import os
import json
from mcp.types import TextContent
from jira import JIRA


JIRA_EMAIL = os.getenv('JIRA_EMAIL')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_BASE_URL = os.getenv('JIRA_BASE_URL')


def _get_jira_client():
    if not JIRA_BASE_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        raise RuntimeError(
            "Jira configuration missing. Set "
            "JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN"
        )
    return JIRA(
        server=JIRA_BASE_URL,
        basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN)
    )


def get_issue(issue_key: str):
    """Retrieve a full Jira issue with comments and attachments."""
    try:
        jira_client = _get_jira_client()
        issue = jira_client.issue(issue_key, expand='comment,attachment')
        comments = []
        for c in issue.fields.comment.comments:
            comments.append({
                "id": c.id,
                "author": getattr(c.author, "displayName", str(c.author)),
                "body": c.body,
                "created": str(c.created),
            })
        attachments = []
        for a in issue.fields.attachment:
            attachments.append({
                "id": a.id,
                "filename": a.filename,
                "size": a.size,
                "created": str(a.created),
                "mimeType": getattr(a, "mimeType", None),
                "content": getattr(a, "content", None)
            })
        data = {
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description,
            "status": getattr(issue.fields.status, "name", None),
            "priority": getattr(issue.fields.priority, "name", None),
            "assignee": getattr(
                issue.fields.assignee,
                "displayName",
                None
            ),
            "type": getattr(issue.fields.issuetype, "name", None),
            "comments": comments,
            "attachments": attachments
        }
        return [
            TextContent(
                type="text",
                text=json.dumps(data, ensure_ascii=False)
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error retrieving issue {issue_key}: {e}",
                isError=True
            )
        ]


def search_issues(jql: str, max_results: int = 30):
    """Search Jira issues using JQL."""
    if not jql:
        return [TextContent(type="text", text="jql is required", isError=True)]
    try:
        jira_client = _get_jira_client()
        fields = "summary,description,status,priority,assignee,issuetype"
        issues = jira_client.search_issues(
            jql,
            maxResults=max_results,
            fields=fields
        )
        results = []
        for issue in issues:
            results.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": getattr(issue.fields.status, "name", None),
                "priority": getattr(issue.fields.priority, "name", None),
                "assignee": getattr(
                    issue.fields.assignee,
                    "displayName",
                    None
                ),
                "type": getattr(issue.fields.issuetype, "name", None)
            })
        return [
            TextContent(
                type="text",
                text=json.dumps(results, ensure_ascii=False)
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error searching issues: {e}",
                isError=True
            )
        ]


def add_jira_comment(issue_key: str, body: str):
    """Add a comment to a Jira issue."""
    try:
        jira_client = _get_jira_client()
        comment = jira_client.add_comment(issue_key, body)
        return {
            'ok': True,
            'id': getattr(comment, 'id', None),
            'created': getattr(comment, 'created', None)
        }
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def register(mcp):
    """Bind this module's tools to a FastMCP server instance."""
    mcp.tool(get_issue)
    mcp.tool(search_issues)
    mcp.tool(add_jira_comment)
