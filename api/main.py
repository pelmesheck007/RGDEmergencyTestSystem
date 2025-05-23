from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.models.user import User
from api.models.task import Task
from api.models.test import Test, TestAnswer
from database import engine, SessionLocal, Base, get_db
import uvicorn
from auth import create_access_token, get_password_hash, verify_password, get_user_id_from_token
from fastapi import Request
from sqlalchemy.exc import OperationalError
from api.schemas.user import *
app = FastAPI()

from api.routers import test
app.include_router(test.router)  # 👈 это должно быть в main.py

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


@app.on_event("startup")
async def startup():
    from .models.user import configure_user_relationships
    configure_user_relationships()

    Base.metadata.create_all(bind=engine)

    # Загружаем тестовые данные
    from .database import SessionLocal
    from .scripts.init_db import create_test_data

    db = SessionLocal()
    try:
        create_test_data(db)
        print("✅ Тестовые данные успешно загружены")
    except Exception as e:
        print(f"❌ Ошибка загрузки тестовых данных: {e}")
    finally:
        db.close()

@app.get("/test-users")
def get_test_users(db: Session = Depends(get_db)):
    users = db.query(User).limit(5).all()
    return {"users": [{"username": u.username} for u in users]}



@app.post("/auth/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(
        username=user.username,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.id})

    return {
        "access_token": access_token,
        "user": UserOut.from_orm(db_user)
    }

@app.get("/users/me", response_model=UserOut)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/me", response_model=UserOut)
def update_me(data: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    if data.full_name:
        user.full_name = data.full_name
    if data.password:
        user.hashed_password = get_password_hash(data.password)
    db.commit()
    db.refresh(user)
    return user

from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    username: Optional[str]
    full_name: Optional[str]
    email: Optional[str]
    password: Optional[str]

@app.patch("/users/me", response_model=UserOut)
def patch_me(data: UserUpdate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.email is not None:
        user.email = data.email
    if data.username is not None:
        user.username = data.username
    if data.password is not None:
        user.hashed_password = get_password_hash(data.password)

    db.commit()
    db.refresh(user)
    return user



@app.delete("/users/me")
def delete_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@app.delete("/admin/users/{user_id}")
def delete_user_as_admin(user_id: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    admin_id = get_user_id_from_token(token)
    admin = db.query(User).get(admin_id)
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted by admin"}

@app.patch("/users/me", response_model=UserOut)
def patch_update_me(
    data: UserUpdate = Body(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "password":
            setattr(user, "hashed_password", get_password_hash(value))
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
