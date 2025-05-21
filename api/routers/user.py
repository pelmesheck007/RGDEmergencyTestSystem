# app/routers/users.py
from fastapi import APIRouter, Depends
from api.dependencies import get_current_user
from api.models.user import User

router = APIRouter()

@router.get("/me")
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }