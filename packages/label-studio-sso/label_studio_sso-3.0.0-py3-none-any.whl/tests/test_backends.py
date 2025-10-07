"""
Tests for JWT Authentication Backend
"""

import pytest
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from label_studio_sso.backends import JWTAuthenticationBackend

User = get_user_model()


@pytest.fixture
def jwt_secret():
    return "test-secret-key"


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def backend():
    return JWTAuthenticationBackend()


@pytest.fixture
def user(db):
    return User.objects.create(
        email="test@example.com",
        username="test@example.com"
    )


@pytest.mark.django_db
class TestJWTAuthenticationBackend:

    def test_authenticate_with_valid_token(self, backend, request_factory, user, jwt_secret):
        """Test authentication with a valid JWT token"""
        # Create valid JWT token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=10)
            },
            jwt_secret,
            algorithm='HS256'
        )

        request = request_factory.get('/')

        with patch('label_studio_sso.backends.settings') as mock_settings:
            mock_settings.JWT_SSO_SECRET = jwt_secret
            mock_settings.JWT_SSO_ALGORITHM = 'HS256'
            mock_settings.JWT_SSO_EMAIL_CLAIM = 'email'
            mock_settings.JWT_SSO_USERNAME_CLAIM = 'username'
            mock_settings.JWT_SSO_AUTO_CREATE_USERS = True
            authenticated_user = backend.authenticate(request, token=token)

        assert authenticated_user is not None
        assert authenticated_user.email == 'test@example.com'

    def test_authenticate_with_expired_token(self, backend, request_factory, user, jwt_secret):
        """Test authentication with an expired JWT token"""
        # Create expired token
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'iat': datetime.utcnow() - timedelta(minutes=20),
                'exp': datetime.utcnow() - timedelta(minutes=10)
            },
            jwt_secret,
            algorithm='HS256'
        )

        request = request_factory.get('/')

        with patch('label_studio_sso.backends.settings') as mock_settings:
            mock_settings.JWT_SSO_SECRET = jwt_secret
            mock_settings.JWT_SSO_ALGORITHM = 'HS256'
            mock_settings.JWT_SSO_EMAIL_CLAIM = 'email'
            mock_settings.JWT_SSO_USERNAME_CLAIM = 'username'
            mock_settings.JWT_SSO_AUTO_CREATE_USERS = True
            authenticated_user = backend.authenticate(request, token=token)

        assert authenticated_user is None

    def test_authenticate_with_invalid_signature(self, backend, request_factory, user, jwt_secret):
        """Test authentication with invalid token signature"""
        # Create token with wrong secret
        token = jwt.encode(
            {
                'email': 'test@example.com',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=10)
            },
            'wrong-secret',
            algorithm='HS256'
        )

        request = request_factory.get('/')

        with patch('label_studio_sso.backends.settings') as mock_settings:
            mock_settings.JWT_SSO_SECRET = jwt_secret
            mock_settings.JWT_SSO_ALGORITHM = 'HS256'
            mock_settings.JWT_SSO_EMAIL_CLAIM = 'email'
            mock_settings.JWT_SSO_USERNAME_CLAIM = 'username'
            mock_settings.JWT_SSO_AUTO_CREATE_USERS = True
            authenticated_user = backend.authenticate(request, token=token)

        assert authenticated_user is None

    def test_authenticate_with_nonexistent_user(self, backend, request_factory, jwt_secret):
        """Test authentication when user doesn't exist in Label Studio"""
        token = jwt.encode(
            {
                'email': 'nonexistent@example.com',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=10)
            },
            jwt_secret,
            algorithm='HS256'
        )

        request = request_factory.get('/')

        with patch('label_studio_sso.backends.settings') as mock_settings:
            mock_settings.JWT_SSO_SECRET = jwt_secret
            mock_settings.JWT_SSO_ALGORITHM = 'HS256'
            mock_settings.JWT_SSO_EMAIL_CLAIM = 'email'
            mock_settings.JWT_SSO_USERNAME_CLAIM = 'username'
            mock_settings.JWT_SSO_AUTO_CREATE_USERS = False  # Don't auto-create
            authenticated_user = backend.authenticate(request, token=token)

        assert authenticated_user is None

    def test_authenticate_without_token(self, backend, request_factory):
        """Test authentication without providing a token"""
        request = request_factory.get('/')
        authenticated_user = backend.authenticate(request)

        assert authenticated_user is None

    def test_authenticate_with_token_missing_email(self, backend, request_factory, jwt_secret):
        """Test authentication with token that doesn't contain email"""
        token = jwt.encode(
            {
                'username': 'testuser',
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(minutes=10)
            },
            jwt_secret,
            algorithm='HS256'
        )

        request = request_factory.get('/')

        with patch('label_studio_sso.backends.settings') as mock_settings:
            mock_settings.JWT_SSO_SECRET = jwt_secret
            mock_settings.JWT_SSO_ALGORITHM = 'HS256'
            mock_settings.JWT_SSO_EMAIL_CLAIM = 'email'
            mock_settings.JWT_SSO_USERNAME_CLAIM = 'username'
            mock_settings.JWT_SSO_AUTO_CREATE_USERS = True
            authenticated_user = backend.authenticate(request, token=token)

        assert authenticated_user is None

    def test_get_user(self, backend, user):
        """Test get_user method"""
        retrieved_user = backend.get_user(user.id)
        assert retrieved_user == user

        # Test with non-existent user ID
        assert backend.get_user(99999) is None
