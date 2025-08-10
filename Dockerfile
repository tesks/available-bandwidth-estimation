FROM python:3.10-slim

# Install system packages
RUN apt-get update && apt-get install -y\
    tcpdump\
    iproute2 \
    iputils-ping \
    tshark \
    net-tools \
    gcc \
    libpcap-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 

# Copy over the packet probe scripts into the container
COPY . /app/
