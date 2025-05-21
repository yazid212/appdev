from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# Configuration
app.config['DATABASE'] = 'todo.db'

def get_db_connection():
    """Get database connection using the configured database path"""
    db_path = app.config.get('DATABASE', 'todo.db')
    return sqlite3.connect(db_path)

def init_db():
    """Initialize the database with the tasks table"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY, title TEXT, description TEXT)""")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (title, description))
        conn.commit()
        conn.close()
        return redirect(url_for('view_tasks'))
    return render_template('add_task.html')

@app.route('/tasks')
def view_tasks():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()
    conn.close()
    return render_template('view_tasks.html', tasks=tasks)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
