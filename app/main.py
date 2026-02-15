from fastapi import FastAPI
from .database import engine
from . import models
from .routes import user, task

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure Task Manager API")

app.include_router(user.router)
app.include_router(task.router)

@app.get("/")
def root():
    return {"message": "Secure Task Manager API is running"}
