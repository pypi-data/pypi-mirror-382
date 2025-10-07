# Installation Guide

This guide covers how to install `label-studio-sso` in your Label Studio environment.

## Prerequisites

Before installing, ensure you have:

- **Python 3.8 or higher**
- **Django 3.2 or higher** (Label Studio requirement)
- **Label Studio** installed and running
- **Admin access** to Label Studio's Django settings

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install label-studio-sso
```

### Method 2: Install from GitHub

**Latest version:**

```bash
pip install git+https://github.com/aidoop/label-studio-sso.git
```

**Specific version:**

```bash
pip install git+https://github.com/aidoop/label-studio-sso.git@v1.0.0
```

### Method 3: Install from Source

```bash
# Clone the repository
git clone https://github.com/aidoop/label-studio-sso.git
cd label-studio-sso

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Method 4: Install from Wheel File

```bash
# Download the wheel file
wget https://github.com/aidoop/label-studio-sso/releases/download/v1.0.0/label_studio_sso-1.0.0-py3-none-any.whl

# Install
pip install label_studio_sso-1.0.0-py3-none-any.whl
```

## Verify Installation

After installation, verify the package is installed correctly:

```bash
# Check if package is installed
pip list | grep label-studio-sso

# Verify version
python -c "import label_studio_sso; print(label_studio_sso.__version__)"

# Expected output: 1.0.0
```

## Label Studio Integration

### Step 1: Locate Label Studio Settings

Find your Label Studio installation:

```bash
# Find Label Studio installation
pip show label-studio

# Common locations:
# - /path/to/label-studio/label_studio/core/settings/base.py
# - /usr/local/lib/python3.9/site-packages/label_studio/core/settings/base.py
```

### Step 2: Add to INSTALLED_APPS

Edit `label_studio/core/settings/base.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # ... other Label Studio apps ...

    'label_studio_sso',  # ← Add this
]
```

### Step 3: Add Authentication Backend

In the same `base.py` file:

```python
AUTHENTICATION_BACKENDS = [
    'label_studio_sso.backends.JWTAuthenticationBackend',  # ← Add this (first)
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

**Important**: Place `JWTAuthenticationBackend` **first** in the list for priority.

### Step 4: Add Middleware

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'core.middleware.DisableCSRF',
    'django.middleware.csrf.CsrfViewMiddleware',
    'core.middleware.XApiKeySupportMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'label_studio_sso.middleware.JWTAutoLoginMiddleware',  # ← Add this (after AuthenticationMiddleware)
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ... other middleware ...
]
```

**Important**: Place `JWTAutoLoginMiddleware` **after** `AuthenticationMiddleware`.

### Step 5: Configure JWT Settings

Add JWT configuration to `base.py`:

```python
import os

# JWT SSO Configuration
JWT_SSO_SECRET = os.getenv('JWT_SSO_SECRET')  # Required
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_TOKEN_PARAM = 'token'
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_AUTO_CREATE_USERS = False  # Set to True to auto-create users
```

### Step 6: Set Environment Variables

Create or edit `.env` file:

```bash
# Label Studio .env file
JWT_SSO_SECRET=your-shared-secret-key-here
```

**Important**: This secret must be **identical** to the one used by your external system.

### Step 7: Restart Label Studio

```bash
# If using systemd
sudo systemctl restart label-studio

# If running manually
python label_studio/manage.py runserver 0.0.0.0:8080
```

## Troubleshooting Installation

### Issue 1: Import Error

```
ImportError: No module named 'label_studio_sso'
```

**Solution:**

```bash
# Verify installation
pip list | grep label-studio-sso

# Reinstall
pip install --force-reinstall label-studio-sso
```

### Issue 2: Django Settings Error

```
django.core.exceptions.ImproperlyConfigured: INSTALLED_APPS
```

**Solution:** Check that `'label_studio_sso'` is properly quoted in `INSTALLED_APPS`.

### Issue 3: Permission Error

```
PermissionError: [Errno 13] Permission denied
```

**Solution:**

```bash
# Use sudo (if needed)
sudo pip install label-studio-sso

# Or use user install
pip install --user label-studio-sso
```

### Issue 4: Version Conflict

```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**Solution:**

```bash
# Check Django version
python -c "import django; print(django.VERSION)"

# Upgrade Django if needed
pip install --upgrade Django>=3.2
```

## Uninstallation

To remove `label-studio-sso`:

```bash
# Uninstall package
pip uninstall label-studio-sso

# Remove from Label Studio settings
# 1. Remove 'label_studio_sso' from INSTALLED_APPS
# 2. Remove JWTAuthenticationBackend from AUTHENTICATION_BACKENDS
# 3. Remove JWTAutoLoginMiddleware from MIDDLEWARE
# 4. Restart Label Studio
```

## Next Steps

- **[Quick Start Guide](quick-start.md)** - Get started with basic configuration
- **[Configuration Guide](configuration.md)** - Detailed configuration options
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Support

If you encounter issues during installation:

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Search [GitHub Issues](https://github.com/aidoop/label-studio-sso/issues)
3. Create a new issue with:
   - Python version (`python --version`)
   - Django version (`pip show django`)
   - Label Studio version (`pip show label-studio`)
   - Error logs
