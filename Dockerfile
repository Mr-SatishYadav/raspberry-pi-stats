# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install project dependencies using pip
RUN pip install --no-cache-dir .

# Expose the port the Flask app runs on
EXPOSE 5000

# Command to run the app
CMD ["python", "src/app.py"]
