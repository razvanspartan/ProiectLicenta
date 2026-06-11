import socket
import time

import requests


def register_to_load_balancer():
    while True:
        load_balancer_url = "http://loadbalancer:7000/api/v1/loadbalancer/register"
        data = {
            "service_name": "orderservice",
            "service_ip": socket.gethostbyname(socket.gethostname()),
            "service_port": 4000,
        }
        try:
            response = requests.post(load_balancer_url, json=data)
            if response.status_code == 201:
                print("OrderService instance registered with Load Balancer successfully.")
            else:
                print("OrderService instance registration with Load Balancer failed.")
        except Exception as e:
            print(f"error registering OrderService instance with Load Balancer: {e}")
        time.sleep(10)
