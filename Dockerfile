FROM python:3.9-slim

WORKDIR /app

# Ensure our data directory exists (so the volume mount has somewhere to go)
RUN mkdir -p /app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]