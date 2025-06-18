# app/routers/users.py
import os
import shutil
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, validator
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from api.auth import get_user_id_from_token, get_password_hash
from api.dependencies import get_current_user, get_db
from api.models import TestAnswer
from api.models.scenario_tests import ScenarioResult
from api.schemas import *
from api.models.user import User, StudyGroupMember, StudyGroup
from api.schemas.user import UserUpdate, UserOut, UserCreate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.services import user_service
from api.dependencies import require_admin
router = APIRouter(prefix="/users", tags=["Users"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.post("/", response_model=UserOut)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    return user_service.create_user(db, data)


@router.get("/", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    return user_service.get_all_users(db)


@router.put("/{user_id}", response_model=UserOut)
def admin_update_user(
    user_id: str,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    return user_service.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_admin)
):
    user_service.delete_user(db, user_id)
    return None

@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), _: str = Depends(require_admin)):
    deleted = user_service.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "Deleted successfully"}


@router.patch("/me", response_model=UserUpdate)
async def update_current_user(
        user_data: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """
    Обновление данных текущего пользователя
    """
    try:
        update_data = user_data.dict(exclude_unset=True)

        # Проверка уникальности username
        if 'username' in update_data:
            existing_user = db.query(User).filter(
                User.username == update_data['username'],
                User.id != current_user.id
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Проверка уникальности email
        if 'email' in update_data:
            existing_email = db.query(User).filter(
                User.email == update_data['email'],
                User.id != current_user.id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Обновление полей
        for field, value in update_data.items():
            setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)

        return {
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/me2", response_model=UserOut)
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

@router.get("/me", response_model=UserOut)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/me", response_model=UserOut)
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


@router.delete("/me")
def delete_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

@router.get("/admin/user_stats")
def get_user_stats(db: Session = Depends(get_db)):
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

    roles_count = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    roles_dict = {role.value.lower(): count for role, count in roles_count}

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_30d = db.query(func.count(User.id)).filter(User.registration_date >= thirty_days_ago).scalar()
    last_logins = db.query(User.full_name, User.registration_date) \
        .order_by(User.registration_date.desc()) \
        .limit(5).all()

    return {
         "total_users": total_users,
        "active_users": active_users,
        "roles_count": roles_dict,
        "new_users_30d": new_users_30d,
        "latest_users": [
            {"name": name, "registered": reg_date.strftime("%Y-%m-%d")}
            for name, reg_date in last_logins
        ]
    }



@router.get("/{user_id}/main_info")
def get_user_main_info(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    group = (
        db.query(StudyGroup)
        .join(StudyGroupMember, StudyGroup.id == StudyGroupMember.group_id)
        .filter(StudyGroupMember.user_id == user_id)
        .first()
    )

    test_answers = (
        db.query(TestAnswer)
        .filter(TestAnswer.student_id == user_id)
        .order_by(TestAnswer.end_datetime.desc())
        .limit(5)
        .all()
    )

    scenario_results = (
        db.query(ScenarioResult)
        .filter(ScenarioResult.user_id == user_id)
        .order_by(ScenarioResult.completed_at.desc())
        .limit(5)
        .all()
    )

    return {
        "group": {
            "id": group.id if group else None,
            "name": group.name if group else "Без группы"  # Название поля name, а не title
        },
        "recent_tests": [
        {
            "id": t.test_id,
            "title": t.test.test_name if t.test else "Неизвестный тест",
            "score_percent": (
                round((t.score / max(len(t.test.tasks), 1)) * 100, 1)
                if t.test and t.test.tasks else None
            ),

            "score_str": (
                f"{t.score} / {len(t.test.tasks)}" if t.test and t.test.tasks else None
            ),
            "passed": t.is_passed,
            "datetime": t.end_datetime.isoformat() if t.end_datetime else None
        }
        for t in test_answers
    ],


        "recent_scenarios": [
            {
                "id": s.scenario_id,
                "test_type": "scenario",  # Чтобы фронт понимал, что это сценарий
                "name": s.scenario.title if s.scenario else "Неизвестный сценарий",
                "result": s.result,
                "datetime": s.completed_at.isoformat() if s.completed_at else None
            }
            for s in scenario_results
        ]
    }

@router.get("/me/main_information")
def get_current_user_full_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user_id = get_user_id_from_token(token)
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Учебная группа
    group = (
        db.query(StudyGroup)
        .join(StudyGroupMember, StudyGroup.id == StudyGroupMember.group_id)
        .filter(StudyGroupMember.user_id == user_id)
        .first()
    )

    # Последние 5 обычных тестов
    test_answers = (
        db.query(TestAnswer)
        .filter(TestAnswer.student_id == user_id)
        .order_by(TestAnswer.end_datetime.desc())
        .limit(5)
        .all()
    )

    # Последние 5 сценариев
    scenario_results = (
        db.query(ScenarioResult)
        .filter(ScenarioResult.user_id == user_id)
        .order_by(ScenarioResult.completed_at.desc())
        .limit(5)
        .all()
    )

    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
        "group": {
            "id": group.id if group else None,
            "title": group.title if group else "Без группы"
        },
        "recent_tests": [
            {
                "id": t.test_id,
                "title": t.test.test_name if t.test else "Неизвестный тест",
                "score": t.score,
                "passed": t.is_passed,
                "datetime": t.end_datetime.isoformat() if t.end_datetime else None
            }
            for t in test_answers
        ],
        "recent_scenarios": [
            {
                "id": s.scenario_id,
                "title": s.scenario.title if s.scenario else "Неизвестный сценарий",
                "result": s.result,
                "datetime": s.completed_at.isoformat() if s.completed_at else None
            }
            for s in scenario_results
        ]
    }

@router.get("/{user_id}/main_info")
def get_user_main_info(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Учебная группа
    group = (
        db.query(StudyGroup)
        .join(StudyGroupMember, StudyGroup.id == StudyGroupMember.group_id)
        .filter(StudyGroupMember.user_id == user_id)
        .first()
    )

    # Последние 5 обычных тестов
    test_answers = (
        db.query(TestAnswer)
        .filter(TestAnswer.student_id == user_id)
        .order_by(TestAnswer.end_datetime.desc())
        .limit(5)
        .all()
    )

    # Последние 5 сценариев
    scenario_results = (
        db.query(ScenarioResult)
        .filter(ScenarioResult.user_id == user_id)
        .order_by(ScenarioResult.completed_at.desc())
        .limit(5)
        .all()
    )

    return {
        "group": {
            "id": group.id if group else None,
            "title": group.title if group else "Без группы"
        },
        "recent_tests": [
            {
                "id": t.test_id,
                "type": "test",
                "title": t.test.test_name if t.test else "Неизвестный тест",
                "score": t.score,
                "passed": t.is_passed,
                "datetime": t.end_datetime.isoformat() if t.end_datetime else None
            }
            for t in test_answers
        ],
        "recent_scenarios": [
            {
                "id": s.scenario_id,
                "type": "scenario",
                "title": s.scenario.title if s.scenario else "Неизвестный сценарий",
                "result": s.result,
                "datetime": s.completed_at.isoformat() if s.completed_at else None
            }
            for s in scenario_results
        ]
    }
