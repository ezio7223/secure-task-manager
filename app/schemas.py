from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class TaskCreate(BaseModel):
    title: str
    description: str


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str

    class Config:
        orm_mode = True
