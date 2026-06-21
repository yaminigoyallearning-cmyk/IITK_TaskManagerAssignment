# Task Manager API

REST API for Task Management with User Authentication

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

Server runs on `http://localhost:5000`

## API Endpoints

### Authentication

**Register**
```
POST /api/auth/register
{
  "username": "john",
  "password": "password123"
}
```

**Login**
```
POST /api/auth/login
{
  "username": "john",
  "password": "password123"
}
```
Returns: `{"token": "john", "username": "john"}`

### Tasks

All task endpoints require `Authorization: Bearer <token>` header

**Get Tasks**
```
GET /api/tasks
```

**Get Single Task**
```
GET /api/tasks/<task_id>
```

**Create Task**
```
POST /api/tasks
{
  "description": "Buy groceries"
}
```

**Update Task**
```
PUT /api/tasks/<task_id>
{
  "status": "Completed"
}
```

**Delete Task**
```
DELETE /api/tasks/<task_id>
```

## Testing

Use curl or Postman to test endpoints:

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"pass123"}'

# Create task (use token from login)
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer john" \
  -H "Content-Type: application/json" \
  -d '{"description":"Buy groceries"}'

# Get tasks
curl -X GET http://localhost:5000/api/tasks \
  -H "Authorization: Bearer john"

# Get single task (replace 1 with actual task_id)
curl -X GET http://localhost:5000/api/tasks/1 \
  -H "Authorization: Bearer john"
```

## Web Frontend

A simple HTML/JavaScript frontend is included in the `frontend/` folder.

### How to Use

1. Open the HTML file in your browser:
   - Open `frontend/index.html` directly in your browser, or
   - Use a local web server: `python -m http.server 8000` (then visit `http://localhost:8000/frontend/`)

2. The frontend includes:
   - User registration and login
   - Create new tasks
   - View all tasks
   - View single task details
   - Mark tasks as completed
   - Delete tasks

3. The frontend uses a separate `TaskManagerAPI` JavaScript class (`frontend/api-client.js`) to handle all API communications.

## Python API Client

A Python API client class is also available (`api_client.py`) for programmatic access to the API.

### Usage Example

```python
from api_client import TaskManagerAPIClient

# Create client
client = TaskManagerAPIClient('http://localhost:5000')

# Register and login
client.register('john', 'password123')
client.login('john', 'password123')

# Create task
task = client.create_task('Buy groceries')

# Get all tasks
tasks = client.get_tasks()

# Get single task
task = client.get_task(task_id='1')

# Update task
client.update_task('1', 'Completed')

# Delete task
client.delete_task('1')
```

### Run the Client Example

```bash
python api_client.py
```

This will run example operations against the API.

