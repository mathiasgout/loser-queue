FROM python:3.9.13-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

WORKDIR /loser-queue
COPY . /loser-queue

# Install & use pipenv
RUN python -m pip install --upgrade pip 
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile

CMD ["python", "main.py"]