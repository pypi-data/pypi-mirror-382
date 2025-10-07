# Label Studio SSO Documentation

Generic JWT SSO integration for Label Studio - works with any JWT-based authentication system.

## Overview

`label-studio-sso` is a Django app that provides SSO (Single Sign-On) authentication for Label Studio using JWT tokens from any external system. It enables seamless integration between Label Studio and your existing authentication infrastructure.

## Key Features

- ✅ **Generic JWT Authentication**: Works with any JWT-based system (not limited to Things-Factory)
- ✅ **Auto-Login via URL Token**: Automatic user login when accessing Label Studio with a valid JWT token
- ✅ **Configurable Claims Mapping**: Map JWT claims to Django user fields
- ✅ **Optional Auto-Create Users**: Automatically create users on first login (configurable)
- ✅ **Django Standard**: Follows Django authentication backend and middleware patterns
- ✅ **Python 3.8+ & Django 3.2+**: Modern Python and Django support

## How It Works

```
┌─────────────────────┐
│  External System    │
│  (Things-Factory,   │
│   Keycloak, etc.)   │
└──────────┬──────────┘
           │
           │ 1. Generate JWT Token
           │
           ▼
    ┌──────────────────────┐
    │  User Access URL     │
    │  with JWT Token      │
    │  ?token=eyJhbGc...   │
    └──────────┬───────────┘
               │
               │ 2. Token in URL
               │
               ▼
    ┌──────────────────────────┐
    │  JWTAutoLoginMiddleware  │
    │  - Extract token         │
    │  - Verify signature      │
    │  - Authenticate user     │
    └──────────┬───────────────┘
               │
               │ 3. User Logged In
               │
               ▼
    ┌──────────────────────┐
    │   Label Studio       │
    │   (Authenticated)    │
    └──────────────────────┘
```

## Quick Links

- **[Installation Guide](installation.md)** - Install and setup
- **[Quick Start](quick-start.md)** - Get started in 5 minutes
- **[Configuration](configuration.md)** - Detailed configuration options
- **[API Reference](api-reference.md)** - API documentation
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
- **[Examples](examples/)** - Usage examples

## Use Cases

### 1. Things-Factory Integration

Integrate Label Studio with Things-Factory enterprise application framework.

### 2. Custom SSO System

Integrate Label Studio with your custom authentication system using JWT.

### 3. Multi-System Integration

Use Label Studio with multiple external systems, each with their own JWT issuer.

### 4. Microservices Architecture

Integrate Label Studio into microservices with centralized authentication.

## Requirements

- **Python**: 3.8 or higher
- **Django**: 3.2 or higher
- **Label Studio**: Any version (Community or Enterprise)
- **JWT Secret**: Shared secret key between external system and Label Studio

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Support

- **GitHub Issues**: [Report bugs](https://github.com/aidoop/label-studio-sso/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/aidoop/label-studio-sso/discussions)
- **Documentation**: [Full docs](https://github.com/aidoop/label-studio-sso/blob/main/README.md)

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](contributing.md) for guidelines.

## Related Projects

- [Label Studio](https://github.com/HumanSignal/label-studio) - Open source data labeling tool
- [Things-Factory](https://github.com/hatiolab/things-factory) - Modular enterprise application framework
- [PyJWT](https://github.com/jpadilla/pyjwt) - JSON Web Token implementation in Python
