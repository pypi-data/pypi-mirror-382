# Integration Examples

Example integrations of Label Studio SSO with various systems.

## Available Examples

### 1. [Things-Factory Integration](things-factory.md)

Complete integration example with Things-Factory enterprise framework.

**Features:**

- iframe embedding
- User synchronization
- Permission mapping
- GraphQL API integration

**Use Case:** Enterprise applications built with Things-Factory

---

### 2. [Custom JWT System](custom-jwt.md)

Generic integration example for any custom JWT-based authentication system.

**Features:**

- Node.js/Express implementation
- Python/Flask implementation
- Django implementation
- React component example

**Use Case:** Custom applications with JWT authentication

---

## Quick Start

### 1. Choose Your Integration Type

- **Things-Factory**: Use [things-factory.md](things-factory.md)
- **Custom System**: Use [custom-jwt.md](custom-jwt.md)

### 2. Common Setup Steps

All integrations require:

1. **Install label-studio-sso**

   ```bash
   pip install label-studio-sso
   ```

2. **Configure Django Settings**

   ```python
   INSTALLED_APPS = [..., 'label_studio_sso']
   AUTHENTICATION_BACKENDS = ['label_studio_sso.backends.JWTAuthenticationBackend', ...]
   MIDDLEWARE = [..., 'label_studio_sso.middleware.JWTAutoLoginMiddleware']
   JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')
   ```

3. **Generate JWT Tokens in Your System**

   ```javascript
   const token = jwt.sign(
     { email: user.email, iat: now, exp: now + 600 },
     JWT_SECRET,
     { algorithm: "HS256" }
   );
   ```

4. **Access Label Studio with Token**
   ```
   https://label-studio.com/?token=YOUR_JWT_TOKEN
   ```

### 3. Integration Patterns

#### Pattern A: Direct Redirect

```javascript
app.get("/label-studio", (req, res) => {
  const token = generateJWT(req.user);
  res.redirect(`https://label-studio.com/?token=${token}`);
});
```

#### Pattern B: iframe Embedding

```html
<iframe src="https://label-studio.com/?token=YOUR_TOKEN"></iframe>
```

#### Pattern C: API + Dynamic Loading

```javascript
const { token } = await fetch("/api/label-studio-token").then((r) => r.json());
iframe.src = `https://label-studio.com/?token=${token}`;
```

## Example Code Templates

### JavaScript/Node.js

```javascript
const jwt = require("jsonwebtoken");

function generateLabelStudioToken(user, secret) {
  return jwt.sign(
    {
      email: user.email,
      first_name: user.firstName,
      last_name: user.lastName,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 600,
    },
    secret,
    { algorithm: "HS256" }
  );
}
```

### Python

```python
import jwt
import time

def generate_label_studio_token(user, secret):
    return jwt.encode(
        {
            'email': user['email'],
            'first_name': user.get('first_name', ''),
            'last_name': user.get('last_name', ''),
            'iat': int(time.time()),
            'exp': int(time.time()) + 600
        },
        secret,
        algorithm='HS256'
    )
```

### TypeScript

```typescript
import jwt from "jsonwebtoken";

interface User {
  email: string;
  firstName?: string;
  lastName?: string;
}

function generateLabelStudioToken(user: User, secret: string): string {
  return jwt.sign(
    {
      email: user.email,
      first_name: user.firstName || "",
      last_name: user.lastName || "",
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 600,
    },
    secret,
    { algorithm: "HS256" }
  );
}
```

## Testing Your Integration

### 1. Generate Test Token

```bash
# Node.js
node -e "const jwt = require('jsonwebtoken'); console.log(jwt.sign({email:'test@example.com',iat:Math.floor(Date.now()/1000),exp:Math.floor(Date.now()/1000)+600},'your-secret',{algorithm:'HS256'}))"

# Python
python -c "import jwt,time; print(jwt.encode({'email':'test@example.com','iat':int(time.time()),'exp':int(time.time())+600},'your-secret',algorithm='HS256'))"
```

### 2. Test Direct Access

```
https://label-studio.example.com/?token=YOUR_TEST_TOKEN
```

### 3. Verify Logs

```bash
tail -f /var/log/label-studio/label-studio.log | grep "JWT"
```

## Common Integration Issues

### Issue: Token Signature Verification Failed

**Cause:** JWT secrets don't match

**Solution:**

```bash
# Check both systems use same secret
echo $JWT_SSO_SECRET  # Your system
python manage.py shell  # Label Studio
>>> from django.conf import settings
>>> print(settings.JWT_SSO_SECRET)
```

### Issue: User Not Found

**Cause:** User doesn't exist in Label Studio

**Solution:**

```python
# Enable auto-create
JWT_SSO_AUTO_CREATE_USERS = True

# Or create user manually
python manage.py createsuperuser --email user@example.com
```

### Issue: CORS Error in iframe

**Cause:** CORS not configured

**Solution:**

```python
# Label Studio settings
CORS_ALLOWED_ORIGINS = [
    'https://your-app.example.com',
]
```

## Next Steps

1. Choose an example that matches your use case
2. Follow the step-by-step guide
3. Customize for your specific needs
4. Test thoroughly before production deployment

## Contributing Examples

Have an integration example to share? Please contribute!

1. Fork the repository
2. Add your example to `docs/examples/`
3. Follow the existing format
4. Submit a pull request

## Support

- [Configuration Guide](../configuration.md)
- [API Reference](../api-reference.md)
- [Troubleshooting](../troubleshooting.md)
- [GitHub Issues](https://github.com/aidoop/label-studio-sso/issues)
