from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import hash_password
from app.models.user import User


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    username: str,
    password: str,
    *,
    email: str | None = None,
    display_name: str | None = None,
):
    hashed_pw = hash_password(password)
    new_user = User(
        username=username,
        hashed_password=hashed_pw,
        email=email,
        display_name=display_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, user: User, updates: dict) -> User:
    for field, value in updates.items():
        setattr(user, field, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
