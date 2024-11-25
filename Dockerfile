# Use an official Python image as the base
FROM python:3.10-slim

# Set environment variables to prevent Python from writing .pyc files and using buffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first to leverage Docker's caching
COPY requirements.txt /app/

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container
COPY . /app

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run Flask in development mode with reloader enabled
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload", "--debug"]
