from fastapi import FastAPI

from app import models
from app.database import engine
from app.seed import seed_database
from app.routers import auth, tasks

models.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Task TRacker API"
)

seed_database()


@app.get("/")
def home():
    return {"message": "Task Tracker API is running"}


app.include_router(auth.router)
app.include_router(tasks.router)
