from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.models.user import User
from api.services.auth import get_password_hash, verify_password
from database import engine, SessionLocal, Base
import uvicorn

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class UserLogin(BaseModel):
    username: str
    password: str


# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("Таблицы созданы:", Base.metadata.tables.keys())


@app.post("/auth/login", response_model=dict)
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Ищем пользователя в базе данных
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Неверный логин")

    if not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный пароль")

    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Пользователь неактивен")

    return {
        "access_token": "generated_jwt_token_here",  # Замените на реальную генерацию JWT
        "token_type": "bearer",
        "user": {
            "username": db_user.username,
            "role": db_user.role.value,  # Для Enum
            "full_name": db_user.full_name,
            "email": db_user.email
        }
    }


@app.get("/test-users")
def get_test_users(db: Session = Depends(get_db)):
    users = db.query(User).limit(5).all()
    return {"users": [{"username": u.username, "email": u.email} for u in users]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)