from typing import Dict

from app.services.metric_collector import MetricCollector


class MetricCollectorFactory:
    def __init__(self):
        self.metric_collectors = {}

    def get_metric_collector(self, service_name: str) -> LoadBalancer:
        if service_name not in self.metric_collectors:
            self.metric_collectors[service_name] = MetricCollector()
        return self.metric_collectors[service_name]

    def remove_metric_collector(self, service_name: str):
        if service_name in self.metric_collectors:
            del self.metric_collectors[service_name]
