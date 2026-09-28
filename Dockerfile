FROM python:3.11-slim

WORKDIR /app

# Install system libraries required by OpenCV
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
    opencv-python-headless==4.10.0.84 \
    pymysql \
    Pillow

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
