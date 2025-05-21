import os
import pytest
import sqlite3
from app import app as flask_app


@pytest.fixture
def app():
    # Set up a test database
    test_db = 'test_todo.db'
    flask_app.config['DATABASE'] = test_db
    flask_app.config['TESTING'] = True

    # Initialize test database
    with flask_app.app_context():
        conn = sqlite3.connect(test_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS tasks 
                     (id INTEGER PRIMARY KEY, title TEXT, description TEXT)""")
        conn.commit()
        conn.close()

    yield flask_app

    # Teardown - remove the test database
    if os.path.exists(test_db):
        os.remove(test_db)


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_route(client):
    """Test that the index route returns 200 OK"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'index.html' in response.data  # Assuming your index template has this


def test_add_task_get(client):
    """Test that the add task page loads correctly"""
    response = client.get('/add')
    assert response.status_code == 200
    assert b'add_task.html' in response.data


def test_add_task_post(client):
    """Test that a task can be added via POST"""
    test_data = {
        'title': 'Test Task',
        'description': 'This is a test description'
    }
    response = client.post('/add', data=test_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'view_tasks.html' in response.data

    # Verify the task was added to the database
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE title = ?", ('Test Task',))
    task = c.fetchone()
    conn.close()

    assert task is not None
    assert task[1] == 'Test Task'
    assert task[2] == 'This is a test description'


def test_view_tasks_empty(client):
    """Test viewing tasks when none exist"""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert b'No tasks found' in response.data or b'view_tasks.html' in response.data


def test_view_tasks_with_data(client):
    """Test viewing tasks after adding some"""
    # Add test data directly to database
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, description) VALUES (?, ?)",
              ('Task 1', 'Description 1'))
    c.execute("INSERT INTO tasks (title, description) VALUES (?, ?)",
              ('Task 2', 'Description 2'))
    conn.commit()
    conn.close()

    # Check if tasks appear in the view
    response = client.get('/tasks')
    assert response.status_code == 200
    assert b'Task 1' in response.data
    assert b'Description 1' in response.data
    assert b'Task 2' in response.data
    assert b'Description 2' in response.data


def test_database_initialization():
    """Test that the database initializes correctly"""
    test_db = 'test_init.db'
    flask_app.config['DATABASE'] = test_db

    # Call the init_db function
    with flask_app.app_context():
        from app import init_db
        init_db()

    # Verify the table exists
    conn = sqlite3.connect(test_db)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    table_exists = c.fetchone()
    conn.close()

    # Clean up
    if os.path.exists(test_db):
        os.remove(test_db)

    assert table_exists is not None
    assert table_exists[0] == 'tasks'