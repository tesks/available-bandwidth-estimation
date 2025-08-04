#!/usr/bin/env python
from pathlib import Path

# A packet sending and logging with Scapy
script_content = '''\
#!/usr/bin/env python
from scapy.all import *
import csv
import time
import random

# CONFIGURATION
DEST_IP = "128.149.123.52"    # mc-integration
DEST_PORT = 12345
IFACE = "eth0"            
PACKET_SIZES = [100, 300, 500, 700, 900, 1100, 1300]  
NUM_PACKETS_PER_SIZE = 20
CSV_FILE = "packet_delay_results.csv"

# Function to build a packet of a given size
def build_packet(size):
    payload = Raw(load=bytes([0x42] * (size - 28)))  # subtract IP+UDP header size (20+8)
    pkt = IP(dst=DEST_IP)/UDP(dport=DEST_PORT)/payload
    return pkt

# Start background sniffing
received_times = {}

def pkt_callback(pkt):
    if UDP in pkt and pkt[UDP].dport == DEST_PORT:
        recv_time = time.time()
        payload_len = len(pkt[Raw].load)
        received_times[payload_len + 28] = recv_time  # 28 bytes for headers

sniffer = AsyncSniffer(iface=IFACE, prn=pkt_callback)
sniffer.start()
time.sleep(2)

# Send packets and log timestamps
with open(CSV_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["packet_size_bytes", "send_timestamp", "receive_timestamp", "delay_seconds"])

    for size in PACKET_SIZES:
        for _ in range(NUM_PACKETS_PER_SIZE):
            pkt = build_packet(size)
            send_time = time.time()
            send(pkt, iface=IFACE, verbose=0)
            time.sleep(0.1)  # small delay between packets

            # Wait for the response
            time.sleep(0.2)
            recv_time = received_times.get(size)
            if recv_time:
                delay = recv_time - send_time
            else:
                delay = None

            writer.writerow([size, send_time, recv_time, delay])
            print(f"Sent packet size {size}B: delay = {delay}")

sniffer.stop()
'''

# Store the script
script_path = Path("main_vps_packet_delay_logger.py")
with open(script_path, "w") as f:
    f.write(script_content)

script_path.as_posix()