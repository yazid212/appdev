import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Database configuration
DATABASE = os.environ.get('DATABASE', 'todo.db')

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Display all todos."""
    conn = get_db_connection()
    todos = conn.execute('SELECT * FROM todos ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', todos=todos)

@app.route('/', methods=['POST'])
def add_todo():
    """Add a new todo."""
    task = request.form.get('task')
    if task and task.strip():
        conn = get_db_connection()
        conn.execute('INSERT INTO todos (task) VALUES (?)', (task.strip(),))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    """Delete a todo."""
    conn = get_db_connection()
    conn.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/toggle/<int:todo_id>', methods=['POST'])
def toggle_todo(todo_id):
    """Toggle todo completion status."""
    conn = get_db_connection()
    conn.execute('UPDATE todos SET completed = NOT completed WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    # CRITICAL: Bind to 0.0.0.0 to accept external connections
    app.run(host='0.0.0.0', port=5000, debug=True)