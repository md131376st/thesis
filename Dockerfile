FROM python:3.12
LABEL authors="davarimona"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
#ENV DJANGO_SETTINGS_MODULE=fileService.settingsDeployment

# Declare arguments
ARG OPENAI_ORGANIZATION
ARG OPENAI_API_KEY
ARG CHROMA_DB_PATH

# Set environment variables using ARG values
ENV OPENAI_ORGANIZATION=${OPENAI_ORGANIZATION}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV CHROMA_DB_PATH=${CHROMA_DB_PATH}


# Set work directory
WORKDIR /code

# Install system dependencies
#RUN apt-get update && apt-get install -y netcat
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Add the current directory to the container
COPY . /code/

# Command to run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]

