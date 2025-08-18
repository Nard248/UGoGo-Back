FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 from deadsnakes PPA
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
    python3-pip \
    tzdata \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt /app/

# Bootstrap pip & upgrade build tools
RUN python3.12 -m ensurepip --upgrade \
    && python3.12 -m pip install --upgrade pip setuptools wheel \
    && python3.12 -m pip install --no-cache-dir -r requirements.txt \
    && python3.12 -m pip install daphne channels

# Copy project code
COPY . /app

# Collect static files (optional)
RUN python3.12 manage.py collectstatic --noinput || true

EXPOSE 8000

# Run with Daphne (HTTP + WebSockets)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "ugogo.asgi:application"]
