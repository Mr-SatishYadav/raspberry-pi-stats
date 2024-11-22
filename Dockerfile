# Use an official Python image as the base
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /app

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the Flask app with the reloader enabled
CMD ["flask", "run", "--host=0.0.0.0"]