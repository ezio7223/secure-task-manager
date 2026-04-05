# Project Documentation: Secure Task Manager API

## Overview
The **Secure Task Manager API** is a lightweight web application built with Python and FastAPI. It provides functionalities for user authentication (registration and login) and task management. It offers both a RESTful API and a basic server-side rendered UI using Jinja2 templates. 

## Technology Stack
- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: SQLite (`test.db`)
- **Authentication**: JWT (JSON Web Tokens) using `python-jose` and `passlib` for password hashing (bcrypt).
- **Template Engine**: Jinja2 (for HTML UI)
- **Containerization**: Docker

## Directory Structure
```
Task-App/
├── Dockerfile              # Docker container configuration
├── requirements.txt        # Python library dependencies
├── test.db                 # SQLite database file
└── app/                    # Main application directory
    ├── main.py             # App entry point, FastAPI initialization, and UI routes
    ├── database.py         # SQLAlchemy engine and session setup
    ├── models.py           # Database models (User, Task)
    ├── schemas.py          # Pydantic schemas for data validation
    ├── auth.py             # JWT token creation and password hashing logic
    ├── routes/             # API Router endpoints
    │   ├── user.py         # /register and /login API endpoints
    │   └── task.py         # /tasks API endpoints (Create and Get tasks)
    └── templates/          # HTML templates (e.g., index.html)
```

## Features
1. **User Authentication API:**
   - `POST /register`: Registers a new user.
   - `POST /login`: Authenticates a user and returns a JWT access token.
2. **Task Management API:**
   - `POST /tasks`: Creates a task.
   - `GET /tasks`: Retrieves all tasks.
3. **Web User Interface (UI):**
   - `GET /`: Renders the index HTML page showing a list of tasks.
   - `POST /ui/add-task`: Form submission to add a new task.
   - `GET /ui/delete-task/{task_id}`: Deletes a specific task.

---

## Areas for Improvement & Suggestions

Based on a preliminary code analysis, here are recommendations for improving the application's security, architecture, and maintainability:

### 1. Security & Authentication Flaws
- **Hardcoded Secret Key:** In `app/auth.py`, the `SECRET_KEY` is hardcoded (`SECRET_KEY = "supersecretkey"`). This should be loaded securely from an environment variable (e.g., using a `.env` file and `python-dotenv` or `pydantic-settings`).
- **Unprotected Task Routes:** The API endpoints in `app/routes/task.py` (`POST /tasks` and `GET /tasks`) and UI routes in `main.py` do not enforce authentication. Anyone can view or add tasks. You must implement a `get_current_user` dependency to verify the JWT token and protect these routes.
- **Task Ownership Enforcement:** The `Task` model has an `owner_id` relationship to a `User`, but tasks are currently created without attaching them to the user creating them. Modifying the `create_task` logic so that the `owner_id` maps to the currently logged-in user is essential.

### 2. Best Practices & Architecture
- **Environment Variables:** Abstract configurations such as the database URL (`DATABASE_URL = "sqlite:///./test.db"`) into environment variables. This avoids hardcoding paths and makes moving from SQLite to PostgreSQL/MySQL in production easy.
- **Separation of Concerns:** `main.py` currently handles both the FastApi setup and the UI routes (`/ui/...`). Consider moving the UI-specific routes into their own router file (e.g., `app/routes/ui.py`) to keep `main.py` clean.
- **Error Handling:** In `main.py` (`/ui/delete-task/{task_id}`), if an invalid `task_id` is passed, the app ignores it. Consider implementing proper error messages (e.g., HTTP 404 Not Found) or flashing an error message to the user UI.
- **CORS Middleware:** If you plan on building a separate frontend application (e.g., React, Vue) to consume this API, you will need to add CORS (Cross-Origin Resource Sharing) middleware in `main.py`.

### 3. Docker Improvements
- A `.dockerignore` file exists, but ensure it ignores `test.db` and `venv/` so local files don't override the container's environment. Ensure `__pycache__` isn't copied.

### Recommended Next Steps for Implementation
If you would like to proceed with implementing these suggestions, I recommend starting with securing the API by adding the missing JWT authentication middleware to the task routes and loading the database/JWT variables securely from an `.env` file.
