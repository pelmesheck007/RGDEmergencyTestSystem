from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.models import StudyGroup, StudyGroupMember, User, UserRole
from api.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/groups", tags=["Groups"])


class UsernameInput(BaseModel):
    username: str


class RoleInput(BaseModel):
    role: str


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
