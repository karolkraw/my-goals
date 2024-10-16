# Base image
FROM python:3.9-alpine

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    mariadb-dev \
    linux-headers \
    libffi-dev \
    build-base \
    postgresql-dev \
    bash \
    curl \
    librdkafka-dev  # Add librdkafka-dev for confluent-kafka

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Add a non-root user for security
RUN adduser -D myuser
USER myuser

# Command to run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
