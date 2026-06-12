import threading
import time
import requests
import math
import random

TARGET_URL = "http://0.0.0.0:7000/api/v1/bookservice/expensive_cpu_computations"
target_rps = 1.0


def worker():
    session = requests.Session()
    while True:
        delay = (1.0 / max(target_rps, 0.1)) * 3
        time.sleep(max(0.01, delay * random.uniform(0.8, 1.2)))

        try:
            session.get(TARGET_URL, timeout=2)
        except Exception:
            pass


def slow_rps_controller(stop_event):
    global target_rps
    start_time = time.time()

    while not stop_event.is_set():
        elapsed = time.time() - start_time
        base_load = 1.5 + 3.5 * math.sin(elapsed / 60.0)
        target_rps = max(0.5, base_load + random.uniform(-0.5, 0.5))
        print(f"Time: {int(elapsed)}s | Target RPS: {target_rps:.2f}")
        time.sleep(5)

if __name__ == "__main__":
    stop_event = threading.Event()
    for i in range(3):
        threading.Thread(target=worker, daemon=True).start()
    threading.Thread(target=slow_rps_controller, args=(stop_event,), daemon=True).start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")