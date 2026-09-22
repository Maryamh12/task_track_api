from fastapi import FastAPI, HTTPException, Depends

from sqlalchemy.orm import Session

import models, schemas
from database import engine, get_db
from seed import seed_database

from security import (hash_password, verify_password, create_access_token,
                      get_current_user)

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

seed_database()

# --------------------------------------------------------------
#  Helper Function
# --------------------------------------------------------------

def get_user_task(
    task_id: int,
    current_user: models.User,
    db: Session
    ) -> models.Task:

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).filter()

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

# --------------------------------------------------------------
#  Home
# --------------------------------------------------------------
@app.get("/")
def home():
    return {"message": "Task Tracker API is running"}


# --------------------------------------------------------------
# Authentication
# --------------------------------------------------------------


@app.post(
    "/auth/register",
    response_model=schemas.UserResponse,
    status_code=201
)
def register_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        print(existing_user)
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        print(existing_user)
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post(
    "/auth/login",
    response_model=schemas.Token
)
def login_user(
        login_data: schemas.UserLogin,
        db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == login_data.email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
            login_data.password,
            user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get(
    "/auth/me",
    response_model=schemas.UserResponse
)
def get_me(
        current_user: models.User = Depends(get_current_user)
):

    return current_user

# --------------------------------------------------------------
#  Tasks
# --------------------------------------------------------------

@app.get(
    "/tasks",
         response_model=list[schemas.TaskResponse]
         )
def get_tasks(
        current_user: models.User = Depends(get_current_user)
):
    return current_user.tasks


@app.get(
    "/tasks/{task_id}",
         response_model=schemas.TaskResponse
         )
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
    ):
    task = get_user_task(
        task_id,
        current_user,
        db
    )

    return task


@app.post(
    "/tasks",
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
    db.refresh(new_task)

    return new_task


@app.patch(
    "/tasks/{task_id}",
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


@app.delete("/tasks/{task_id}")
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

