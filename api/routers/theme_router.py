# backend/routers/theme_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List

from api.database import get_db
from api.models import ThemeTask
from api.schemas.theme_task import (ThemeCreate, ThemeOut)

router = APIRouter(prefix="/themes", tags=["Themes"])

@router.get("/", response_model=List[ThemeOut])
def list_unique_themes(db: Session = Depends(get_db)):
    result = db.execute(
        select(
            ThemeTask.id,
            ThemeTask.theme.label("title")  # Return as 'title' for frontend
        ).where(ThemeTask.is_active.is_(True))
        .group_by(ThemeTask.theme, ThemeTask.id)
    ).all()

    themes = []
    for row in result:
        if row.title:  # avoid empty themes
            themes.append({"id": row.id, "title": row.title, "theme": row.title})
    return themes

@router.post("/", response_model=ThemeOut)
def create_theme(data: ThemeCreate, db: Session = Depends(get_db)):
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="Theme title cannot be empty")

    new_theme = ThemeTask(
        title=data.title,
        description=data.description,
        theme=data.title
    )
    db.add(new_theme)
    db.commit()
    db.refresh(new_theme)
    return ThemeOut(id=new_theme.id, title=new_theme.title, theme=new_theme.theme)
