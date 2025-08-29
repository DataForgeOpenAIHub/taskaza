from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, verify_api_key
from app.crud import task as crud
from app.models.user import User
from app.schemas.task import (
    TaskBulkRequest,
    TaskBulkResponse,
    TaskCreate,
    TaskOut,
    TaskStatus,
    TaskStatusBulkUpdate,
    TaskStatusUpdate,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_task(db, user_id=user.id, task_data=task_in.model_dump())


@router.get("/", response_model=list[TaskOut], status_code=status.HTTP_200_OK)
async def list_tasks(
    status: TaskStatus | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("desc", pattern="^(asc|desc)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_tasks_for_user(
        db,
        user.id,
        status=status,
        q=q,
        page=page,
        limit=limit,
        sort=sort,
    )


@router.get("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def get_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: int,
    update: TaskUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await crud.update_task(db, task, update.model_dump())


@router.patch("/{task_id}", response_model=TaskOut, status_code=status.HTTP_200_OK)
async def update_task_status(
    task_id: int,
    update: TaskStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return await crud.update_task_status(db, task, update.status)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task_by_id(db, task_id, user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    await crud.delete_task(db, task)


@router.post("/bulk", response_model=TaskBulkResponse, status_code=status.HTTP_200_OK)
async def bulk_tasks(
    payload: TaskBulkRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    created = []
    if payload.create:
        created = await crud.create_tasks_bulk(
            db, user.id, [task.model_dump() for task in payload.create]
        )

    updated = []
    if payload.update_status:
        updates = [(u.id, u.status) for u in payload.update_status]
        updated = await crud.update_tasks_status_bulk(db, user.id, updates)

    return TaskBulkResponse(created=created, updated=updated)
