import time
from collections import deque

from app.interfaces.load_balancer_interface import LoadBalancerInterface
import requests

class LoadBalancer(LoadBalancerInterface):
    def __init__(self):
        self.service_instances = []
        self.current_index = -1
        self.requests = deque()
        self.window_time_requests_seconds = 5
    def add_service_instance(self, server):
        if server.ip not in [s.ip for s in self.service_instances]:
            self.service_instances.append(server)

    def remove_service_instance(self, server):
        self.service_instances.remove(server)
        print(f"Removed dead service instance: {server}")

    def get_next_service_instance(self):
        if not self.service_instances:
            return None
        self.current_index = (self.current_index + 1) % len(self.service_instances)
        instance = self.service_instances[self.current_index]
        return instance
    def count_request(self):
        now = time.time()
        self.requests.append(now)
    def get_requests_per_second(self):
        now = time.time()
        while self.requests and self.requests[0] < now - self.window_time_requests_seconds:
            self.requests.popleft()
        return len(self.requests) / self.window_time_requests_seconds
    def health_check_all_instances(self):
        for instance in self.service_instances:
            try:
                response = requests.get(f"http://{instance.ip}:{instance.port}/api/v1/{instance.service_name}/health",  timeout=2)
                if response.status_code != 200:
                    instance.failed_health_check_count += 1
                    if instance.failed_health_check_count >= 3:
                        self.remove_service_instance(instance)
                else:
                    instance.failed_health_check_count = 0
            except requests.RequestException as e:
                print({e})
                instance.failed_health_check_count += 1
                if instance.failed_health_check_count >= 3:
                    self.remove_service_instance(instance)