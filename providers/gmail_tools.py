"""Gmail MCP tools."""

import os
import pathlib
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
GMAIL_CREDENTIALS_JSON = os.getenv('GMAIL_CREDENTIALS_JSON')
GMAIL_TOKEN_JSON = os.getenv('GMAIL_TOKEN_JSON', 'token.json')


def _build_gmail_service():
    creds = None
    token_path = pathlib.Path(GMAIL_TOKEN_JSON)
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    elif GMAIL_CREDENTIALS_JSON:
        flow = InstalledAppFlow.from_client_secrets_file(
            GMAIL_CREDENTIALS_JSON, SCOPES
            )
        creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    else:
        raise RuntimeError('GMail credentials missing')
    return build('gmail', 'v1', credentials=creds)


def _gmail_get_header(headers, name):
    target = (name or '').lower()
    for h in headers or []:
        if (h.get('name', '').lower()) == target:
            return h.get('value')
    return None


def _gmail_extract_text(payload, prefer='plain'):
    if not payload:
        return None
    mime = payload.get('mimeType', '')
    body = payload.get('body', {})
    data = body.get('data')

    def _decode(b64):
        import base64
        try:
            raw = base64.urlsafe_b64decode(b64.encode())
            return raw.decode('utf-8', 'ignore')
        except Exception:
            return None

    if mime == 'text/plain' and data:
        return _decode(data)
    if mime == 'text/html' and data and prefer == 'html':
        return _decode(data)
    for part in payload.get('parts', []) or []:
        text = _gmail_extract_text(part, prefer=prefer)
        if text:
            return text
    return None


def list_emails(q: str = ''):
    try:
        service = _build_gmail_service()
    except RuntimeError as e:
        return {'error': str(e)}
    resp = service.users().messages().list(
        userId='me', q=q, maxResults=5
    ).execute()
    return {'messages': resp.get('messages', [])}


def get_email(id: str):
    service = _build_gmail_service()
    msg = service.users().messages().get(
        userId='me', id=id, format='full'
    ).execute()
    return msg


def list_gmail_labels():
    try:
        service = _build_gmail_service()
        resp = service.users().labels().list(userId='me').execute()
        labels = resp.get('labels', [])
        items = []
        for label in labels:
            items.append({'id': label.get('id'), 'name': label.get('name')})
        return {'labels': items}
    except Exception as e:
        return {'error': str(e)}


def search_gmail(q: str = '', max_results: int = 10):
    try:
        service = _build_gmail_service()
        resp = service.users().messages().list(
            userId='me', q=q, maxResults=max_results
        ).execute()
        summaries = []
        for m in resp.get('messages', []):
            full = service.users().messages().get(
                userId='me', id=m['id'], format='metadata',
                metadataHeaders=['Subject', 'From', 'Date']
            ).execute()
            payload = full.get('payload', {})
            headers = payload.get('headers', [])
            summaries.append({
                'id': full.get('id'),
                'threadId': full.get('threadId'),
                'subject': _gmail_get_header(headers, 'Subject'),
                'from': _gmail_get_header(headers, 'From'),
                'date': _gmail_get_header(headers, 'Date'),
                'snippet': full.get('snippet')
            })
        return {'messages': summaries}
    except Exception as e:
        return {'error': str(e)}


def get_gmail_thread(thread_id: str, prefer_body: str = 'plain'):
    try:
        service = _build_gmail_service()
        thread = service.users().threads().get(
            userId='me', id=thread_id, format='full'
        ).execute()
        messages = []
        for msg in thread.get('messages', []):
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            messages.append({
                'id': msg.get('id'),
                'subject': _gmail_get_header(headers, 'Subject'),
                'from': _gmail_get_header(headers, 'From'),
                'to': _gmail_get_header(headers, 'To'),
                'date': _gmail_get_header(headers, 'Date'),
                'snippet': msg.get('snippet'),
                'body': _gmail_extract_text(payload, prefer=prefer_body)
            })
        return {'id': thread.get('id'), 'messages': messages}
    except Exception as e:
        return {'error': str(e)}


def register(mcp):
    """Bind this module's tools to a FastMCP server instance."""
    mcp.tool(list_emails)
    mcp.tool(get_email)
    mcp.tool(list_gmail_labels)
    mcp.tool(search_gmail)
    mcp.tool(get_gmail_thread)
