# Docker to containerize the cv-index.py, use as 3rd service in the backend service through docker-compose.yml configuration
# Base image with Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy files into container
COPY cv-index.py ./
COPY requirements.txt ./
COPY cv-valid-dev.csv ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
CMD ["python", "cv-index.py"]