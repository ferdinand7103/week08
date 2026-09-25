FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

# Upgrade pip, the pip in the base image has known CVEs (Docker Scout)
RUN pip install --no-cache-dir --root-user-action=ignore --upgrade pip

RUN pip install \
    --no-cache-dir \
    --root-user-action=ignore \
    -r requirements.txt

COPY . .

RUN useradd -m appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]