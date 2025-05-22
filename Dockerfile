FROM python:3.9-slim

WORKDIR /app

# ensure volume mount point exists
RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tell SQLite where to write by default
ENV DATABASE=/app/data/todo.db

# Expose the port
EXPOSE 5000

# Use gunicorn in production, binding 0.0.0.0
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]