"""
Generic JWT Auto-Login Middleware

Automatically logs in users when they access Label Studio with a valid JWT token.
"""

import logging
import time
from django.contrib.auth import login
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .backends import JWTAuthenticationBackend

logger = logging.getLogger(__name__)


class JWTAutoLoginMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log in users via JWT token.

    When a request contains a valid JWT token in the URL parameter,
    this middleware authenticates the user and establishes a session.

    Configuration (in Django settings.py):
        JWT_SSO_TOKEN_PARAM: URL parameter name for token (default: 'token')
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.backend = JWTAuthenticationBackend()

    def process_request(self, request):
        # Skip if user is already authenticated
        if request.user.is_authenticated:
            logger.debug(f"User already authenticated: {request.user.email}")
            print(f"[JWT Middleware] User already authenticated: {request.user.email}")
            return

        # Check for JWT token in URL parameters
        token_param = getattr(settings, 'JWT_SSO_TOKEN_PARAM', 'token')
        token = request.GET.get(token_param)

        print(f"[JWT Middleware] Checking for token param '{token_param}' in URL")
        print(f"[JWT Middleware] Token found: {token[:20] if token else 'None'}...")

        if not token:
            # No token, proceed normally
            return

        logger.info("JWT token detected in URL, attempting auto-login")
        print(f"[JWT Middleware] JWT token detected, attempting auto-login")

        # Attempt to authenticate with JWT token
        user = self.backend.authenticate(request, token=token)

        print(f"[JWT Middleware] Authentication result: {user}")

        if user:
            # Log in the user
            login(
                request,
                user,
                backend='label_studio_sso.backends.JWTAuthenticationBackend'
            )
            # Mark this session as JWT auto-login to skip session timeout check
            request.session['jwt_auto_login'] = True
            request.session['last_login'] = time.time()  # Update last_login immediately
            logger.info(f"User auto-logged in: {user.email}")
            print(f"[JWT Middleware] User auto-logged in: {user.email}")
        else:
            logger.warning("JWT token authentication failed")
            print(f"[JWT Middleware] JWT token authentication FAILED")
