# Use an official Python runtime as a base image
FROM python:3.12.6-slim

# Set environment variables to prevent Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project into the container
COPY . /app/

# Copy the .env file into the container (make sure .env is in your .dockerignore)
COPY .env /app/.env

# Collect static files for production
RUN python manage.py collectstatic --noinput

# Expose the port on which Django will run (default 8000)
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
