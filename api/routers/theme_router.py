from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from api.database import get_db
from api.models import Theme
from api.schemas.theme_task import ThemeCreate, ThemeOut

router = APIRouter(prefix="/themes", tags=["Themes"])


@router.get("/", response_model=List[ThemeOut])
def list_unique_themes(db: Session = Depends(get_db)):
    # Получаем уникальные темы с их id и title
    themes = db.execute(
        select(Theme.id, Theme.title).distinct()
    ).all()

    # Возвращаем список словарей
    return [{"id": row.id, "title": row.title} for row in themes if row.title]


@router.post("/", response_model=ThemeOut)
def create_theme(data: ThemeCreate, db: Session = Depends(get_db)):
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="Theme title cannot be empty")

    new_theme = Theme(
        title=data.title,
        description=data.description
    )
    db.add(new_theme)
    db.commit()
    db.refresh(new_theme)
    return ThemeOut(id=new_theme.id, title=new_theme.title)
