# Task Management API

A robust, containerized Task Management API built with **FastAPI**, **PostgreSQL**, and **SQLAlchemy**.

## Features

- **User Authentication**: Register/Login with JWT.
- **Project Management**: Create, Read, Update, Delete (Soft) projects.
- **Task Management**: Create, Read, Update, Delete (Soft) tasks.
- **Filtering**: List tasks by project.
- **Permissions**: Users can only manage their own projects and tasks.
- **Background Tasks**: Simulated email notification on task creation.

## Tech Stack

- **FastAPI**: Modern, fast web framework.
- **PostgreSQL**: Robust SQL database (via Docker).
- **SQLAlchemy (Async)**: ORM for database interactions.
- **Pydantic v2**: Data validation.
- **Docker & Docker Compose**: Containerization.
- **Pytest**: Testing.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed.

### Installation & Running

1.  **Clone the repository** (if you haven't already).
2.  **Setup Environment Variables**:
    Copy the example environment file and update it if necessary:
    ```bash
    cp .env.example .env
    ```
3.  **Run with Docker Compose**:

    ```bash
    docker-compose up --build
    ```

    The API will be available at `http://localhost:8000`.

3.  **Access Documentation**:
    - Swagger UI: `http://localhost:8000/docs`

### How to Authenticate in Swagger UI

1.  Click the **Authorize** button (padlock icon) at the top right.
2.  Enter your **username** and **password**.
3.  **Leave `client_id` and `client_secret` EMPTY.** These are optional fields for the OAuth2 specification and are not required for this API.
4.  Click **Authorize**.
5.  Click **Close**.
6.  Now calls to protected endpoints (padlock icon) will automatically use your token.

You can run tests inside the container or locally.

**Inside Container**:
```bash
docker-compose exec app pytest
```

**Locally** (requires python environment):
```bash
bash install_dependencies.sh # optional
pytest
```

## Endpoints Overview

### Auth
- `POST /api/v1/register`: Create a new user.
- `POST /api/v1/login/access-token`: Get JWT token.

### Projects
- `GET /api/v1/projects/`: List all own projects.
- `POST /api/v1/projects/`: Create a project.
- `PUT /api/v1/projects/{id}`: Update a project.
- `DELETE /api/v1/projects/{id}`: Soft delete a project.

### Tasks
- `GET /api/v1/tasks/`: List all own tasks (optional `project_id` filter).
- `POST /api/v1/tasks/`: Create a task.
- `PUT /api/v1/tasks/{id}`: Update a task.
- `DELETE /api/v1/tasks/{id}`: Soft delete a task.
