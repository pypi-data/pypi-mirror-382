# Configuration Guide

Detailed configuration options for `label-studio-sso`.

## Django Settings

All configuration is done through Django settings in `label_studio/core/settings/base.py`.

### Required Settings

#### JWT_SSO_SECRET

The JWT secret key used to verify token signatures.

```python
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')
```

**Type:** `str`
**Required:** Yes
**Default:** `None`

**Security Notes:**
- Must be **identical** to the secret used by your external system
- Should be at least 32 bytes long
- Store in environment variables, never in code
- Use cryptographically secure random values

**Generate Secure Secret:**
```bash
# Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"

# OpenSSL
openssl rand -base64 32
```

### Optional Settings

#### JWT_SSO_ALGORITHM

JWT signing algorithm.

```python
JWT_SSO_ALGORITHM = 'HS256'
```

**Type:** `str`
**Required:** No
**Default:** `'HS256'`

**Supported Algorithms:**
- `HS256` (HMAC-SHA256) - Recommended for shared secret
- `HS384` (HMAC-SHA384)
- `HS512` (HMAC-SHA512)
- `RS256` (RSA-SHA256) - For public/private key pairs
- `RS384` (RSA-SHA384)
- `RS512` (RSA-SHA512)

#### JWT_SSO_TOKEN_PARAM

URL parameter name for the JWT token.

```python
JWT_SSO_TOKEN_PARAM = 'token'
```

**Type:** `str`
**Required:** No
**Default:** `'token'`

**Example URLs:**
- Default: `http://label-studio.com/?token=eyJhbGc...`
- Custom: `http://label-studio.com/?sso_token=eyJhbGc...` (set to `'sso_token'`)

#### JWT_SSO_EMAIL_CLAIM

JWT claim containing the user's email address.

```python
JWT_SSO_EMAIL_CLAIM = 'email'
```

**Type:** `str`
**Required:** No
**Default:** `'email'`

**Examples:**
- Standard: `'email'` → JWT contains `{"email": "user@example.com"}`
- Custom: `'user_email'` → JWT contains `{"user_email": "user@example.com"}`

#### JWT_SSO_USERNAME_CLAIM

JWT claim containing the username.

```python
JWT_SSO_USERNAME_CLAIM = 'username'
```

**Type:** `str`
**Required:** No
**Default:** `None` (uses email as username)

**Behavior:**
- If `None`: Username defaults to email
- If set: Uses specified claim for username

#### JWT_SSO_FIRST_NAME_CLAIM

JWT claim containing the user's first name.

```python
JWT_SSO_FIRST_NAME_CLAIM = 'first_name'
```

**Type:** `str`
**Required:** No
**Default:** `'first_name'`

#### JWT_SSO_LAST_NAME_CLAIM

JWT claim containing the user's last name.

```python
JWT_SSO_LAST_NAME_CLAIM = 'last_name'
```

**Type:** `str`
**Required:** No
**Default:** `'last_name'`

#### JWT_SSO_AUTO_CREATE_USERS

Automatically create users on first login if they don't exist.

```python
JWT_SSO_AUTO_CREATE_USERS = False
```

**Type:** `bool`
**Required:** No
**Default:** `False`

**Behavior:**
- `True`: Create user automatically if not found
- `False`: Require manual user creation or external sync

**Security Consideration:** Set to `False` in production if you manage users separately.

## Complete Configuration Example

### Minimal Configuration

```python
# label_studio/core/settings/base.py
import os

INSTALLED_APPS = [
    # ... existing apps ...
    'label_studio_sso',
]

AUTHENTICATION_BACKENDS = [
    'label_studio_sso.backends.JWTAuthenticationBackend',
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    # ... existing middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',
    # ... rest of middleware ...
]

# Minimal JWT configuration
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')
```

### Full Configuration

```python
# label_studio/core/settings/base.py
import os

INSTALLED_APPS = [
    # ... existing apps ...
    'label_studio_sso',
]

AUTHENTICATION_BACKENDS = [
    'label_studio_sso.backends.JWTAuthenticationBackend',
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    # ... existing middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',
    # ... rest of middleware ...
]

# Complete JWT SSO configuration
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_TOKEN_PARAM = 'token'
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_USERNAME_CLAIM = None  # Use email as username
JWT_SSO_FIRST_NAME_CLAIM = 'first_name'
JWT_SSO_LAST_NAME_CLAIM = 'last_name'
JWT_SSO_AUTO_CREATE_USERS = False

# Additional Django settings for production
DEBUG = False
ALLOWED_HOSTS = ['label-studio.example.com']
CORS_ALLOWED_ORIGINS = [
    'https://things-factory.example.com',
]
X_FRAME_OPTIONS = 'SAMEORIGIN'
```

## Environment Variables

Store sensitive configuration in environment variables.

### .env File

```bash
# JWT SSO Configuration
JWT_SSO_SECRET=x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p

# Optional overrides
JWT_SSO_ALGORITHM=HS256
JWT_SSO_TOKEN_PARAM=token
JWT_SSO_AUTO_CREATE_USERS=false
```

### systemd Service File

```ini
# /etc/systemd/system/label-studio.service
[Service]
Environment="JWT_SSO_SECRET=x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p"
Environment="JWT_SSO_ALGORITHM=HS256"
Environment="JWT_SSO_AUTO_CREATE_USERS=false"
```

### Docker Environment

```yaml
# docker-compose.yml
services:
  label-studio:
    image: heartexlabs/label-studio:latest
    environment:
      - JWT_SSO_SECRET=x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p
      - JWT_SSO_ALGORITHM=HS256
      - JWT_SSO_AUTO_CREATE_USERS=false
```

## JWT Token Structure

Your external system must generate JWT tokens with the following structure:

### Required Claims

```json
{
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234567900
}
```

### Optional Claims

```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "iat": 1234567890,
  "exp": 1234567900
}
```

### Custom Claims Mapping

Map custom JWT claims to Django user fields:

```python
# Settings
JWT_SSO_EMAIL_CLAIM = 'user_email'
JWT_SSO_FIRST_NAME_CLAIM = 'given_name'
JWT_SSO_LAST_NAME_CLAIM = 'family_name'
```

```json
{
  "user_email": "user@example.com",
  "given_name": "John",
  "family_name": "Doe",
  "iat": 1234567890,
  "exp": 1234567900
}
```

## Security Best Practices

### 1. Secret Management

✅ **Do:**
- Store secrets in environment variables
- Use secrets management tools (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets periodically
- Use different secrets for dev/staging/production

❌ **Don't:**
- Hardcode secrets in settings.py
- Commit secrets to version control
- Share secrets between environments
- Use weak or predictable secrets

### 2. Token Expiration

```python
# External system token generation
exp = int(time.time()) + 600  # 10 minutes
```

**Recommended Expiration Times:**
- **Development:** 1 hour
- **Staging:** 30 minutes
- **Production:** 5-10 minutes

### 3. HTTPS Only

```python
# Django settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 4. CORS Configuration

```python
# Allow specific origins only
CORS_ALLOWED_ORIGINS = [
    'https://things-factory.example.com',
    'https://app.example.com',
]

# Never use in production:
# CORS_ALLOW_ALL_ORIGINS = True
```

### 5. Logging

```python
# Django logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/label-studio/sso.log',
        },
    },
    'loggers': {
        'label_studio_sso': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Configuration Validation

Validate your configuration:

```python
# Django shell
python manage.py shell

>>> from django.conf import settings
>>>
>>> # Check JWT_SSO_SECRET
>>> assert settings.JWT_SSO_SECRET is not None, "JWT_SSO_SECRET not set"
>>> assert len(settings.JWT_SSO_SECRET) >= 32, "JWT_SSO_SECRET too short"
>>>
>>> # Check installed apps
>>> assert 'label_studio_sso' in settings.INSTALLED_APPS
>>>
>>> # Check authentication backends
>>> assert 'label_studio_sso.backends.JWTAuthenticationBackend' in settings.AUTHENTICATION_BACKENDS
>>>
>>> # Check middleware
>>> assert 'label_studio_sso.middleware.JWTAutoLoginMiddleware' in settings.MIDDLEWARE
>>>
>>> print("✅ Configuration valid")
```

## Troubleshooting Configuration

### Check Current Settings

```python
# Django shell
python manage.py shell

>>> from django.conf import settings
>>>
>>> # View JWT settings
>>> print(f"SECRET: {settings.JWT_SSO_SECRET[:10]}...")
>>> print(f"ALGORITHM: {settings.JWT_SSO_ALGORITHM}")
>>> print(f"TOKEN_PARAM: {settings.JWT_SSO_TOKEN_PARAM}")
>>> print(f"EMAIL_CLAIM: {settings.JWT_SSO_EMAIL_CLAIM}")
>>> print(f"AUTO_CREATE: {settings.JWT_SSO_AUTO_CREATE_USERS}")
```

### Test Configuration

See [Troubleshooting Guide](troubleshooting.md) for detailed testing procedures.

## Next Steps

- **[API Reference](api-reference.md)** - Detailed API documentation
- **[Examples](examples/)** - Configuration examples
- **[Troubleshooting](troubleshooting.md)** - Common issues
