# Use official Python slim image
FROM python:3.11-slim


# Set work directory
WORKDIR /app

# Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Install Python dependencies

COPY requirements.txt .


RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Use Gunicorn to run the app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
