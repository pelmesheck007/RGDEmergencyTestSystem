from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models import StudyGroup, StudyGroupMember, User, UserRole
from api.database import get_db
from pydantic import BaseModel
from typing import List
from api.schemas.group import StudyGroupOut, StudyGroupCreate, StudyGroupUpdate

router = APIRouter(prefix="/groups", tags=["Groups"])


class UsernameInput(BaseModel):
    username: str


class RoleInput(BaseModel):
    role: str



@router.get("/", response_model=List[StudyGroupOut])
def get_groups(db: Session = Depends(get_db)):
    return db.query(StudyGroup).all()


@router.post("/", response_model=StudyGroupOut)
def create_group(group_data: StudyGroupCreate, db: Session = Depends(get_db)):
    new_group = StudyGroup(**group_data.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group


@router.put("/{group_id}", response_model=StudyGroupOut)
def update_group(group_id: str, group_data: StudyGroupUpdate, db: Session = Depends(get_db)):
    group = db.query(StudyGroup).filter_by(id=group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    for key, value in group_data.dict(exclude_unset=True).items():
        setattr(group, key, value)

    db.commit()
    db.refresh(group)
    return group


@router.get("/{group_id}/members/")
def get_group_members(group_id: str, db: Session = Depends(get_db)):
    group = db.query(StudyGroup).filter(StudyGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    members = db.query(User).join(StudyGroupMember).filter(StudyGroupMember.group_id == group_id).all()
    return [{"id": m.id, "username": m.username, "full_name": m.full_name, "role": m.role} for m in members]


@router.post("/{group_id}/add_member/")
def add_member(group_id: str, data: UsernameInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    exists = db.query(StudyGroupMember).filter_by(group_id=group_id, user_id=user.id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Участник уже в группе")

    member = StudyGroupMember(user_id=user.id, group_id=group_id)
    db.add(member)
    db.commit()
    return {"detail": "Участник добавлен"}


@router.delete("/{group_id}/members/{user_id}")
def remove_member(group_id: str, user_id: str, db: Session = Depends(get_db)):
    member = db.query(StudyGroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Участник не найден")

    db.delete(member)
    db.commit()
    return {"detail": "Участник удалён"}


@router.post("/{group_id}/members/{user_id}/assign-role/")
def assign_role(group_id: str, user_id: str, data: RoleInput, db: Session = Depends(get_db)):
    if data.role not in UserRole.__members__:
        raise HTTPException(status_code=400, detail="Некорректная роль")

    # Проверяем, состоит ли пользователь в группе
    member = db.query(StudyGroupMember).filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Пользователь не состоит в группе")

    # Меняем глобальную роль пользователя
    user = db.query(User).filter(User.id == user_id).first()
    user.role = data.role
    db.commit()

    return {"detail": f"Глобальная роль пользователя изменена на '{data.role}'"}
