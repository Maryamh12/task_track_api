from pydantic import BaseModel, Field, EmailStr


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=500)
    completed: bool = False



class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: str | None = Field(
        default=None,
        min_length=1,
        max_length=500
    )

    completed: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str