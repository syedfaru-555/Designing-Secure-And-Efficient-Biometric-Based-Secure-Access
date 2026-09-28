FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir django numpy pandas opencv-python-headless pymysql Pillow

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
