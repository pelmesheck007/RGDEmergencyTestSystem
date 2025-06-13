from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from api.models.user import User
from api.models.test import Task, VariableAnswer
from api.schemas.test import TaskCreate
from database import engine, Base
import uvicorn
from auth import get_user_id_from_token
from database import get_db

app = FastAPI()

from routers import user,test, theme_router, task_router, answers, scenario_test_router, groups, auth
app.include_router(user.router)
app.include_router(test.router)
app.include_router(theme_router.router)
app.include_router(task_router.router)
app.include_router(answers.router)
app.include_router(scenario_test_router.router)
app.include_router(groups.router)
app.include_router(auth.router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



@app.on_event("startup")
async def startup():

    Base.metadata.create_all(bind=engine)

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
