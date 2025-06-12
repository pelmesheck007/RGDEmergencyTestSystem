# services/theme_task_service.py

from sqlalchemy.orm import Session
from api.models.test import Theme
from uuid import uuid4
from datetime import datetime


def create_theme_task(db: Session, title: str, description: str = None, theme: str = None, order_number: int = 0):
    new_task = Theme(
        id=str(uuid4()),
        title=title,
        description=description,
        created_at=datetime.utcnow()
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task




def update_theme_task(db: Session, task_id: str, data: dict):
    task = db.query(Theme).filter(Theme.id == task_id).first()
    if not task:
        return None
    for key, value in data.items():
        setattr(task, key, value)
    task.updated_at = datetime.utcnow()
    db.commit()
    return task


def delete_theme_task(db: Session, task_id: str):
    task = db.query(Theme).filter(Theme.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
    return task


def get_theme_task(db: Session, task_id: str):
    return db.query(Theme).filter(Theme.id == task_id).first()


def get_theme_tasks(
    db: Session,
    theme: str = None,
    order_by: str = 'order_number'
):
    query = db.query(Theme)

    if theme:
        query = query.filter(Theme.title == theme)

    if order_by == 'created_at':
        query = query.order_by(Theme.created_at)

    return query.all()
