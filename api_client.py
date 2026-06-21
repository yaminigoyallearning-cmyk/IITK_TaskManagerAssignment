import requests
import json


class TaskManagerAPIClient:
    """Python client for Task Manager API"""
    
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.token = None
        self.username = None
    
    def _request(self, method, endpoint, data=None):
        """Helper method to make API requests"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Error: {str(e)}")
    
    # Authentication Methods
    def register(self, username, password):
        """Register a new user"""
        return self._request('POST', '/api/auth/register', {
            'username': username,
            'password': password
        })
    
    def login(self, username, password):
        """Login and store token"""
        response = self._request('POST', '/api/auth/login', {
            'username': username,
            'password': password
        })
        
        if 'token' in response:
            self.token = response['token']
            self.username = username
        
        return response
    
    def logout(self):
        """Logout and clear token"""
        self.token = None
        self.username = None
    
    # Task Methods
    def get_tasks(self):
        """Get all tasks for authenticated user"""
        return self._request('GET', '/api/tasks')
    
    def get_task(self, task_id):
        """Get a single task by ID"""
        return self._request('GET', f'/api/tasks/{task_id}')
    
    def create_task(self, description):
        """Create a new task"""
        return self._request('POST', '/api/tasks', {
            'description': description
        })
    
    def update_task(self, task_id, status):
        """Update task status"""
        return self._request('PUT', f'/api/tasks/{task_id}', {
            'status': status
        })
    
    def delete_task(self, task_id):
        """Delete a task"""
        return self._request('DELETE', f'/api/tasks/{task_id}')
    
    # Health Check
    def health_check(self):
        """Check API health"""
        return self._request('GET', '/api/health')


if __name__ == '__main__':
    # Example usage
    client = TaskManagerAPIClient()
    
    # Check API health
    print("Checking API health...")
    print(client.health_check())
    
    # Register
    print("\nRegistering user...")
    print(client.register('testuser', 'password123'))
    
    # Login
    print("\nLogging in...")
    print(client.login('testuser', 'password123'))
    
    # Create task
    print("\nCreating task...")
    print(client.create_task('Buy groceries'))
    
    # Get tasks
    print("\nGetting all tasks...")
    tasks = client.get_tasks()
    print(tasks)
    
    if tasks['tasks']:
        task_id = tasks['tasks'][0]['id']
        
        # Get single task
        print(f"\nGetting task {task_id}...")
        print(client.get_task(task_id))
        
        # Update task
        print("\nUpdating task...")
        print(client.update_task(task_id, 'Completed'))
        
        # Delete task
        print("\nDeleting task...")
        print(client.delete_task(task_id))
