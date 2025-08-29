from typing import Iterable

from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.task import Task, TaskStatus


async def create_task(db: AsyncSession, user_id: int, task_data: dict) -> Task:
    task = Task(**task_data, user_id=user_id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_tasks_for_user(
    db: AsyncSession,
    user_id: int,
    *,
    status: TaskStatus | None = None,
    q: str | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "desc",
):
    stmt = select(Task).where(Task.user_id == user_id)
    if status:
        stmt = stmt.where(Task.status == status)
    if q:
        stmt = stmt.where(Task.title.ilike(f"%{q}%"))

    order = desc(Task.created_at) if sort.lower() == "desc" else asc(Task.created_at)
    stmt = stmt.order_by(order).offset((page - 1) * limit).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_task_by_id(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(select(Task).where(Task.id == task_id, Task.user_id == user_id))
    return result.scalar_one_or_none()


async def update_task(db: AsyncSession, task: Task, updated_data: dict):
    for key, value in updated_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


async def update_task_status(db: AsyncSession, task: Task, new_status: str):
    task.status = new_status
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: Task):
    await db.delete(task)
    await db.commit()


async def create_tasks_bulk(db: AsyncSession, user_id: int, tasks_data: Iterable[dict]):
    tasks = [Task(**data, user_id=user_id) for data in tasks_data]
    db.add_all(tasks)
    await db.commit()
    for task in tasks:
        await db.refresh(task)
    return tasks


async def update_tasks_status_bulk(
    db: AsyncSession, user_id: int, updates: Iterable[tuple[int, TaskStatus]]
):
    tasks: list[Task] = []
    for task_id, status in updates:
        result = await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        task = result.scalar_one_or_none()
        if task:
            task.status = status
            tasks.append(task)

    await db.commit()
    for task in tasks:
        await db.refresh(task)
    return tasks
