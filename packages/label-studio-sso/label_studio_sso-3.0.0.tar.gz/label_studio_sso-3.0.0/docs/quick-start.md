# Quick Start Guide

Get up and running with Label Studio SSO in 5 minutes.

## Overview

This guide will walk you through:

1. Installing the package
2. Configuring Label Studio
3. Testing SSO authentication

## Prerequisites

- Label Studio installed and running
- Admin access to Label Studio settings
- JWT secret shared between your system and Label Studio

## Step 1: Install Package

```bash
pip install label-studio-sso
```

## Step 2: Configure Label Studio

Edit `label_studio/core/settings/base.py`:

```python
import os

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... existing apps ...
    'label_studio_sso',  # Add this
]

# Add to AUTHENTICATION_BACKENDS (at the beginning)
AUTHENTICATION_BACKENDS = [
    'label_studio_sso.backends.JWTAuthenticationBackend',  # Add this first
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Add to MIDDLEWARE (after AuthenticationMiddleware)
MIDDLEWARE = [
    # ... existing middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # Add this
    # ... rest of middleware ...
]

# JWT SSO Configuration
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_TOKEN_PARAM = 'token'
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_AUTO_CREATE_USERS = False  # Set True to auto-create users
```

## Step 3: Set Environment Variables

Create or edit `.env` file:

```bash
# This secret must match your external system's JWT secret
JWT_SSO_SECRET=your-shared-secret-key-here
```

## Step 4: Restart Label Studio

```bash
# If using systemd
sudo systemctl restart label-studio

# If running manually
python label_studio/manage.py runserver 0.0.0.0:8080
```

## Step 5: Create a Test User in Label Studio

Since `JWT_SSO_AUTO_CREATE_USERS` is `False`, create a user manually:

```bash
cd /path/to/label-studio
python manage.py createsuperuser --email test@example.com
```

## Step 6: Generate JWT Token (External System)

In your external system (Things-Factory, custom app, etc.), generate a JWT token:

**Node.js Example:**

```javascript
const jwt = require("jsonwebtoken");

const token = jwt.sign(
  {
    email: "test@example.com",
    name: "Test User",
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 600, // 10 minutes
  },
  "your-shared-secret-key-here",
  { algorithm: "HS256" }
);

console.log(token);
```

**Python Example:**

```python
import jwt
import time

token = jwt.encode(
    {
        'email': 'test@example.com',
        'name': 'Test User',
        'iat': int(time.time()),
        'exp': int(time.time()) + 600  # 10 minutes
    },
    'your-shared-secret-key-here',
    algorithm='HS256'
)

print(token)
```

## Step 7: Test SSO Login

Access Label Studio with the JWT token:

```
http://localhost:8080/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Expected Result:**

- User is automatically logged in
- Redirected to Label Studio dashboard
- User session is established

## Step 8: Verify Authentication

Check Label Studio logs:

```bash
# Check logs for authentication messages
tail -f /var/log/label-studio/label-studio.log | grep "JWT"

# Expected output:
# INFO: JWT token detected in URL, attempting auto-login
# INFO: JWT token verified for email: test@example.com
# INFO: User found: test@example.com
# INFO: User auto-logged in: test@example.com
```

## Complete Working Example

### External System (Node.js)

```javascript
// app.js
const express = require("express");
const jwt = require("jsonwebtoken");

const app = express();
const JWT_SECRET = "your-shared-secret-key-here";
const LABEL_STUDIO_URL = "http://localhost:8080";

app.get("/label-studio", (req, res) => {
  const user = req.user; // Your authenticated user

  const token = jwt.sign(
    {
      email: user.email,
      name: user.name,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 600,
    },
    JWT_SECRET,
    { algorithm: "HS256" }
  );

  const labelStudioUrl = `${LABEL_STUDIO_URL}/?token=${token}`;
  res.redirect(labelStudioUrl);
});

app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
```

### iframe Integration

```html
<!-- Embed Label Studio in your app -->
<!DOCTYPE html>
<html>
  <head>
    <title>My App - Label Studio</title>
  </head>
  <body>
    <h1>Data Labeling</h1>

    <iframe
      id="label-studio-iframe"
      src="http://localhost:8080/?token=YOUR_JWT_TOKEN"
      width="100%"
      height="800px"
      frameborder="0"
      allow="fullscreen"
    ></iframe>

    <script>
      // Generate token dynamically
      async function loadLabelStudio() {
        const response = await fetch("/api/generate-label-studio-token");
        const { token } = await response.json();

        const iframe = document.getElementById("label-studio-iframe");
        iframe.src = `http://localhost:8080/?token=${token}`;
      }

      loadLabelStudio();
    </script>
  </body>
</html>
```

## Troubleshooting Quick Start

### Issue 1: "JWT token signature verification failed"

**Cause:** JWT secrets don't match

**Solution:**

```bash
# Check secrets match
# External system secret
echo "your-shared-secret-key-here"

# Label Studio secret
cat /path/to/label-studio/.env | grep JWT_SSO_SECRET

# They must be identical!
```

### Issue 2: "User not found in Label Studio"

**Cause:** User doesn't exist and auto-create is disabled

**Solution:**

```bash
# Option 1: Create user manually
python manage.py createsuperuser --email test@example.com

# Option 2: Enable auto-create
# In settings.py: JWT_SSO_AUTO_CREATE_USERS = True
```

### Issue 3: Token expired

**Cause:** JWT token has expired

**Solution:** Generate a new token with longer expiration:

```javascript
exp: Math.floor(Date.now() / 1000) + 3600; // 1 hour instead of 10 minutes
```

### Issue 4: No auto-login

**Cause:** Middleware not loaded or misconfigured

**Solution:**

```bash
# Check Django settings
python manage.py diffsettings | grep MIDDLEWARE

# Verify JWTAutoLoginMiddleware is listed
```

## Next Steps

Now that you have SSO working:

1. **[Configuration Guide](configuration.md)** - Learn about all configuration options
2. **[API Reference](api-reference.md)** - Detailed API documentation
3. **[Examples](examples/)** - More usage examples
4. **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Production Checklist

Before deploying to production:

- [ ] Use strong, randomly generated JWT secret (32+ bytes)
- [ ] Enable HTTPS for all Label Studio traffic
- [ ] Set appropriate token expiration times (5-10 minutes recommended)
- [ ] Configure CORS properly
- [ ] Set `DEBUG = False` in Django settings
- [ ] Configure logging for authentication events
- [ ] Test token expiration and refresh flows
- [ ] Document JWT claims structure for your team

## Support

Need help?

- Check [Troubleshooting Guide](troubleshooting.md)
- Search [GitHub Issues](https://github.com/aidoop/label-studio-sso/issues)
- Ask in [GitHub Discussions](https://github.com/aidoop/label-studio-sso/discussions)
