from abc import ABC, abstractmethod

class MetricCollectorInterface(ABC):
    @abstractmethod
    def collect_metrics(self,instance_name: str, metrics: list) -> None:
        pass
    @abstractmethod
    def aggregate_metrics(self) -> dict:
        pass