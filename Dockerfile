# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents Python from writing .pyc files to disk
ENV PYTHONUNBUFFERED 1  # Ensures that Python output is logged directly

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including MariaDB development libraries
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    musl-dev \
    libc-dev \
    libmariadb-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the Django project code into the container
COPY . /app/

# Expose the port on which the app runs
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
