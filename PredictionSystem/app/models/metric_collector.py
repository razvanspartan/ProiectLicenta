import time

from app.interfaces.metric_collector_interface import MetricCollectorInterface


class MetricCollector(MetricCollectorInterface):
    def __init__(self):
        self.window_size_seconds = 5
        self.instances = {}

    def collect_metrics(self, instance_name: str, metrics: dict) -> None:
        now = time.time()
        self.instances[instance_name] = {
            "last_seen": now,
            "metrics": metrics
        }

    def aggregate_metrics (self):
        now = time.time()
        for instance_name in list(self.instances.keys()):
            if now - self.instances[instance_name]["last_seen"] > 300:
                del self.instances[instance_name]
        if not self.instances:
            return {
            "cpu_avg": 0,
            "memory_sum": 0,
            "requests_per_second": 0
            }
        cpu_avg = sum(metric["metrics"]["cpu"] for metric in self.instances.values()) / len(self.instances)
        memory_sum = sum(metric["metrics"]["memory"] for metric in self.instances.values())
        requests_per_second= sum(metric["metrics"]["requests_per_second"] for metric in self.instances.values())
        return {
            "cpu_avg": cpu_avg,
            "memory_sum": memory_sum,
            "requests_per_second": requests_per_second
        }