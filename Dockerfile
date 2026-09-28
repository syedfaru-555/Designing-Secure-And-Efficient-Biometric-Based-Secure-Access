FROM python:3.11-slim

WORKDIR /app

# Install required system packages for OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir \
    django \
    numpy \
    pandas \
    opencv-python-headless \
    pymysql \
    Pillow

# Expose Django port
EXPOSE 8000

# Start Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
