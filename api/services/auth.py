from datetime import datetime, timedelta
from hashlib import sha256
import jwt
from fastapi import HTTPException, status

# Конфигурация
SECRET_KEY = "your-secret-key"  # Замените на надежный ключ в продакшене!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_password_hash(password: str) -> str:
    """Хеширование пароля (временно через SHA-256, лучше заменить на bcrypt)."""
    return sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля (временное решение)."""
    return sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание JWT-токена."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> str:
    """Проверка JWT-токена."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token credentials",
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )