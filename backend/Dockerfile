FROM python:3.11-slim

WORKDIR /app

# -------------------------------------------------
# System dependencies (Postgres, compilation)
# -------------------------------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------
# Python dependencies
# -------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------
# Copy project
# -------------------------------------------------
COPY . .

# -------------------------------------------------
# Flask environment
# -------------------------------------------------
ENV FLASK_APP=app:create_app
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# -------------------------------------------------
# Entrypoint
# -------------------------------------------------
CMD ["flask", "run"]
