#!/usr/bin/env python
from scapy.all import *
import csv
import time
import random

# CONFIGURATION
DEST_IP = "128.149.123.52"    # mc-integration
DEST_PORT = 12345
IFACE = "en0"            
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

# Check available interfaces first
from scapy.arch import get_if_list
available_interfaces = get_if_list()
print(f"Available interfaces: {available_interfaces}")

# Try to find a working interface
working_interface = None
for iface_name in [IFACE, "lo", "any"] + available_interfaces:
    try:
        print(f"Trying interface: {iface_name}")
        test_sniffer = AsyncSniffer(iface=iface_name, prn=pkt_callback, timeout=1)
        test_sniffer.start()
        time.sleep(0.5)
        if test_sniffer.running:
            working_interface = iface_name
            test_sniffer.stop()
            print(f"Success! Using interface: {working_interface}")
            break
        test_sniffer.stop()
    except Exception as e:
        print(f"Interface {iface_name} failed: {e}")
        continue

if not working_interface:
    print("ERROR: No working network interface found!")
    print("This might be due to:")
    print("1. Container not running with --privileged --net=host")
    print("2. No network interfaces available")
    print("3. Permission issues")
    exit(1)

# Start the actual sniffer with working interface
sniffer = AsyncSniffer(iface=working_interface, prn=pkt_callback)
sniffer_started = False
try:
    sniffer.start()
    sniffer_started = True
    print(f"Sniffer started successfully on interface {working_interface}")
    time.sleep(2)
except Exception as e:
    print(f"Failed to start sniffer: {e}")
    sniffer_started = False

# Send packets and log timestamps
with open(CSV_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["packet_size_bytes", "send_timestamp", "receive_timestamp", "delay_seconds"])

    for size in PACKET_SIZES:
        for _ in range(NUM_PACKETS_PER_SIZE):
            pkt = build_packet(size)
            send_time = time.time()
            try:
                send(pkt, iface=working_interface, verbose=0)
            except Exception as e:
                print(f"Failed to send packet: {e}")
                continue
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

# Stop sniffer safely
try:
    if sniffer_started and hasattr(sniffer, 'running') and sniffer.running:
        sniffer.stop()
        print("Sniffer stopped successfully")
    else:
        print("Sniffer was not running or not started")
except Exception as e:
    print(f"Error stopping sniffer: {e}")
    # Force cleanup if needed
    try:
        sniffer._cleanup()
    except:
        pass
