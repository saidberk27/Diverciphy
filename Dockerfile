# Base Image: Lightweight Python
FROM python:3.9-slim

# Best Practices: Set working directory and env vars
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Dependency Layer (Cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Layer
COPY . .

# Executable permissions for entrypoint
RUN chmod +x entrypoint.sh

# Security: Create non-root user (Clean Code / Best Practice)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose ports (Shredder, Assembler, Worker-Standard)
EXPOSE 5555 5556 5000

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]
