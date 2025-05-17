# Base image
FROM python:3.10-bullseye

# ติดตั้ง netcat และ dependencies อื่น ๆ
RUN apt-get update && apt-get install -y netcat gcc libpq-dev \
  && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories for the application
RUN mkdir -p uploads/products/temp

# Expose port
EXPOSE 8000

# Command to run the application
# The application will start after the database is ready (handled by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]