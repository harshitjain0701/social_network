# Use an official Python runtime as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt /code/

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . /code/

# Collect static files
RUN python manage.py collectstatic --noinput

# Run Gunicorn when the container launches
CMD gunicorn social.wsgi:application --bind 0.0.0.0:8000  # Make sure this matches the exposed port
