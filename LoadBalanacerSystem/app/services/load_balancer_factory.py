from typing import Dict

from app.services.load_balancer import LoadBalancer


class LoadBalancerFactory:
    def __init__(self):
        self.load_balancer = {}

    def get_load_balancer(self, service_name: str) -> LoadBalancer:
        if service_name not in self.load_balancer:
            self.load_balancer[service_name] = LoadBalancer()
        return self.load_balancer[service_name]

    def remove_load_balancer(self, service_name: str):
        if service_name in self.load_balancer:
            del self.load_balancer[service_name]
