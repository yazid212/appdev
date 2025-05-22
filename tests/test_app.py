import sys
import os
import pytest
import tempfile

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app, init_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file for the test database
    db_fd, flask_app.config['DATABASE'] = tempfile.mkstemp()
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    with flask_app.app_context():
        init_db()
    
    yield flask_app
    
    # Clean up
    os.close(db_fd)
    os.unlink(flask_app.config['DATABASE'])

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_index_page(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Todo List' in response.data

def test_add_todo(client):
    """Test adding a new todo item."""
    response = client.post('/', data={'task': 'Test Task'})
    assert response.status_code == 302  # Redirect after POST
    
    # Check if the task appears on the page
    response = client.get('/')
    assert b'Test Task' in response.data

def test_add_empty_todo(client):
    """Test adding an empty todo item."""
    response = client.post('/', data={'task': ''})
    # Should redirect back or show error
    assert response.status_code in [200, 302]

def test_delete_todo(client):
    """Test deleting a todo item."""
    # First add a todo
    client.post('/', data={'task': 'Task to Delete'})
    
    # Then delete it (assuming delete endpoint exists)
    response = client.post('/delete/1')
    assert response.status_code in [200, 302]

def test_database_connection(app):
    """Test that database connection works."""
    with app.app_context():
        # This should not raise an exception
        init_db()