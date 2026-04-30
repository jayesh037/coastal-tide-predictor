FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir httpx asyncpg apscheduler pandas python-dotenv
COPY scheduler.py .
CMD ["python", "scheduler.py"]