# Guardrail: No Secrets

## Purpose
Prevent accidental exposure of secrets, credentials, and sensitive data.

## Rules

### Never Commit
- API keys or tokens
- Passwords or passphrases
- Private keys (SSH, SSL, etc.)
- Database connection strings with credentials
- OAuth client secrets
- Webhook secrets
- Encryption keys

### Files to Never Create or Modify Directly
- `.env` files (use `.env.example` as template)
- `credentials.json`
- `secrets.yaml`
- `*.pem`, `*.key`, `*.p12` files
- AWS credentials files
- GCP service account keys

### Patterns to Avoid in Code
```
# Never hardcode these patterns:
password = "..."
api_key = "..."
secret = "..."
token = "..."
AWS_SECRET_ACCESS_KEY = "..."
PRIVATE_KEY = "..."
```

### Safe Alternatives
```python
# Use environment variables
import os
api_key = os.environ.get('API_KEY')

# Use secrets manager
from aws_secretsmanager import get_secret
api_key = get_secret('my-api-key')
```

### Git Configuration
Ensure `.gitignore` includes:
```
.env
.env.*
!.env.example
*.pem
*.key
secrets/
credentials.json
```

## Actions

1. If asked to add credentials to code, suggest environment variables instead
2. If a file appears to contain secrets, warn before any operation
3. Never log or display secret values, even in debug output
4. Suggest using secret scanning tools (git-secrets, trufflehog)
