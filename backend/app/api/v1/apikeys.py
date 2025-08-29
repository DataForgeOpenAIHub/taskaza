from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.crud import apikey as crud_apikey
from app.models.user import User
from app.schemas.apikey import APIKeyCreated, APIKeyOut

router = APIRouter(prefix="/apikeys", tags=["API Keys"])


@router.post("", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    key, db_key = await crud_apikey.create_api_key(db, current_user)
    return APIKeyCreated(id=db_key.id, prefix=db_key.prefix, created_at=db_key.created_at, revoked=db_key.revoked, key=key)


@router.get("", response_model=List[APIKeyOut])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    keys = await crud_apikey.list_api_keys(db, current_user)
    return keys


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    api_key_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    success = await crud_apikey.revoke_api_key(db, current_user, api_key_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    return None
