from pinger import ping_host
import time
from datetime import datetime

def load_devices(filename="devices.txt"):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

def log_result(ip, status, latency):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{now}] {ip} is {'UP' if status else 'DOWN'} | Latency: {latency if status else 'N/A'} ms\n"
    with open("logs.txt", "a") as log:
        log.write(line)

def monitor():
    devices = load_devices()
    while True:
        print("\n--- NetPulse Status ---")
        for ip in devices:
            status, latency = ping_host(ip)
            if status:
                print(f"\033[92m{ip} is UP | Latency: {latency} ms\033[0m")  # green
            else:
                print(f"\033[91m{ip} is DOWN ❌\033[0m")  # red

            log_result(ip, status, latency)
        time.sleep(10)

if __name__ == "__main__":
    monitor()
