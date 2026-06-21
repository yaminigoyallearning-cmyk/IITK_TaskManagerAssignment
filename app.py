from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json
import os
from functools import wraps
import hashlib

app = Flask(__name__)
CORS(app)

# Configuration
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
TASKS_FILE = os.path.join(DATA_DIR, 'tasks.json')

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize JSON files if they don't exist
def init_files():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w') as f:
            json.dump({}, f)

init_files()

# Helper functions
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_tasks():
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        try:
            username = token.replace('Bearer ', '')
            users = load_users()
            if username not in users:
                return jsonify({'error': 'Invalid token'}), 401
            request.username = username
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    return decorated

# Routes - Authentication
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username'].strip()
    password = data['password'].strip()
    
    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    
    users = load_users()
    
    if username in users:
        return jsonify({'error': 'Username already exists'}), 409
    
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    save_users(users)
    
    tasks = load_tasks()
    tasks[username] = []
    save_tasks(tasks)
    
    return jsonify({'message': 'User registered successfully', 'username': username}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    username = data['username']
    password = data['password']
    
    users = load_users()
    
    if username not in users:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if users[username]['password'] != hash_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'token': username,
        'username': username
    }), 200

# Routes - Tasks
@app.route('/api/tasks', methods=['GET'])
@verify_token
def get_tasks():
    tasks = load_tasks()
    username = request.username
    
    user_tasks = tasks.get(username, [])
    
    return jsonify({
        'tasks': user_tasks,
        'count': len(user_tasks)
    }), 200

@app.route('/api/tasks/<task_id>', methods=['GET'])
@verify_token
def get_single_task(task_id):
    username = request.username
    tasks = load_tasks()
    user_tasks = tasks.get(username, [])
    
    for task in user_tasks:
        if task['id'] == task_id:
            return jsonify({
                'task': task
            }), 200
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks', methods=['POST'])
@verify_token
def create_task():
    data = request.get_json()
    
    if not data or not data.get('description'):
        return jsonify({'error': 'Task description required'}), 400
    
    username = request.username
    description = data['description'].strip()
    
    tasks = load_tasks()
    
    if username not in tasks:
        tasks[username] = []
    
    task_id = max([int(t['id']) for t in tasks[username]], default=0) + 1
    
    task = {
        'id': str(task_id),
        'description': description,
        'status': 'Pending',
        'created_at': datetime.now().isoformat()
    }
    
    tasks[username].append(task)
    save_tasks(tasks)
    
    return jsonify({
        'message': 'Task created',
        'task': task
    }), 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
@verify_token
def update_task(task_id):
    data = request.get_json()
    
    if not data or not data.get('status'):
        return jsonify({'error': 'Status required'}), 400
    
    username = request.username
    status = data['status']
    
    if status not in ['Pending', 'Completed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    tasks = load_tasks()
    user_tasks = tasks.get(username, [])
    
    for task in user_tasks:
        if task['id'] == task_id:
            task['status'] = status
            task['updated_at'] = datetime.now().isoformat()
            save_tasks(tasks)
            return jsonify({'message': 'Task updated', 'task': task}), 200
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@verify_token
def delete_task(task_id):
    username = request.username
    tasks = load_tasks()
    user_tasks = tasks.get(username, [])
    
    for task in user_tasks:
        if task['id'] == task_id:
            user_tasks.remove(task)
            save_tasks(tasks)
            return jsonify({'message': 'Task deleted'}), 200
    
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
