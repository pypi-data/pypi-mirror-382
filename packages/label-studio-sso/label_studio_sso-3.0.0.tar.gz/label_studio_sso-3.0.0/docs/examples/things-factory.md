# Things-Factory Integration Example

Complete example of integrating Label Studio with Things-Factory.

## Overview

This example shows how to:

1. Configure Label Studio SSO for Things-Factory
2. Generate JWT tokens in Things-Factory
3. Embed Label Studio in Things-Factory iframe
4. Sync users between systems

## Architecture

```
┌─────────────────────────┐
│  Things-Factory         │
│                         │
│  1. User logs in        │
│  2. Clicks Label Studio │
│  3. Generate JWT token  │
│  4. Open iframe         │
└────────────┬────────────┘
             │
             │ iframe with JWT token
             │ ?token=eyJhbGc...&interfaces=panel,controls,annotations:menu
             │
┌────────────▼────────────┐
│  Label Studio           │
│                         │
│  5. Verify JWT token    │
│  6. Auto-login user     │
│  7. Show minimal UI     │
└─────────────────────────┘
```

## Things-Factory Configuration

### 1. Environment Variables

```bash
# .env
LABEL_STUDIO_URL=https://label-studio.example.com
LABEL_STUDIO_API_TOKEN=your-api-token-here
```

### 2. Config File

**config/label-studio.config.js**:

```javascript
module.exports = {
  labelStudio: {
    serverUrl: process.env.LABEL_STUDIO_URL || "http://localhost:8080",
    apiToken: process.env.LABEL_STUDIO_API_TOKEN || "",
    interfaces: "panel,controls,annotations:menu",
  },
};
```

### 3. Client Component

**client/label-studio-wrapper.ts**:

```typescript
import { LitElement, html, css } from "lit";
import { customElement, state } from "lit/decorators.js";

@customElement("label-studio-wrapper")
export class LabelStudioWrapper extends LitElement {
  static styles = css`
    :host {
      display: block;
      height: 100%;
    }

    iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
  `;

  @state() private iframeUrl: string = "";

  async connectedCallback() {
    super.connectedCallback();
    await this.buildIframeUrl();
  }

  async buildIframeUrl() {
    // Get Label Studio config from Things-Factory
    const config = await this.getConfig();

    // Get JWT token from localStorage
    const token = localStorage.getItem("access-token");

    // Build URL with token and interfaces
    const params = new URLSearchParams({
      token: token || "",
      interfaces: config.interfaces || "panel,controls,annotations:menu",
    });

    this.iframeUrl = `${config.serverUrl}?${params.toString()}`;
  }

  async getConfig() {
    // Fetch from Things-Factory GraphQL or config
    return {
      serverUrl: "http://localhost:8080",
      interfaces: "panel,controls,annotations:menu",
    };
  }

  render() {
    return html`
      <iframe
        src=${this.iframeUrl}
        allow="fullscreen"
        allow-same-origin
        allow-scripts
      ></iframe>
    `;
  }
}
```

### 4. Server Route

**server/route.ts**:

```typescript
import { config } from "@things-factory/env";

const LabelStudioConfig = config.get("labelStudio", {});

if (LabelStudioConfig.enabled !== false) {
  process.on("bootstrap-module-menu", (_, menus) => {
    menus.push({
      name: "label-studio",
      icon: "label",
      childrens: [
        {
          name: "data-labeling",
          template: "label-studio-wrapper",
        },
      ],
    });
  });
}
```

## Label Studio Configuration

### 1. Install Package

```bash
pip install label-studio-sso
```

### 2. Django Settings

**label_studio/core/settings/base.py**:

```python
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

# JWT SSO Configuration
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_TOKEN_PARAM = 'token'
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_AUTO_CREATE_USERS = False  # Use Things-Factory user sync

# CORS for Things-Factory
CORS_ALLOWED_ORIGINS = [
    'https://things-factory.example.com',
]

# Allow iframe embedding
X_FRAME_OPTIONS = 'SAMEORIGIN'
```

### 3. Environment Variables

```bash
# Label Studio .env
JWT_SSO_SECRET=your-shared-secret-key
```

**Important:** This secret must match the one used by Things-Factory for JWT generation.

## User Synchronization

### 1. GraphQL Mutation (Things-Factory)

```graphql
mutation {
  syncAllUsersToLabelStudio {
    total
    created
    updated
    deactivated
    skipped
    errors
    results {
      success
      email
      action
      lsUserId
      lsPermissions
      error
    }
  }
}
```

### 2. User Provisioning Service

**server/controller/user-provisioning-service.ts**:

```typescript
import axios from "axios";
import { User } from "@things-factory/auth-base";
import { config } from "@things-factory/env";

export class UserProvisioningService {
  static async syncUser(domain: Domain, user: User): Promise<SyncResult> {
    const config = this.getConfig();

    // Check Label Studio privileges
    const hasLSPrivilege =
      (await User.hasPrivilege("label-studio", "query", domain, user)) ||
      (await User.hasPrivilege("label-studio", "mutation", domain, user));

    if (!hasLSPrivilege) {
      return { success: true, email: user.email, action: "skipped" };
    }

    // Map permissions
    const lsPermissions = {
      is_superuser: user.owner === true,
      is_staff: user.owner === true,
      is_active: true,
    };

    // Create/update user in Label Studio
    const apiUrl = `${config.serverUrl}/api/users`;
    const response = await axios.post(
      apiUrl,
      {
        email: user.email,
        username: user.email,
        first_name: user.name?.split(" ")[0] || "",
        last_name: user.name?.split(" ").slice(1).join(" ") || "",
        ...lsPermissions,
      },
      {
        headers: {
          Authorization: `Token ${config.apiToken}`,
        },
      }
    );

    return {
      success: true,
      email: user.email,
      action: "created",
      lsUserId: response.data.id.toString(),
      lsPermissions: user.owner ? "Admin" : "Staff",
    };
  }

  private static getConfig() {
    return config.get("labelStudio", {
      serverUrl: "",
      apiToken: "",
    });
  }
}
```

## JWT Token Structure

### Things-Factory JWT Token

```javascript
// Things-Factory generates this token
{
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1234567890,
  "exp": 1234567900  // 10 minutes expiration
}
```

**Token Generation (Things-Factory)**:

```typescript
import jwt from "jsonwebtoken";

const token = jwt.sign(
  {
    email: user.email,
    name: user.name,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + 600,
  },
  process.env.JWT_SSO_SECRET,
  { algorithm: "HS256" }
);
```

## Complete Flow

### 1. User Access

```
User → Things-Factory → Label Studio Menu → label-studio-wrapper component
```

### 2. Token Generation

```typescript
// label-studio-wrapper.ts
const token = localStorage.getItem("access-token");
```

### 3. iframe URL

```
https://label-studio.example.com/?token=eyJhbGc...&interfaces=panel,controls,annotations:menu
```

### 4. Auto-Login

```python
# Label Studio
# 1. JWTAutoLoginMiddleware extracts token
# 2. JWTAuthenticationBackend verifies token
# 3. User is logged in
# 4. Session established
```

### 5. UI Rendering

Label Studio shows minimal UI:

- Panel (navigation: undo, redo, reset)
- Controls (submit, update, skip)
- Annotations menu

## Permission Mapping

| Things-Factory       | Label Studio               |
| -------------------- | -------------------------- |
| label-studio + Owner | Admin (is_superuser=true)  |
| label-studio         | Staff (is_superuser=false) |
| No label-studio      | Inactive (is_active=false) |

## Testing

### 1. Generate Test Token

```bash
# In Things-Factory
node -e "
const jwt = require('jsonwebtoken');
const token = jwt.sign(
  { email: 'test@example.com', name: 'Test User', iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + 600 },
  'your-secret-key',
  { algorithm: 'HS256' }
);
console.log(token);
"
```

### 2. Test URL

```
http://localhost:8080/?token=YOUR_TOKEN&interfaces=panel,controls,annotations:menu
```

### 3. Verify Logs

**Things-Factory:**

```bash
DEBUG=things-factory:*,typeorm:* yarn workspace @things-factory/operato-mms run serve:dev
```

**Label Studio:**

```bash
tail -f /var/log/label-studio/label-studio.log | grep "JWT"
```

## Troubleshooting

### Issue 1: Token Not Valid

**Check secret match:**

```bash
# Things-Factory
echo $JWT_SSO_SECRET

# Label Studio
python manage.py shell
>>> from django.conf import settings
>>> print(settings.JWT_SSO_SECRET)
```

### Issue 2: User Not Synced

**Run sync:**

```graphql
mutation {
  syncAllUsersToLabelStudio {
    total
    created
    updated
  }
}
```

### Issue 3: iframe Not Loading

**Check CORS:**

```python
# Label Studio settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Things-Factory dev
    'https://things-factory.example.com',  # Production
]
```

## Production Deployment

### Checklist

- [ ] Use HTTPS for both systems
- [ ] Set strong JWT_SSO_SECRET (32+ bytes)
- [ ] Configure CORS properly
- [ ] Set short token expiration (5-10 minutes)
- [ ] Enable logging
- [ ] Test user sync
- [ ] Document integration for team

## Related Documentation

- [Things-Factory Integration Module](https://github.com/hatiolab/things-factory/tree/main/packages/integration-label-studio)
- [Label Studio SSO Package](https://github.com/aidoop/label-studio-sso)
