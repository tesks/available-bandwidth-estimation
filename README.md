# available-bandwidth-estimation

# Running the Experiment

# Prerequisites
- Install and run docker server

```


git clone https://github.com/tesks/available-bandwidth-estimation.git
cd available-bandwidth-estimation

# Build the docker image
docker build -t abe:vps .

# One-time network
docker network create vpsnet
docker network ls  # Verify it's running

# Make sure the shared folder exists (and is writable on host)
mkdir -p local_mnt/data

# Start the receiver container
docker run -d --name receiver \
  --network vpsnet \
  --cap-add=NET_ADMIN \
  -v "$PWD/local_mnt:/app/local_mnt" \
  abe:vps \
  python -u main_vps_packet_delay_logger.py \
    --role receiver \
    --bind 0.0.0.0 \
    --port 6000 \
    --outfile /app/local_mnt/data/receiver_log.jsonl

# Start the sender container (the experiment)
docker run -it --name sender \
  --network vpsnet \
  --cap-add=NET_ADMIN \
  -v "$PWD/local_mnt:/app/local_mnt" \
  abe:vps \
  python -u main_data_collection.py \
    --role sender \
    --dest receiver \
    --port 6000 \
    --sizes 100,1100 \
    --pairs 100 \
    --inter_packet_ms 40 \
    --outfile /app/local_mnt/data/sender_log.jsonl

# Watch logs while it runs
docker logs -f receiver
docker logs -f sender

# ---- Clean-up -----
docker rm -f sender receiver
docker network rm vpsnet  # only if you want to terminate the network
```

# Quickstart with VSCode and Docker (This section of the README is In Progress and may not be accurate)
1. Install VSCode to your localhost: https://code.visualstudio.com/download
2. Install Docker to your localhost: https://www.docker.com/get-started/
3. Clone this repository to your localhost: `git clone https://github.com/tesks/available-bandwidth-estimation.git`