# Label Studio SSO - 설정 가이드

이 문서는 다양한 환경에서 `label-studio-sso`를 설정하는 방법을 설명합니다.

---

## 📋 설정 옵션

### 필수 설정

| 설정 변수 | 설명 | 예시 |
|----------|------|------|
| `JWT_SSO_SECRET` | JWT 서명 검증용 공유 시크릿 키 | `"your-secret-key-here"` |

### 선택 설정

| 설정 변수 | 기본값 | 설명 | 예시 |
|----------|--------|------|------|
| `JWT_SSO_ALGORITHM` | `HS256` | JWT 서명 알고리즘 | `HS256`, `HS512`, `RS256` |
| `JWT_SSO_TOKEN_PARAM` | `token` | URL에서 토큰을 추출할 파라미터 이름 | `token`, `jwt`, `auth_token` |
| `JWT_SSO_EMAIL_CLAIM` | `email` | JWT에서 이메일을 추출할 claim 이름 | `email`, `user_email`, `mail` |
| `JWT_SSO_USERNAME_CLAIM` | `None` | JWT에서 사용자명을 추출할 claim 이름 (None이면 email 사용) | `username`, `sub`, `user_id` |
| `JWT_SSO_FIRST_NAME_CLAIM` | `first_name` | 이름 claim | `first_name`, `given_name`, `fname` |
| `JWT_SSO_LAST_NAME_CLAIM` | `last_name` | 성 claim | `last_name`, `family_name`, `surname` |
| `JWT_SSO_AUTO_CREATE_USERS` | `False` | 사용자가 없으면 자동 생성 | `True`, `False` |

---

## 🎯 사용 사례별 설정

### 1. Things-Factory 통합

**JWT 토큰 구조**:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1234567890,
  "exp": 1234567900
}
```

**Label Studio 설정**:
```python
# settings.py
JWT_SSO_SECRET = os.getenv('THINGS_FACTORY_JWT_SECRET')
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_AUTO_CREATE_USERS = False  # Things-Factory에서 사용자 동기화 사용
```

---

### 2. Auth0 통합

**JWT 토큰 구조**:
```json
{
  "email": "user@example.com",
  "sub": "auth0|123456",
  "given_name": "John",
  "family_name": "Doe",
  "iat": 1234567890,
  "exp": 1234567900
}
```

**Label Studio 설정**:
```python
# settings.py
JWT_SSO_SECRET = os.getenv('AUTH0_JWT_SECRET')
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_USERNAME_CLAIM = 'sub'
JWT_SSO_FIRST_NAME_CLAIM = 'given_name'
JWT_SSO_LAST_NAME_CLAIM = 'family_name'
JWT_SSO_AUTO_CREATE_USERS = True  # Auth0에서 자동 생성
```

---

### 3. Keycloak 통합

**JWT 토큰 구조**:
```json
{
  "email": "user@example.com",
  "preferred_username": "john.doe",
  "given_name": "John",
  "family_name": "Doe",
  "iat": 1234567890,
  "exp": 1234567900
}
```

**Label Studio 설정**:
```python
# settings.py
JWT_SSO_SECRET = os.getenv('KEYCLOAK_JWT_SECRET')
JWT_SSO_ALGORITHM = 'RS256'  # Keycloak은 보통 RS256 사용
JWT_SSO_EMAIL_CLAIM = 'email'
JWT_SSO_USERNAME_CLAIM = 'preferred_username'
JWT_SSO_FIRST_NAME_CLAIM = 'given_name'
JWT_SSO_LAST_NAME_CLAIM = 'family_name'
JWT_SSO_AUTO_CREATE_USERS = True
```

---

### 4. 커스텀 시스템 통합

**JWT 토큰 구조** (예시):
```json
{
  "user_email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "iat": 1234567890,
  "exp": 1234567900
}
```

**Label Studio 설정**:
```python
# settings.py
JWT_SSO_SECRET = os.getenv('CUSTOM_JWT_SECRET')
JWT_SSO_ALGORITHM = 'HS256'
JWT_SSO_EMAIL_CLAIM = 'user_email'
JWT_SSO_USERNAME_CLAIM = 'username'
JWT_SSO_FIRST_NAME_CLAIM = 'full_name'  # full_name을 first_name에 매핑
JWT_SSO_AUTO_CREATE_USERS = True
```

---

## 🔐 보안 설정

### 1. JWT 시크릿 생성

**권장 방법**:
```python
import secrets
secret = secrets.token_urlsafe(32)
print(f"JWT_SSO_SECRET={secret}")
```

**결과 예시**:
```
JWT_SSO_SECRET=6Xo9d8fK3jN2hT5vL1mP4wQ7rY0eU9aZ3bC6sD8gH2k
```

### 2. HTTPS 필수

JWT 토큰이 URL 파라미터로 전달되므로 **반드시 HTTPS를 사용**해야 합니다.

```nginx
# nginx 설정 예시
server {
    listen 443 ssl;
    server_name label-studio.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
    }
}
```

### 3. 토큰 유효 기간

**권장 설정**: 5-10분

```python
# 외부 시스템에서 토큰 생성 시
from datetime import datetime, timedelta

token = jwt.encode({
    'email': 'user@example.com',
    'iat': datetime.utcnow(),
    'exp': datetime.utcnow() + timedelta(minutes=5)  # 5분 유효
}, secret, algorithm='HS256')
```

### 4. CORS 설정

Label Studio에서 iframe 임베딩을 허용해야 합니다:

```python
# Label Studio settings.py
CORS_ALLOWED_ORIGINS = [
    'https://your-portal.example.com',
]

X_FRAME_OPTIONS = 'SAMEORIGIN'  # 또는 특정 도메인 허용
```

---

## 🧪 테스트 설정

### 로컬 개발 환경

```bash
# .env.local
JWT_SSO_SECRET="test-secret-key-for-development"
JWT_SSO_ALGORITHM="HS256"
JWT_SSO_EMAIL_CLAIM="email"
JWT_SSO_AUTO_CREATE_USERS="true"
```

### 테스트 토큰 생성 스크립트

```python
# generate_test_token.py
import jwt
from datetime import datetime, timedelta

SECRET = "test-secret-key-for-development"

def generate_token(email, first_name="", last_name="", minutes=10):
    payload = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=minutes)
    }
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return token

if __name__ == '__main__':
    token = generate_token('test@example.com', 'John', 'Doe')
    print(f"Test URL: http://localhost:8080?token={token}")
```

---

## 🔧 트러블슈팅

### 문제 1: "JWT_SSO_SECRET is not configured"

**원인**: 환경 변수가 설정되지 않음

**해결**:
```bash
export JWT_SSO_SECRET="your-secret-key"
# 또는 .env 파일에 추가
```

### 문제 2: "JWT token does not contain 'email' claim"

**원인**: JWT 토큰에 email claim이 없거나 이름이 다름

**해결**:
```python
# JWT 토큰 구조 확인
import jwt
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)  # claim 이름 확인

# 설정 조정
JWT_SSO_EMAIL_CLAIM = 'user_email'  # 실제 claim 이름으로 변경
```

### 문제 3: "User not found in Label Studio"

**원인**: 사용자가 Label Studio에 존재하지 않음

**해결 방법 1**: 자동 생성 활성화
```python
JWT_SSO_AUTO_CREATE_USERS = True
```

**해결 방법 2**: 수동으로 사용자 생성
```bash
python manage.py createsuperuser --email user@example.com
```

### 문제 4: "JWT token signature verification failed"

**원인**: JWT 시크릿이 일치하지 않음

**해결**:
1. 외부 시스템과 Label Studio의 `JWT_SSO_SECRET`이 동일한지 확인
2. 알고리즘(`JWT_SSO_ALGORITHM`)이 일치하는지 확인

---

## 📊 모니터링

### 로그 설정

```python
# Label Studio settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/label-studio/sso.log',
        },
    },
    'loggers': {
        'label_studio_sso': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

### 주요 로그 메시지

```
# 성공
INFO: JWT token verified for email: user@example.com
INFO: User found: user@example.com
INFO: User auto-logged in: user@example.com

# 실패
WARNING: JWT token has expired
ERROR: JWT token signature verification failed
WARNING: User not found in Label Studio: user@example.com
```

---

## 📚 참고 자료

- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Django Authentication Backends](https://docs.djangoproject.com/en/stable/topics/auth/customizing/)
- [JWT.io - JWT Debugger](https://jwt.io/)
