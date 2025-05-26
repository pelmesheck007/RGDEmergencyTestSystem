from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic.schema import datetime
from sqlalchemy.orm import Session
from typing import List
from api.database import get_db
from api.dependencies import get_current_user
from api.models import TestTask, VariableAnswer, Task
from api.services import theme_task_service
from api.schemas.theme_task import ThemeTaskCreate, ThemeTaskUpdate, ThemeTaskOut, CreateTasksRequest

router = APIRouter(prefix="/theme-tasks", tags=["Theme Tasks"])


@router.post("/", response_model=ThemeTaskOut)
def create_theme_task(data: ThemeTaskCreate, db: Session = Depends(get_db)):
    return theme_task_service.create_theme_task(db, **data.dict())


@router.get("/{task_id}", response_model=ThemeTaskOut)
def get_theme_task(task_id: str, db: Session = Depends(get_db)):
    task = theme_task_service.get_theme_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="ThemeTask not found")
    return task


@router.get("/", response_model=List[ThemeTaskOut])
def list_theme_tasks(
    theme: str = None,
    only_active: bool = True,
    order_by: str = 'order_number',
    db: Session = Depends(get_db)
):
    return theme_task_service.get_theme_tasks(db, theme, only_active, order_by)


@router.put("/{task_id}", response_model=ThemeTaskOut)
def update_theme_task(task_id: str, data: ThemeTaskUpdate, db: Session = Depends(get_db)):
    updated = theme_task_service.update_theme_task(db, task_id, data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="ThemeTask not found")
    return updated


@router.delete("/{task_id}")
def delete_theme_task(task_id: str, db: Session = Depends(get_db)):
    deleted = theme_task_service.delete_theme_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="ThemeTask not found")
    return {"detail": "Deleted successfully"}

