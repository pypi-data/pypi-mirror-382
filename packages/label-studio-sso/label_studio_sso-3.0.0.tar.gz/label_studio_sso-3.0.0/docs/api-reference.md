# API Reference

Complete API documentation for `label-studio-sso`.

## Authentication Backend

### JWTAuthenticationBackend

Django authentication backend for JWT-based SSO.

```python
from label_studio_sso.backends import JWTAuthenticationBackend
```

#### Class Definition

```python
class JWTAuthenticationBackend(ModelBackend):
    """
    Generic JWT Authentication Backend for external SSO integration.
    """
```

#### Methods

##### authenticate(request, token=None, **kwargs)

Authenticate user using external JWT token.

**Parameters:**
- `request` (HttpRequest): Django HTTP request object
- `token` (str, optional): JWT token string. If not provided, extracted from URL parameter
- `**kwargs`: Additional keyword arguments (unused)

**Returns:**
- `User` object if authentication succeeds
- `None` if authentication fails

**Raises:**
- No exceptions (returns `None` on error)

**Example:**
```python
from django.test import RequestFactory
from label_studio_sso.backends import JWTAuthenticationBackend

backend = JWTAuthenticationBackend()
request = RequestFactory().get('/?token=eyJhbGc...')

user = backend.authenticate(request)
if user:
    print(f"Authenticated: {user.email}")
else:
    print("Authentication failed")
```

##### get_user(user_id)

Get user by ID (required by Django auth backend interface).

**Parameters:**
- `user_id` (int): User primary key

**Returns:**
- `User` object if found
- `None` if not found

**Example:**
```python
backend = JWTAuthenticationBackend()
user = backend.get_user(123)
```

#### Configuration

The backend reads configuration from Django settings:

```python
JWT_SSO_SECRET          # JWT secret key (required)
JWT_SSO_ALGORITHM       # JWT algorithm (default: 'HS256')
JWT_SSO_TOKEN_PARAM     # URL parameter name (default: 'token')
JWT_SSO_EMAIL_CLAIM     # Email claim name (default: 'email')
JWT_SSO_USERNAME_CLAIM  # Username claim (default: None, uses email)
JWT_SSO_FIRST_NAME_CLAIM  # First name claim (default: 'first_name')
JWT_SSO_LAST_NAME_CLAIM   # Last name claim (default: 'last_name')
JWT_SSO_AUTO_CREATE_USERS # Auto-create users (default: False)
```

#### Token Verification Process

1. Extract token from request URL parameter
2. Verify JWT signature using `JWT_SSO_SECRET`
3. Check token expiration
4. Extract user email from token
5. Find or create user in database
6. Update user information from token claims
7. Return authenticated user

#### Error Handling

The backend logs errors and returns `None` for:
- Missing token
- Invalid token format
- Signature verification failure
- Expired token
- Missing email claim
- User not found (when auto-create is disabled)

**Log Messages:**
```python
logger.debug("No JWT token provided")
logger.error("JWT_SSO_SECRET is not configured")
logger.warning(f"JWT token does not contain '{email_claim}' claim")
logger.warning("JWT token has expired")
logger.error("JWT token signature verification failed")
logger.warning(f"User not found in Label Studio: {email}")
```

## Middleware

### JWTAutoLoginMiddleware

Django middleware for automatic user login via JWT token.

```python
from label_studio_sso.middleware import JWTAutoLoginMiddleware
```

#### Class Definition

```python
class JWTAutoLoginMiddleware:
    """
    Middleware to automatically log in users via JWT token.
    """
```

#### Methods

##### __init__(get_response)

Initialize middleware.

**Parameters:**
- `get_response` (callable): Next middleware or view in chain

**Example:**
```python
# Django automatically initializes middleware
middleware = JWTAutoLoginMiddleware(get_response)
```

##### __call__(request)

Process request and auto-login if JWT token present.

**Parameters:**
- `request` (HttpRequest): Django HTTP request object

**Returns:**
- `HttpResponse`: Response from next middleware/view

**Process:**
1. Skip if user already authenticated
2. Check for JWT token in URL parameters
3. Authenticate using `JWTAuthenticationBackend`
4. Log in user if authentication succeeds
5. Continue request processing

**Example:**
```python
# Middleware is called automatically by Django
# User accesses: http://label-studio.com/?token=eyJhbGc...
# Middleware auto-logs in the user
```

#### Configuration

The middleware reads configuration from Django settings:

```python
JWT_SSO_TOKEN_PARAM  # URL parameter name (default: 'token')
```

#### Auto-Login Flow

```
Request with token
        ↓
Already authenticated? → Yes → Skip auto-login
        ↓ No
Extract token from URL
        ↓
Authenticate with JWTAuthenticationBackend
        ↓
Authentication success? → Yes → Log in user
        ↓ No                     ↓
Continue request         Continue request
```

#### Log Messages

```python
logger.debug(f"User already authenticated: {request.user.email}")
logger.info("JWT token detected in URL, attempting auto-login")
logger.info(f"User auto-logged in: {user.email}")
logger.warning("JWT token authentication failed")
```

## Django Integration

### INSTALLED_APPS

```python
INSTALLED_APPS = [
    # ...
    'label_studio_sso',
]
```

### AUTHENTICATION_BACKENDS

```python
AUTHENTICATION_BACKENDS = [
    'label_studio_sso.backends.JWTAuthenticationBackend',  # Must be first
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

**Order Matters:** Place `JWTAuthenticationBackend` **first** for priority.

### MIDDLEWARE

```python
MIDDLEWARE = [
    # ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # Must be after AuthenticationMiddleware
    # ...
]
```

**Order Matters:** Place `JWTAutoLoginMiddleware` **after** `AuthenticationMiddleware`.

## Configuration Settings

### Complete Settings Reference

| Setting | Type | Required | Default | Description |
|---------|------|----------|---------|-------------|
| `JWT_SSO_SECRET` | str | Yes | None | JWT secret key for signature verification |
| `JWT_SSO_ALGORITHM` | str | No | 'HS256' | JWT signing algorithm |
| `JWT_SSO_TOKEN_PARAM` | str | No | 'token' | URL parameter name for JWT token |
| `JWT_SSO_EMAIL_CLAIM` | str | No | 'email' | JWT claim containing user email |
| `JWT_SSO_USERNAME_CLAIM` | str | No | None | JWT claim for username (uses email if None) |
| `JWT_SSO_FIRST_NAME_CLAIM` | str | No | 'first_name' | JWT claim for first name |
| `JWT_SSO_LAST_NAME_CLAIM` | str | No | 'last_name' | JWT claim for last name |
| `JWT_SSO_AUTO_CREATE_USERS` | bool | No | False | Auto-create users on first login |

## JWT Token Format

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

### Token Generation

**Python:**
```python
import jwt
import time

token = jwt.encode(
    {
        'email': 'user@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'iat': int(time.time()),
        'exp': int(time.time()) + 600  # 10 minutes
    },
    'your-secret-key',
    algorithm='HS256'
)
```

**Node.js:**
```javascript
const jwt = require('jsonwebtoken');

const token = jwt.sign(
  {
    email: 'user@example.com',
    first_name: 'John',
    last_name: 'Doe',
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 600  // 10 minutes
  },
  'your-secret-key',
  { algorithm: 'HS256' }
);
```

## Usage Examples

### Basic Authentication

```python
from django.test import RequestFactory
from label_studio_sso.backends import JWTAuthenticationBackend

# Create request with token
factory = RequestFactory()
request = factory.get('/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')

# Authenticate
backend = JWTAuthenticationBackend()
user = backend.authenticate(request)

if user:
    print(f"✅ Authenticated: {user.email}")
else:
    print("❌ Authentication failed")
```

### Manual Login

```python
from django.contrib.auth import login
from django.http import HttpRequest
from label_studio_sso.backends import JWTAuthenticationBackend

def manual_sso_login(request: HttpRequest, token: str):
    """Manually log in user with JWT token"""
    backend = JWTAuthenticationBackend()
    user = backend.authenticate(request, token=token)

    if user:
        login(
            request,
            user,
            backend='label_studio_sso.backends.JWTAuthenticationBackend'
        )
        return True
    return False
```

### Custom Claims

```python
# Django settings
JWT_SSO_EMAIL_CLAIM = 'user_email'
JWT_SSO_FIRST_NAME_CLAIM = 'given_name'
JWT_SSO_LAST_NAME_CLAIM = 'family_name'

# Token structure
{
    "user_email": "user@example.com",
    "given_name": "John",
    "family_name": "Doe",
    "iat": 1234567890,
    "exp": 1234567900
}
```

### Testing in Django Shell

```python
# Django shell
python manage.py shell

>>> from django.test import RequestFactory
>>> from label_studio_sso.backends import JWTAuthenticationBackend
>>> import jwt
>>> import time
>>>
>>> # Generate test token
>>> token = jwt.encode(
...     {'email': 'test@example.com', 'iat': int(time.time()), 'exp': int(time.time()) + 600},
...     'your-secret-key',
...     algorithm='HS256'
... )
>>>
>>> # Create request
>>> factory = RequestFactory()
>>> request = factory.get(f'/?token={token}')
>>>
>>> # Test authentication
>>> backend = JWTAuthenticationBackend()
>>> user = backend.authenticate(request)
>>> print(user.email if user else "Failed")
```

## Error Codes and Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `JWT_SSO_SECRET is not configured` | Missing secret | Set `JWT_SSO_SECRET` in settings |
| `JWT token signature verification failed` | Invalid signature | Check secret matches |
| `JWT token has expired` | Expired token | Generate new token |
| `JWT token does not contain 'email' claim` | Missing email | Include email in token |
| `User not found in Label Studio` | User doesn't exist | Create user or enable auto-create |

## Backward Compatibility

### Legacy Aliases

```python
# Old names (deprecated, for backward compatibility)
from label_studio_sso.backends import ThingsFactoryJWTBackend
from label_studio_sso.middleware import ThingsFactoryAutoLoginMiddleware

# New names (recommended)
from label_studio_sso.backends import JWTAuthenticationBackend
from label_studio_sso.middleware import JWTAutoLoginMiddleware
```

## Next Steps

- **[Configuration Guide](configuration.md)** - Detailed configuration
- **[Examples](examples/)** - Usage examples
- **[Troubleshooting](troubleshooting.md)** - Common issues
