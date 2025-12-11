from typing import Dict

from app.services.load_balancer import LoadBalancer


class LoadBalancerFactory:
    def __init__(self):
        self.load_balancers = {}

    def get_load_balancer(self, service_name: str) -> LoadBalancer:
        if service_name not in self.load_balancers:
            self.load_balancers[service_name] = LoadBalancer()
        return self.load_balancers[service_name]

    def remove_load_balancer(self, service_name: str):
        if service_name in self.load_balancers:
            del self.load_balancers[service_name]
