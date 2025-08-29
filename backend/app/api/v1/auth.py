from datetime import datetime, timedelta
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, verify_api_key
from app.crud import user as crud_user
from app.models.user import User
from app.schemas.auth import Message, VerificationToken

router = APIRouter()


@router.post(
    "/auth/request-verification",
    response_model=Message,
    dependencies=[Depends(verify_api_key)],
)
async def request_verification(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.email_verified:
        return {"detail": "Email already verified"}
    token = secrets.token_urlsafe(16)
    expires = datetime.utcnow() + timedelta(hours=1)
    await crud_user.set_verification_token(db, current_user, token, expires)
    # In a real app, send the token via email
    return {"detail": token}


@router.post("/auth/verify", response_model=Message)
async def verify_email(token_in: VerificationToken, db: AsyncSession = Depends(get_db)):
    user = await crud_user.verify_user_email(db, token_in.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    return {"detail": "Email verified"}
