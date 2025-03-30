# Start from the official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django application code
COPY . /app/

# Expose the port that the app will run on
EXPOSE 8080

# Command to run the app (e.g., using Gunicorn)
CMD ["gunicorn", "ugc_platform.wsgi:application", "--bind", "0.0.0.0:8080"]
