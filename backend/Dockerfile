FROM python:3.12-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY pyproject.toml .
COPY app/__init__.py app/__init__.py
RUN pip install --no-cache-dir .

COPY . .

CMD ["bash", "entrypoint.sh"]
