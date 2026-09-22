from database import  SessionLocal
from models import Task , User
from utils import tasks, users
from security import hash_password

def seed_database():
    db = SessionLocal()

    try:

        existing_user = db.query(User).first()

        if existing_user:
            return

        seedusers = []

        for user in users:

            seedusers.append(User(
                username = user["username"],
                email = user["email"],
                hashed_password = hash_password(user["password"])
            )
            )
        db.add_all(seedusers)

        db.commit()

        existing_task = db.query(Task).first()

        if existing_task:
            return

        seedtasks= []
        for task in tasks:

            owner = db.query(User).filter(
                User.username == task["owner"]
            ).first()

            if owner is None:
                raise ValueError(
                    f"No user found with username '{task['owner']}'"
                )

            seedtasks.append(Task(
                    title = task["title"],
                    description = task["description"],
                    completed = task["completed"],
                    owner_id = owner.id
                ))
        db.add_all(seedtasks)
        db.commit()
    finally:
        db.close()