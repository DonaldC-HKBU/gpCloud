# Use the official Python 3.10 image from the Docker Hub
FROM python:3.10.0-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV TELEGRAM_ACCESS_TOKEN=7852255651:AAGwAPAGhrrh9aLY6yrjwwuyDizTOX5-kU8
ENV REDIS_ACCESS_TOKEN=pDoDppzx5nsSXtSZx1m8ByOvNukyyAO7
ENV GPT_ACCESS_TOKEN=1f63eb2a-dcc4-4da5-86e9-44db01909cd8

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libatlas-base-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your chatbot
CMD ["python", "chatbot.py"]

