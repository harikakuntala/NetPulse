import os
import time

def ping_host(ip):
    start = time.time()
    result = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
    end = time.time()
    latency = round((end - start) * 1000, 2)  # milliseconds
    return (result == 0), latency
