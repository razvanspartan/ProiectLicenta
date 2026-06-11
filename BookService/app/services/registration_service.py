import socket
import time

import requests


def register_to_load_balancer():
    while True:
        load_balancer_url = "http://loadbalancer:7000/api/v1/loadbalancer/register"
        data = {
            "service_name": "bookservice",
            "service_ip": socket.gethostbyname(socket.gethostname()),
            "service_port": 6000,
        }
        try:
            requests.post(load_balancer_url, json=data, timeout=2)
        except Exception as e:
            print(f"Error registering BookService with Load Balancer: {e}")
        time.sleep(5)
