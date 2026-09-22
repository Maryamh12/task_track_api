from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user


router = APIRouter(
    prefix="/taks",
    tags=["Tasks"]
)

def get_user_task(
        task_id: int,
        current_user: models.User,
        db: Session
) -> models.Task:

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this task"
        )

    return task


@router.get(
    "",
    response_model=list[schemas.TaskResponse]
)

def get_tasks(
        current_user: models.User = Depends(get_current_user)
):

    return current_user.tasks


@router.post(
    "",
    response_model=schemas.TaskResponse,
    status_code=201
)

def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    new_task = models.Task(
        title=task.title,
        description=task.description,
        completed=task.completed,
        owner=current_user
    )

    db.add(new_task)
    db.commit()
    db.refresh()

    return new_task


@router.get(
    "/{task_id",
    response_model=schemas.TaskResponse
)

def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    return  get_user_task(
        task_id,
        current_user,
        db
    )


@router.patch(
    "/{task_id}",
         response_model=schemas.TaskResponse
         )
def update_task(
    task_id: int,
    update_task: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    task = get_user_task(
        task_id,
        current_user,
        db
    )

    update_data = update_task.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    task = get_user_task(
        task_id,
        current_user,
        db
    )

    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted successfully"
    }


