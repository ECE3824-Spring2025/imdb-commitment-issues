# Use an official lightweight Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements_docker.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements_docker.txt

# Copy project files
COPY . .

# Expose the port your Flask app runs on
EXPOSE 8000

# Run the Flask app
CMD ["python", "api/index.py"]
