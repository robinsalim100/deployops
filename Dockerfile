# Use an official Python image
FROM python:3.13-slim

# Prevent Python from creating .pyc files
# and make logs appear immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependency file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY run.py .

# Create a directory for the SQLite database
RUN mkdir -p /app/instance

# Application listens on port 5000
EXPOSE 5000

# Start DeployOps
CMD ["python", "run.py"]
