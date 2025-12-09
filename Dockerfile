# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the project code
COPY . /app

# Expose port your Django app will run on
EXPOSE 8088

# Set environment variable for Django
ENV DJANGO_SETTINGS_MODULE=settings.dev

# Collect static files (optional)
# RUN python manage.py collectstatic --noinput

# Run Gunicorn
CMD ["gunicorn", "iScheduler.wsgi:application", "--bind", "0.0.0.0:8088", "--chdir", "/app"]
