# Troubleshooting Guide

Common issues and solutions for `label-studio-sso`.

## Common Issues

### 1. JWT Token Signature Verification Failed

**Error Message:**

```
ERROR: JWT token signature verification failed
```

**Cause:** JWT secrets don't match between external system and Label Studio.

**Solution:**

```bash
# 1. Check external system JWT secret
echo $JWT_SSO_SECRET

# 2. Check Label Studio JWT secret
# In Django shell:
python manage.py shell
>>> from django.conf import settings
>>> print(settings.JWT_SSO_SECRET)

# 3. Verify they are IDENTICAL
# If different, update one to match the other
```

**Prevention:**

- Store secret in a shared secret management system
- Use environment variables consistently
- Document the secret generation process

---

### 2. User Not Found in Label Studio

**Error Message:**

```
WARNING: User not found in Label Studio: user@example.com
```

**Cause:** User doesn't exist and auto-create is disabled.

**Solution:**

**Option 1: Create user manually**

```bash
cd /path/to/label-studio
python manage.py createsuperuser --email user@example.com
```

**Option 2: Enable auto-create**

```python
# Django settings
JWT_SSO_AUTO_CREATE_USERS = True
```

**Option 3: Sync users from external system**

```python
# Use Things-Factory user sync or custom sync script
```

---

### 3. JWT Token Has Expired

**Error Message:**

```
WARNING: JWT token has expired
```

**Cause:** Token expiration time has passed.

**Solution:**

```python
# Generate new token with longer expiration
import jwt
import time

token = jwt.encode(
    {
        'email': 'user@example.com',
        'iat': int(time.time()),
        'exp': int(time.time()) + 3600  # 1 hour instead of 10 minutes
    },
    'your-secret-key',
    algorithm='HS256'
)
```

**Best Practice:**

- Development: 1 hour expiration
- Production: 5-10 minutes expiration
- Implement token refresh mechanism

---

### 4. No Auto-Login (User Not Logged In)

**Symptoms:**

- Token in URL but user not logged in
- Redirected to login page

**Causes & Solutions:**

**A. Middleware not configured**

```python
# Check MIDDLEWARE in settings.py
MIDDLEWARE = [
    # ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # Must be here
    # ...
]
```

**B. Wrong middleware order**

```python
# ❌ Wrong
MIDDLEWARE = [
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # Too early
    'django.contrib.auth.middleware.AuthenticationMiddleware',
]

# ✅ Correct
MIDDLEWARE = [
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # After auth middleware
]
```

**C. Token parameter name mismatch**

```python
# Settings
JWT_SSO_TOKEN_PARAM = 'sso_token'

# URL must match
http://label-studio.com/?sso_token=eyJhbGc...  # ✅
http://label-studio.com/?token=eyJhbGc...      # ❌
```

---

### 5. JWT_SSO_SECRET Not Configured

**Error Message:**

```
ERROR: JWT_SSO_SECRET is not configured
```

**Cause:** Missing JWT_SSO_SECRET in Django settings.

**Solution:**

```python
# 1. Add to settings.py
import os
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')

# 2. Set environment variable
export JWT_SSO_SECRET="your-secret-key-here"

# 3. Verify
python manage.py shell
>>> from django.conf import settings
>>> assert settings.JWT_SSO_SECRET is not None
```

---

### 6. CORS Errors in iframe

**Error Message (Browser Console):**

```
Access to XMLHttpRequest at 'http://label-studio.com' from origin 'http://things-factory.com' has been blocked by CORS policy
```

**Cause:** CORS not configured properly.

**Solution:**

```python
# Django settings
CORS_ALLOWED_ORIGINS = [
    'https://things-factory.example.com',
    'https://app.example.com',
]

# Or for development only
CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ Never use in production
```

---

### 7. iframe Not Loading (X-Frame-Options)

**Error Message (Browser Console):**

```
Refused to display 'http://label-studio.com' in a frame because it set 'X-Frame-Options' to 'DENY'
```

**Cause:** X-Frame-Options blocking iframe.

**Solution:**

```python
# Django settings
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Allow same-origin iframes

# Or allow specific domains
X_FRAME_OPTIONS = 'ALLOW-FROM https://things-factory.example.com'
```

---

### 8. Invalid JWT Token Format

**Error Message:**

```
ERROR: Invalid JWT token: Not enough segments
```

**Cause:** Malformed JWT token.

**Solution:**

```python
# Verify token format
import jwt

# Valid JWT has 3 parts separated by dots
# header.payload.signature
# Example: eyJhbGc...eyJlbWF...SflKxw

token = "your-token-here"
parts = token.split('.')
print(f"Token parts: {len(parts)}")  # Should be 3

# Decode to check structure
try:
    header = jwt.get_unverified_header(token)
    payload = jwt.decode(token, options={"verify_signature": False})
    print(f"Header: {header}")
    print(f"Payload: {payload}")
except Exception as e:
    print(f"Invalid token: {e}")
```

---

### 9. Token Missing Required Claims

**Error Message:**

```
WARNING: JWT token does not contain 'email' claim
```

**Cause:** JWT token missing required email claim.

**Solution:**

```python
# Ensure token includes email
token = jwt.encode(
    {
        'email': 'user@example.com',  # ← Required
        'iat': int(time.time()),
        'exp': int(time.time()) + 600
    },
    'your-secret-key',
    algorithm='HS256'
)

# Or configure custom claim name
JWT_SSO_EMAIL_CLAIM = 'user_email'  # If your token uses different claim
```

---

### 10. Users Auto-Created with Wrong Permissions

**Symptoms:**

- Users created but can't access Label Studio features
- Permission denied errors

**Cause:** Auto-created users have minimal permissions.

**Solution:**

```python
# Disable auto-create and sync users with proper permissions
JWT_SSO_AUTO_CREATE_USERS = False

# Use external user provisioning (e.g., Things-Factory sync)
# Or create users manually with correct roles
```

---

## Debugging Tools

### 1. Enable Debug Logging

```python
# Django settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'label_studio_sso': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

**Log Output:**

```
DEBUG: No JWT token provided
INFO: JWT token detected in URL, attempting auto-login
INFO: JWT token verified for email: user@example.com
INFO: User found: user@example.com
INFO: User auto-logged in: user@example.com
```

### 2. Test JWT Token

```python
# Django shell
python manage.py shell

>>> import jwt
>>> from django.conf import settings
>>>
>>> token = "your-token-here"
>>>
>>> # Decode without verification (for debugging)
>>> payload = jwt.decode(token, options={"verify_signature": False})
>>> print(payload)
>>>
>>> # Decode with verification
>>> payload = jwt.decode(token, settings.JWT_SSO_SECRET, algorithms=['HS256'])
>>> print(payload)
```

### 3. Check Django Configuration

```python
# Django shell
python manage.py shell

>>> from django.conf import settings
>>>
>>> # Check installed apps
>>> print('label_studio_sso' in settings.INSTALLED_APPS)
>>>
>>> # Check authentication backends
>>> print('label_studio_sso.backends.JWTAuthenticationBackend' in settings.AUTHENTICATION_BACKENDS)
>>>
>>> # Check middleware
>>> print('label_studio_sso.middleware.JWTAutoLoginMiddleware' in settings.MIDDLEWARE)
>>>
>>> # Check JWT settings
>>> print(f"SECRET: {settings.JWT_SSO_SECRET[:10]}...")
>>> print(f"ALGORITHM: {settings.JWT_SSO_ALGORITHM}")
>>> print(f"TOKEN_PARAM: {settings.JWT_SSO_TOKEN_PARAM}")
```

### 4. Test Authentication Manually

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
>>> # Create test request
>>> factory = RequestFactory()
>>> request = factory.get(f'/?token={token}')
>>>
>>> # Test authentication
>>> backend = JWTAuthenticationBackend()
>>> user = backend.authenticate(request)
>>>
>>> if user:
...     print(f"✅ Success: {user.email}")
... else:
...     print("❌ Failed")
```

### 5. Browser Developer Tools

**Check iframe URL:**

```javascript
// Browser console
const iframe = document.querySelector("iframe");
console.log(iframe.src);
// Should include: ?token=eyJhbGc...
```

**Check localStorage:**

```javascript
// Browser console
console.log(localStorage.getItem("access-token"));
```

**Check network requests:**

1. Open DevTools → Network tab
2. Access Label Studio with token
3. Look for authentication-related requests
4. Check request/response headers

---

## Diagnostic Checklist

Use this checklist to diagnose issues:

### Configuration

- [ ] `label_studio_sso` in `INSTALLED_APPS`
- [ ] `JWTAuthenticationBackend` in `AUTHENTICATION_BACKENDS` (first)
- [ ] `JWTAutoLoginMiddleware` in `MIDDLEWARE` (after `AuthenticationMiddleware`)
- [ ] `JWT_SSO_SECRET` configured
- [ ] `JWT_SSO_SECRET` matches external system

### Token

- [ ] Token included in URL: `?token=...`
- [ ] Token format valid (3 parts: header.payload.signature)
- [ ] Token not expired
- [ ] Token includes `email` claim
- [ ] Token signature verifies with `JWT_SSO_SECRET`

### User

- [ ] User exists in Label Studio (or auto-create enabled)
- [ ] User has correct email
- [ ] User is active (`is_active=True`)

### Network

- [ ] CORS configured for external domain
- [ ] X-Frame-Options allows iframe
- [ ] HTTPS used (production)
- [ ] No network errors in browser console

---

## Getting Help

If you're still stuck:

1. **Check Logs:**

   ```bash
   # Django logs
   tail -f /var/log/label-studio/label-studio.log | grep "JWT"

   # System logs
   journalctl -u label-studio -f
   ```

2. **Search GitHub Issues:**

   - [Existing issues](https://github.com/aidoop/label-studio-sso/issues)
   - Search for error message

3. **Create New Issue:**
   Include:

   - Python version (`python --version`)
   - Django version (`pip show django`)
   - Label Studio version (`pip show label-studio`)
   - label-studio-sso version (`pip show label-studio-sso`)
   - Relevant Django settings (redact secrets!)
   - Complete error logs
   - Steps to reproduce

4. **Ask in Discussions:**
   - [GitHub Discussions](https://github.com/aidoop/label-studio-sso/discussions)

---

## Related Documentation

- [Configuration Guide](configuration.md) - Detailed configuration
- [API Reference](api-reference.md) - API documentation
- [Quick Start](quick-start.md) - Getting started guide
