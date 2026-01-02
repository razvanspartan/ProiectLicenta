from abc import ABC, abstractmethod

class MetricCollectorInterface(ABC):
    @abstractmethod
    def collect_metrics(self,instance_name: str, metrics: list) -> None:
        pass

    @abstractmethod
    def get_metrics_window(self) -> list:
        pass
    @abstractmethod
    def aggregate_metrics(self) -> dict:
        pass
    @abstractmethod
    def get_training_window(self) -> list:
        pass