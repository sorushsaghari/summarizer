# GitLab Duo License Integration

This document explains how GitLab Duo license validation works in the Telegram Summarizer Bot.

## Overview

GitLab Duo is GitLab's suite of AI-powered features that includes:
- Code completion and suggestions
- Chat assistance
- Code generation
- Security scanning with AI
- Vulnerability detection

This integration ensures that the bot's AI-powered summarization features comply with GitLab Duo licensing requirements.

## Features

### License Validation
- Validates GitLab Duo license status before AI operations
- Supports both GitLab.com and self-hosted GitLab instances
- Checks feature availability and user limits
- Handles license expiration and plan limitations

### Bot Integration
- Automatically checks license before using OpenAI for summarization
- Provides clear feedback when license validation fails
- Continues with basic operations when AI features are restricted
- Logs license status for monitoring and debugging

## Configuration

### Environment Variables

Set these environment variables to enable GitLab Duo license validation:

```bash
# Required: GitLab personal access token with API access
export GITLAB_PRIVATE_TOKEN="your_gitlab_personal_access_token"

# Optional: GitLab instance URL (defaults to https://gitlab.com)
export GITLAB_URL="https://gitlab.com"

# Optional: Project ID for project-level feature checking
export GITLAB_PROJECT_ID="your_project_id"
```

### Settings File

Alternatively, configure in `settings.yaml`:

```yaml
default:
  # ... existing settings ...
  
  # GitLab Duo License Configuration
  gitlab_url: 'https://gitlab.com'
  gitlab_private_token: 'your_gitlab_personal_access_token'
  gitlab_project_id: 'your_project_id'  # optional
```

## How It Works

### 1. Initialization
When the bot starts, it initializes the GitLab Duo license validator if credentials are provided:

```python
# Bot checks for GitLab credentials
if hasattr(settings, 'gitlab_private_token') and settings.gitlab_private_token:
    self.gitlab_license_validator = GitLabDuoLicenseValidator(...)
```

### 2. License Validation
Before each AI operation, the bot validates the license:

```python
license_info = self.gitlab_license_validator.check_license()
if not license_info.is_valid:
    # Block AI operation and notify user
    return
```

### 3. Response Handling
Based on license status, the bot:
- **Valid License**: Proceeds with AI summarization using OpenAI
- **Invalid License**: Sends license notice instead of AI summary
- **No License Config**: Operates normally without validation

## License Scenarios

### Valid Ultimate License
```
✓ License Valid: True
✓ License Type: ultimate
✓ Features: ['code_completion', 'chat_assistance', 'code_generation']
→ AI summarization: ALLOWED
```

### Valid Premium License (Limited)
```
✓ License Valid: True
✓ License Type: premium  
✓ Features: ['code_completion']
→ AI summarization: ALLOWED (with limited features)
```

### Free Plan
```
✗ License Valid: False
✗ License Type: free
✗ Features: []
→ AI summarization: BLOCKED
→ Sends: "⚠️ License Notice: GitLab Duo not available on free plan"
```

### Expired License
```
✗ License Valid: False
✗ License Type: premium
✗ Expired: 2023-12-31
→ AI summarization: BLOCKED
→ Sends: "⚠️ License Notice: License has expired"
```

## Testing

Run the test script to verify the integration:

```bash
python test_gitlab_duo_license.py
```

This will demonstrate:
- License validation scenarios
- Bot behavior with different license states
- Environment configuration testing

## API Reference

### GitLabDuoLicenseValidator

Main class for license validation:

```python
validator = GitLabDuoLicenseValidator(
    gitlab_url="https://gitlab.com",
    private_token="token",
    project_id="project_id"
)

license_info = validator.check_license()
```

### GitLabDuoLicense

Data class representing license information:

```python
@dataclass
class GitLabDuoLicense:
    is_valid: bool
    license_type: str
    expires_at: Optional[datetime]
    features_enabled: list
    user_limit: Optional[int]
    current_users: Optional[int]
    message: str
```

## Security Considerations

1. **Token Security**: Store GitLab tokens securely and never commit them to version control
2. **API Access**: Use tokens with minimal required permissions
3. **Error Handling**: License validation failures are logged but don't crash the bot
4. **Fallback Behavior**: Configure appropriate fallback when license validation fails

## Troubleshooting

### Common Issues

1. **"GitLab private token is required"**
   - Set `GITLAB_PRIVATE_TOKEN` environment variable
   - Or configure `gitlab_private_token` in settings.yaml

2. **"Failed to validate GitLab Duo license"**
   - Check network connectivity to GitLab instance
   - Verify token has API access permissions
   - Check GitLab instance URL is correct

3. **"No admin access to check instance license"**
   - This is normal for non-admin users
   - System falls back to project-level feature checking
   - Consider using project-level validation instead

### Debug Logging

Enable debug logging to see detailed license validation:

```python
import logging
logging.getLogger('gitlab_duo_license').setLevel(logging.DEBUG)
```

## License Compliance

This integration helps ensure:
- AI features are only used when properly licensed
- Usage stays within license limits
- Users are notified of license status changes
- Audit trail of license validation attempts

For more information about GitLab Duo licensing, visit the [GitLab documentation](https://docs.gitlab.com/).