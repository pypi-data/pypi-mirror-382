# Custom JWT System Integration

Example of integrating Label Studio with a custom JWT-based authentication system.

## Overview

This example demonstrates how to integrate Label Studio SSO with any custom authentication system that uses JWT tokens.

## Scenario

You have a custom application that:

- Issues JWT tokens for authenticated users
- Wants to embed Label Studio
- Needs seamless SSO integration

## Architecture

```
┌─────────────────────────┐
│  Your Application       │
│  - User authentication  │
│  - JWT token issuer     │
│  - Label Studio client  │
└────────────┬────────────┘
             │
             │ JWT Token
             │
┌────────────▼────────────┐
│  Label Studio           │
│  - Verify JWT           │
│  - Auto-login           │
│  - Data labeling        │
└─────────────────────────┘
```

## Step 1: Generate JWT Secret

```bash
# Generate a secure random secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Output: x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p
```

**Store this secret securely** - it will be used by both systems.

## Step 2: Configure Label Studio

### Install Package

```bash
pip install label-studio-sso
```

### Django Settings

**label_studio/core/settings/base.py**:

```python
import os

INSTALLED_APPS = [
    # ... existing apps ...
    'label_studio_sso',
]

AUTHENTICATION_BACKENDS = [
    'label_studio_sso.backends.JWTAuthenticationBackend',  # Add first
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]

MIDDLEWARE = [
    # ... existing middleware ...
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # Add after auth
    # ... rest ...
]

# JWT SSO Configuration
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET', 'x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p')
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_TOKEN_PARAM = 'token'
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_AUTO_CREATE_USERS = True  # Auto-create users from JWT

# CORS for your application
CORS_ALLOWED_ORIGINS = [
    'https://your-app.example.com',
]

# Allow iframe
X_FRAME_OPTIONS = 'SAMEORIGIN'
```

### Restart Label Studio

```bash
sudo systemctl restart label-studio
```

## Step 3: Implement JWT Generation in Your App

### Node.js/Express Example

```javascript
// app.js
const express = require("express");
const jwt = require("jsonwebtoken");

const app = express();
const JWT_SECRET = "x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p";
const LABEL_STUDIO_URL = "https://label-studio.example.com";

// Middleware to check if user is authenticated
function requireAuth(req, res, next) {
  if (!req.user) {
    return res.status(401).json({ error: "Not authenticated" });
  }
  next();
}

// Generate JWT token for Label Studio SSO
function generateLabelStudioToken(user) {
  return jwt.sign(
    {
      email: user.email,
      first_name: user.firstName,
      last_name: user.lastName,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 600, // 10 minutes
    },
    JWT_SECRET,
    { algorithm: "HS256" }
  );
}

// Route to redirect to Label Studio with SSO
app.get("/label-studio", requireAuth, (req, res) => {
  const token = generateLabelStudioToken(req.user);
  const labelStudioUrl = `${LABEL_STUDIO_URL}/?token=${token}`;
  res.redirect(labelStudioUrl);
});

// API endpoint to get token (for iframe)
app.get("/api/label-studio-token", requireAuth, (req, res) => {
  const token = generateLabelStudioToken(req.user);
  res.json({ token, url: LABEL_STUDIO_URL });
});

app.listen(3000, () => {
  console.log("Server running on http://localhost:3000");
});
```

### Python/Flask Example

```python
# app.py
from flask import Flask, request, redirect, jsonify
import jwt
import time
import os

app = Flask(__name__)
JWT_SECRET = 'x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p'
LABEL_STUDIO_URL = 'https://label-studio.example.com'

def generate_label_studio_token(user):
    """Generate JWT token for Label Studio SSO"""
    return jwt.encode(
        {
            'email': user['email'],
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'iat': int(time.time()),
            'exp': int(time.time()) + 600  # 10 minutes
        },
        JWT_SECRET,
        algorithm='HS256'
    )

@app.route('/label-studio')
def label_studio():
    """Redirect to Label Studio with SSO token"""
    # Get current user (from session, database, etc.)
    user = get_current_user()  # Your implementation

    if not user:
        return redirect('/login')

    token = generate_label_studio_token(user)
    label_studio_url = f"{LABEL_STUDIO_URL}/?token={token}"
    return redirect(label_studio_url)

@app.route('/api/label-studio-token')
def label_studio_token_api():
    """API endpoint to get Label Studio token"""
    user = get_current_user()

    if not user:
        return jsonify({'error': 'Not authenticated'}), 401

    token = generate_label_studio_token(user)
    return jsonify({'token': token, 'url': LABEL_STUDIO_URL})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```

### Django Example

```python
# views.py
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import jwt
import time
import os

JWT_SECRET = 'x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p'
LABEL_STUDIO_URL = 'https://label-studio.example.com'

def generate_label_studio_token(user):
    """Generate JWT token for Label Studio SSO"""
    return jwt.encode(
        {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'iat': int(time.time()),
            'exp': int(time.time()) + 600  # 10 minutes
        },
        JWT_SECRET,
        algorithm='HS256'
    )

@login_required
def label_studio_redirect(request):
    """Redirect to Label Studio with SSO token"""
    token = generate_label_studio_token(request.user)
    label_studio_url = f"{LABEL_STUDIO_URL}/?token={token}"
    return redirect(label_studio_url)

@login_required
def label_studio_token_api(request):
    """API endpoint to get Label Studio token"""
    token = generate_label_studio_token(request.user)
    return JsonResponse({'token': token, 'url': LABEL_STUDIO_URL})
```

## Step 4: Embed Label Studio in iframe

### HTML + JavaScript

```html
<!DOCTYPE html>
<html>
  <head>
    <title>My App - Label Studio</title>
    <style>
      body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
      }

      .header {
        background: #333;
        color: white;
        padding: 15px;
      }

      .content {
        display: flex;
        height: calc(100vh - 50px);
      }

      iframe {
        flex: 1;
        border: none;
      }
    </style>
  </head>
  <body>
    <div class="header">
      <h1>My Application - Data Labeling</h1>
    </div>

    <div class="content">
      <iframe id="label-studio-iframe"></iframe>
    </div>

    <script>
      async function loadLabelStudio() {
        try {
          // Fetch token from your API
          const response = await fetch("/api/label-studio-token");
          const data = await response.json();

          // Build iframe URL with token
          const iframe = document.getElementById("label-studio-iframe");
          iframe.src = `${data.url}?token=${data.token}`;

          console.log("Label Studio loaded successfully");
        } catch (error) {
          console.error("Failed to load Label Studio:", error);
          alert("Failed to load Label Studio. Please try again.");
        }
      }

      // Load Label Studio when page loads
      loadLabelStudio();
    </script>
  </body>
</html>
```

### React Component

```jsx
// LabelStudioEmbed.jsx
import React, { useState, useEffect } from "react";

function LabelStudioEmbed() {
  const [iframeUrl, setIframeUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadLabelStudio() {
      try {
        const response = await fetch("/api/label-studio-token");
        const data = await response.json();

        setIframeUrl(`${data.url}?token=${data.token}`);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }

    loadLabelStudio();
  }, []);

  if (loading) {
    return <div>Loading Label Studio...</div>;
  }

  if (error) {
    return <div>Error loading Label Studio: {error}</div>;
  }

  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <iframe
        src={iframeUrl}
        style={{ width: "100%", height: "100%", border: "none" }}
        allow="fullscreen"
        title="Label Studio"
      />
    </div>
  );
}

export default LabelStudioEmbed;
```

## Step 5: Create Users in Label Studio

### Option 1: Auto-Create (Enabled in settings)

With `JWT_SSO_AUTO_CREATE_USERS = True`, users are created automatically on first login.

### Option 2: Pre-Create Users

```python
# manage.py script
from django.contrib.auth import get_user_model

User = get_user_model()

# Create user
User.objects.create(
    email='user@example.com',
    username='user@example.com',
    first_name='John',
    last_name='Doe'
)
```

### Option 3: Sync via API

```javascript
// sync-users.js
const axios = require("axios");

const LABEL_STUDIO_URL = "https://label-studio.example.com";
const LABEL_STUDIO_API_TOKEN = "your-label-studio-api-token";

async function syncUser(user) {
  const response = await axios.post(
    `${LABEL_STUDIO_URL}/api/users`,
    {
      email: user.email,
      username: user.email,
      first_name: user.firstName,
      last_name: user.lastName,
    },
    {
      headers: {
        Authorization: `Token ${LABEL_STUDIO_API_TOKEN}`,
      },
    }
  );

  console.log(`Synced user: ${user.email}`);
  return response.data;
}

// Sync all users
async function syncAllUsers(users) {
  for (const user of users) {
    await syncUser(user);
  }
}
```

## JWT Token Structure

### Required Claims

```json
{
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234567900
}
```

### Recommended Claims

```json
{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "iat": 1234567890,
  "exp": 1234567900
}
```

### Custom Claims

If your JWT uses different claim names:

```python
# Label Studio settings
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

## Testing

### 1. Generate Test Token

```javascript
const jwt = require("jsonwebtoken");

const token = jwt.sign(
  {
    email: "test@example.com",
    first_name: "Test",
    last_name: "User",
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 600,
  },
  "x7KjN9mP2vL5wQ8rT4gH1nY6uB3sC0dE9fA5xZ7kM2p",
  { algorithm: "HS256" }
);

console.log(token);
```

### 2. Test Direct Access

```
https://label-studio.example.com/?token=YOUR_TOKEN
```

### 3. Verify Logs

```bash
# Label Studio logs
tail -f /var/log/label-studio/label-studio.log | grep "JWT"

# Expected output:
# INFO: JWT token detected in URL, attempting auto-login
# INFO: JWT token verified for email: test@example.com
# INFO: User auto-logged in: test@example.com
```

## Security Best Practices

### 1. Use Environment Variables

```javascript
// ✅ Good
const JWT_SECRET = process.env.JWT_SSO_SECRET;

// ❌ Bad
const JWT_SECRET = "hardcoded-secret";
```

### 2. Short Token Expiration

```javascript
// ✅ Good: 10 minutes
exp: Math.floor(Date.now() / 1000) + 600;

// ⚠️ Acceptable for development: 1 hour
exp: Math.floor(Date.now() / 1000) + 3600;

// ❌ Bad: 1 day
exp: Math.floor(Date.now() / 1000) + 86400;
```

### 3. HTTPS Only (Production)

```python
# Django settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
```

### 4. Validate JWT Claims

```javascript
// Validate before signing
function validateUser(user) {
  if (!user.email) throw new Error("Email required");
  if (!user.email.includes("@")) throw new Error("Invalid email");
  return true;
}
```

## Troubleshooting

### Token Not Working

**Check secret match:**

```bash
# Your app
echo $JWT_SSO_SECRET

# Label Studio
python manage.py shell
>>> from django.conf import settings
>>> print(settings.JWT_SSO_SECRET)
```

### User Not Created

**Enable auto-create:**

```python
JWT_SSO_AUTO_CREATE_USERS = True
```

### CORS Errors

**Add your domain:**

```python
CORS_ALLOWED_ORIGINS = [
    'https://your-app.example.com',
]
```

## Complete Working Example

See the [full example repository](https://github.com/aidoop/label-studio-sso-example) for a complete working implementation.

## Related Examples

- [Things-Factory Integration](things-factory.md)
- [Keycloak Integration](keycloak.md)
