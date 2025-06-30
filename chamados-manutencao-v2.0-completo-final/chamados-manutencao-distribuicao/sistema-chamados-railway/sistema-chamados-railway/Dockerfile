FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD sh -c "gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 src.main:app"

