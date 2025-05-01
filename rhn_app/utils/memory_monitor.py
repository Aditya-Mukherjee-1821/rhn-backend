import os
import psutil
import threading
import time

def monitor_memory(interval=1):
    process = psutil.Process(os.getpid())
    while True:
        mem = process.memory_info().rss / (1024 ** 2)
        print(f"[MEMORY MONITOR] RSS Memory: {mem:.2f} MB")
        time.sleep(interval)

def start_monitor():
    t = threading.Thread(target=monitor_memory, daemon=True)
    t.start()
