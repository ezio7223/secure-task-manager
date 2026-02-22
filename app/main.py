from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models
from .routes import user, task

app = FastAPI(title="Secure Task Manager API")
templates = Jinja2Templates(directory="app/templates")

# ... (keep your existing router includes) ...

@app.get("/", response_class=HTMLResponse)
def root(request: Request, db: Session = Depends(get_db)):
    # This fetches the tasks for the table
    tasks = db.query(models.Task).all()
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

@app.post("/ui/add-task")
def add_task_ui(title: str = Form(...), db: Session = Depends(get_db)):
    # Create new task in the database
    new_task = models.Task(title=title)
    db.add(new_task)
    db.commit()
    # Refresh the page to show the new task in the table
    return RedirectResponse(url="/", status_code=303)

@app.get("/ui/delete-task/{task_id}")
def delete_task_ui(task_id: int, db: Session = Depends(get_db)):
    task_to_delete = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task_to_delete:
        db.delete(task_to_delete)
        db.commit()
    # Redirect back to the home page to show the updated list
    return RedirectResponse(url="/", status_code=303)