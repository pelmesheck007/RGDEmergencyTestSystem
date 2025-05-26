from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api.models import ThemeTask
from api.models.user import User, StudyGroup, StudyGroupMember
from api.models.task import Task, VariableAnswer
from api.models.test import Test, TestAnswer
from api.schemas.test import TaskCreate
from api.schemas.theme_task import ThemeTaskOut
from database import engine, SessionLocal, Base, get_db
import uvicorn
from auth import create_access_token, get_password_hash, verify_password, get_user_id_from_token
from fastapi import Request
from sqlalchemy.exc import OperationalError
from api.schemas.user import *
app = FastAPI()
from typing import List
from api.routers import test
app.include_router(test.router)  # 👈 это должно быть в main.py
from routers import theme_router
app.include_router(theme_router.router)
from routers import task_router

app.include_router(task_router.router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

from models import StudyGroup
from schemas.group import StudyGroupOut, StudyGroupCreate, StudyGroupUpdate
from database import get_db  # или как у тебя настроено подключение


@app.get("/groups/", response_model=List[StudyGroupOut])
def get_groups(db: Session = Depends(get_db)):
    return db.query(StudyGroup).all()


@app.post("/groups/", response_model=StudyGroupOut)
def create_group(group_data: StudyGroupCreate, db: Session = Depends(get_db)):
    new_group = StudyGroup(**group_data.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group


@app.put("/groups/{group_id}", response_model=StudyGroupOut)
def update_group(group_id: str, group_data: StudyGroupUpdate, db: Session = Depends(get_db)):
    group = db.query(StudyGroup).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    for key, value in group_data.dict(exclude_unset=True).items():
        setattr(group, key, value)

    db.commit()
    db.refresh(group)
    return group


class UserLogin(BaseModel):
    username: str
    password: str


@app.on_event("startup")
async def startup():

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
from typing import Optional, List


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



@app.post("/tasks/")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        **task.dict(exclude={"variable_answers"})
    )
    new_task.count_variables = len(task.variable_answers)
    db.add(new_task)
    db.flush()

    for answer in task.variable_answers:
        db.add(VariableAnswer(
            task_id=new_task.id,
            string_answer=answer.string_answer,
            truthful=answer.truthful
        ))

    db.commit()
    return {"id": new_task.id}



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
