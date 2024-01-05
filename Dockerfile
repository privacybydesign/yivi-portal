FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install project dependencies
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --with prod --no-interaction --no-ansi

# Copy the current directory contents into the container at /app
COPY . /app

ENV DJANGO_SETTINGS_MODULE yivi_portal.settings.production

ENV DJANGO_STATIC_ROOT /app/static
ENV DJANGO_MEDIA_ROOT /app/media

RUN mkdir -p $DJANGO_STATIC_ROOT
RUN mkdir -p $DJANGO_MEDIA_ROOT

RUN python manage.py collectstatic --noinput

RUN chown -R nobody:nogroup $DJANGO_MEDIA_ROOT

# Expose port 8000 to the outside world
EXPOSE 8000

ENV DJANGO_STATIC_URL /static/
ENV DJANGO_MEDIA_URL /media/

# Command to run uWSGI
CMD ["sh", "/app/start.sh"]