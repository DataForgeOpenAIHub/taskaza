from datetime import datetime
from secrets import token_urlsafe
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.apikey import APIKey
from app.models.user import User


async def create_api_key(db: AsyncSession, user: User) -> tuple[str, APIKey]:
    key = token_urlsafe(32)
    hashed = hash_password(key)
    db_key = APIKey(user_id=user.id, hashed_key=hashed, prefix=key[:8])
    db.add(db_key)
    await db.commit()
    await db.refresh(db_key)
    return key, db_key


async def list_api_keys(db: AsyncSession, user: User) -> List[APIKey]:
    result = await db.execute(select(APIKey).where(APIKey.user_id == user.id))
    return result.scalars().all()


async def verify_api_key(db: AsyncSession, user: User, raw_key: str) -> Optional[APIKey]:
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == user.id, APIKey.revoked.is_(False))
    )
    for api_key in result.scalars().all():
        if verify_password(raw_key, api_key.hashed_key):
            api_key.last_used_at = datetime.utcnow()
            await db.commit()
            return api_key
    return None


async def revoke_api_key(db: AsyncSession, user: User, api_key_id: int) -> bool:
    api_key = await db.get(APIKey, api_key_id)
    if not api_key or api_key.user_id != user.id:
        return False
    api_key.revoked = True
    await db.commit()
    return True
