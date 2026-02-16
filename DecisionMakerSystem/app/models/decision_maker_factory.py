from typing import Dict

from app.services.load_balancer import LoadBalancer

from app.models.decision_maker import DecisionMaker


class DecisionMakerFactory:
    def __init__(self):
        self.decision_makers = {}

    def get_decision_maker(self, service_name: str) -> DecisionMaker:
        if service_name not in self.decision_makers:
            self.decision_makers[service_name] = LoadBalancer()
        return self.decision_makers[service_name]

    def remove_load_balancer(self, service_name: str):
        if service_name in self.decision_makers:
            del self.decision_makers[service_name]
