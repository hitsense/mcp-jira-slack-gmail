# Stage 1: Build dependencies (if needed in the future)
# Currently not used, but left as placeholder for tasks like static code analysis or type checking
FROM python:3.11-slim

# Security: run as non-root user
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

WORKDIR /app

# Copy source
COPY server.py ./
COPY providers ./providers

# Install runtime dependencies (pin in real deployments)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
      mcp \
      fastapi \
      slack_sdk \
      jira \
      google-api-python-client \
      google-auth-oauthlib \
      python-dotenv \
      requests

EXPOSE 8000

USER appuser

# Placeholder health check (optional)
# HEALTHCHECK --timeout=3s CMD curl -f http://localhost:8000/ || exit 1

# server.py calls serve_http(mcp)
CMD ["python", "server.py"]