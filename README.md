# MCP Server for Jira, Gmail, and Slack (Python)

Lightweight MCP server exposing tools for Jira, Gmail, and Slack. Authentication is currently disabled in code (ready to add later). Tools are modularized under `providers/`.

## Setup

1. Clone the repo.
2. Create a `.env` with required variables (example):
```
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=you@example.com
JIRA_API_TOKEN=your_api_token
SLACK_BOT_TOKEN=xoxb-...
GMAIL_CREDENTIALS_JSON=/app/credentials.json
```
3. Place your Gmail OAuth client file at the path given by `GMAIL_CREDENTIALS_JSON` and do not commit it.

## Run locally (Python)

```bash
pip install -r requirements.txt  # if present, otherwise:
pip install mcp fastapi slack_sdk jira google-api-python-client google-auth-oauthlib python-dotenv requests uvicorn

python server.py
```

## Build & Run with Docker

```bash
docker build -t mcp-server .
docker run --env-file .env -v $(pwd)/credentials.json:/app/credentials.json:ro -p 8000:8000 mcp-server
```

## Notes
- Gmail tools perform an interactive OAuth on first run and store `token.json` in the working dir.
- Jira tools use `jira` library with API token auth.
- Slack tools use `slack_sdk` with a bot token.

## Deploying to Render.com

1. Push to GitHub
   - Ensure your repo includes `server.py`, `Dockerfile`, and the `providers/` directory. Do not commit secrets.

2. Sign in to Render
   - Go to `https://render.com` and log in or create an account.

3. Create a New Web Service
   - Click New → Web Service.
   - Select Docker so Render builds using your `Dockerfile`.

4. Connect Your Git Repository
   - Connect GitHub and select your repository.
   - Configuration:
     - Branch: e.g. `main`
     - Root Directory: leave blank if `Dockerfile` is at repo root
     - Instance Type: Free (for testing) or higher as needed

5. Environment Variables and Secret Files
   - In the service’s Environment tab, add the same variables you used locally, for example:
     - `JIRA_BASE_URL=https://your-domain.atlassian.net`
     - `JIRA_EMAIL=you@example.com`
     - `JIRA_API_TOKEN=...`
     - `SLACK_BOT_TOKEN=xoxb-...`
     - `GMAIL_CREDENTIALS_JSON=/etc/secrets/credentials.json`
   - If you need `credentials.json` (Gmail OAuth client), upload it under Secret Files named `credentials.json`. Render mounts it at `/etc/secrets/credentials.json` by default, matching the env var above.

6. Deploy
   - Click Create/Deploy. Render will build the container with the `Dockerfile` and start it.
   - After the deploy finishes, your service will be available at `https://<your-service>.onrender.com`.

7. (Optional) Auto-Deploy
   - Auto-deploy on each commit can be enabled/disabled in the service settings.


## Security
- Do not commit `.env`, `credentials.json`, or `token.json`.
- Use scoped tokens and rotate secrets.