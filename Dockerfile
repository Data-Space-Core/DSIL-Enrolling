# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for Flask and disable buffering to get real-time logs
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=server-api.py
ENV FLASK_ENV=production

# Set environment variables for your app (placeholders; these will be overridden by Docker environment variables)
ENV CLIENT_ID=""
ENV CLIENT_SECRET=""
ENV KEYCLOAK_SERVER_URL=""
ENV REALM = ""
ENV DNS_ZONE_FILE = ""
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY ./src /app

# Set the working directory to /app
WORKDIR /app

# Expose port 5000 to allow traffic to the Flask app
EXPOSE 5000

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]