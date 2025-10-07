# Label Studio SSO - Universal JWT Authentication

Universal JWT-based Single Sign-On (SSO) authentication plugin for Label Studio.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version: 3.0.0](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/aidoop/label-studio-sso)

---

## 🎯 Overview

This package provides a simple, universal JWT-based authentication backend for **Label Studio** that works with any external system capable of issuing JWT tokens.

### Key Features

- ✅ **Universal JWT Support**: Works with any JWT-issuing system
- ✅ **URL Parameter Authentication**: Pass JWT tokens via URL parameters
- ✅ **Configurable JWT Claims**: Map any JWT claim to user fields
- ✅ **Auto-User Creation**: Optionally create users automatically from JWT data
- ✅ **Zero Label Studio Modifications**: Pure Django plugin, no core changes needed
- ✅ **Framework Agnostic**: Integrate with Node.js, Python, Java, .NET, or any JWT-capable system

---

## 📦 Installation

### 1. Install via pip

```bash
pip install label-studio-sso
```

---

## 🚀 Quick Start

### 1. Configure Environment Variables

```bash
# Required: JWT secret key (must match your external system)
export JWT_SSO_SECRET="your-shared-secret-key"

# Optional: Customize JWT settings
export JWT_SSO_ALGORITHM="HS256"                    # Default: HS256
export JWT_SSO_TOKEN_PARAM="token"                  # Default: token
export JWT_SSO_EMAIL_CLAIM="email"                  # Default: email
export JWT_SSO_USERNAME_CLAIM="username"            # Default: None (uses email)
export JWT_SSO_AUTO_CREATE_USERS="false"            # Default: false
```

### 2. Update Label Studio Settings

Add to `label_studio/core/settings/label_studio.py`:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'label_studio_sso',  # Add this
]

# Add to AUTHENTICATION_BACKENDS (must be first!)
AUTHENTICATION_BACKENDS = [
    'label_studio_sso.backends.JWTAuthenticationBackend',  # Add this first
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Add to MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'core.middleware.DisableCSRF',
    'django.middleware.csrf.CsrfViewMiddleware',
    'core.middleware.XApiKeySupportMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # Add this after AuthenticationMiddleware
    # ... rest of middleware ...
]

# JWT SSO Configuration
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')
JWT_SSO_ALGORITHM = os.getenv('JWT_SSO_ALGORITHM', 'HS256')
JWT_SSO_TOKEN_PARAM = os.getenv('JWT_SSO_TOKEN_PARAM', 'token')
JWT_SSO_EMAIL_CLAIM = os.getenv('JWT_SSO_EMAIL_CLAIM', 'email')
JWT_SSO_USERNAME_CLAIM = os.getenv('JWT_SSO_USERNAME_CLAIM', None)
JWT_SSO_AUTO_CREATE_USERS = os.getenv('JWT_SSO_AUTO_CREATE_USERS', 'false').lower() == 'true'
```

### 3. How It Works

```
External System (Your App)
  ↓ Generate JWT token with user info
  ↓ Create URL: https://label-studio.example.com?token=eyJhbGc...
  ↓
User clicks link or iframe loads
  ↓
Label Studio
  ↓ JWTAutoLoginMiddleware extracts token from URL
  ↓ JWTAuthenticationBackend validates JWT signature
  ↓ Extract user info from JWT claims
  ↓ Find or create Label Studio user
  ↓ Auto-login user
  ✅ User authenticated!
```

---

## 🔧 Usage Examples

### Example 1: Node.js/Express Integration

```javascript
const jwt = require('jsonwebtoken');

// Generate JWT token for user
const token = jwt.sign(
  {
    email: "user@example.com",
    username: "john_doe",
    first_name: "John",
    last_name: "Doe",
    exp: Math.floor(Date.now() / 1000) + (10 * 60)  // 10 minutes
  },
  process.env.JWT_SSO_SECRET,
  { algorithm: 'HS256' }
);

// Redirect user to Label Studio
const labelStudioUrl = `https://label-studio.example.com?token=${token}`;
res.redirect(labelStudioUrl);
```

### Example 2: Python/Django Integration

```python
import jwt
from datetime import datetime, timedelta

# Generate JWT token
token = jwt.encode(
    {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'exp': datetime.utcnow() + timedelta(minutes=10)
    },
    settings.JWT_SSO_SECRET,
    algorithm='HS256'
)

# Embed in iframe or redirect
label_studio_url = f"https://label-studio.example.com?token={token}"
```

### Example 3: Java/Spring Boot Integration

```java
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;

// Generate JWT token
String token = Jwts.builder()
    .claim("email", user.getEmail())
    .claim("first_name", user.getFirstName())
    .claim("last_name", user.getLastName())
    .setExpiration(new Date(System.currentTimeMillis() + 600000))  // 10 minutes
    .signWith(SignatureAlgorithm.HS256, jwtSecret)
    .compact();

// Redirect to Label Studio
String labelStudioUrl = "https://label-studio.example.com?token=" + token;
return "redirect:" + labelStudioUrl;
```

### Example 4: Custom JWT Claims Mapping

If your JWT uses different claim names:

```bash
# Configure custom JWT claim mapping
export JWT_SSO_EMAIL_CLAIM="user_email"
export JWT_SSO_USERNAME_CLAIM="username"
export JWT_SSO_FIRST_NAME_CLAIM="given_name"
export JWT_SSO_LAST_NAME_CLAIM="family_name"
```

Then your JWT payload:
```json
{
  "user_email": "user@example.com",
  "username": "john_doe",
  "given_name": "John",
  "family_name": "Doe",
  "exp": 1234567890
}
```

---

## ⚙️ Configuration Options

### Required Settings

| Setting | Description | Example |
|---------|-------------|---------|
| `JWT_SSO_SECRET` | Shared secret key for JWT verification | `"your-secret-key"` |

### Optional Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `JWT_SSO_ALGORITHM` | `HS256` | JWT algorithm (HS256, HS512, RS256, etc.) |
| `JWT_SSO_TOKEN_PARAM` | `token` | URL parameter name for JWT token |
| `JWT_SSO_EMAIL_CLAIM` | `email` | JWT claim containing user email |
| `JWT_SSO_USERNAME_CLAIM` | `None` | JWT claim containing username (optional) |
| `JWT_SSO_FIRST_NAME_CLAIM` | `first_name` | JWT claim for first name |
| `JWT_SSO_LAST_NAME_CLAIM` | `last_name` | JWT claim for last name |
| `JWT_SSO_AUTO_CREATE_USERS` | `false` | Auto-create users if not found in Label Studio |

---

## 🔒 Security Best Practices

### 1. Use Strong Secrets

Generate a cryptographically secure secret:

```python
import secrets
secret = secrets.token_urlsafe(32)
print(f"JWT_SSO_SECRET={secret}")
```

### 2. Use HTTPS Only

JWT tokens in URLs are visible in browser history and server logs. **Always use HTTPS** in production.

### 3. Short Token Expiration

Use short-lived tokens (5-10 minutes recommended):

```javascript
// Good: 10 minutes
exp: Math.floor(Date.now() / 1000) + (10 * 60)

// Bad: 24 hours
exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60)
```

### 4. Never Hardcode Secrets

Always use environment variables:

```bash
# Good
export JWT_SSO_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Bad
JWT_SSO_SECRET = "hardcoded-secret"  # ❌ Never do this
```

---

## 🧪 Testing

### Local Testing

```bash
# 1. Set environment variables
export JWT_SSO_SECRET="test-secret-key"
export JWT_SSO_AUTO_CREATE_USERS="true"

# 2. Start Label Studio
cd /path/to/label-studio
python manage.py runserver

# 3. Generate test token
python -c "
import jwt
from datetime import datetime, timedelta

token = jwt.encode(
    {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'exp': datetime.utcnow() + timedelta(minutes=10)
    },
    'test-secret-key',
    algorithm='HS256'
)
print(f'http://localhost:8080?token={token}')
"

# 4. Open the URL in browser
```

---

## 📋 Requirements

- **Python**: 3.8+
- **Label Studio**: 1.7.0+
- **Django**: 3.2+
- **PyJWT**: 2.0+

---

## 🛠️ Development

### Install from Source

```bash
git clone https://github.com/aidoop/label-studio-sso.git
cd label-studio-sso
pip install -e .
```

### Run Tests

```bash
pytest tests/
```

### Build Package

```bash
python -m build
```

---

## 🤝 Contributing

Issues and pull requests are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🔗 Related Projects

- [Label Studio](https://github.com/HumanSignal/label-studio) - Open source data labeling platform
- [PyJWT](https://github.com/jpadilla/pyjwt) - JSON Web Token implementation in Python

---

## 💡 Use Cases

This package can integrate Label Studio with:

- ✅ Custom web portals (Node.js, Django, Flask, Spring Boot, .NET Core)
- ✅ Enterprise SSO systems (Keycloak, Auth0, Okta with JWT)
- ✅ Internal authentication services
- ✅ Microservices architectures
- ✅ Any system that can generate JWT tokens

---

## 📞 Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/aidoop/label-studio-sso/issues).

---

## 🚀 Changelog

### v3.0.0 (2025-01-XX)
- Complete refactoring to universal JWT authentication
- Removed framework-specific implementations
- Simplified configuration
- Enhanced documentation
- Production-ready status

### v2.0.x
- Session-based authentication (deprecated)
- Framework-specific implementation (deprecated)

### v1.0.x
- Initial JWT URL parameter support
