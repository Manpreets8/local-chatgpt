FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY start.sh .
RUN chmod +x start.sh

# Render (and most PaaS hosts) inject $PORT at runtime; 8000 is just the
# local/default fallback for `docker run` without one set.
ENV PORT=8000
EXPOSE 8000

CMD ["./start.sh"]
