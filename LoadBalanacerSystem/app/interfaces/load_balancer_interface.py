from abc import ABC, abstractmethod

class LoadBalancerInterface(ABC):
    @abstractmethod
    def add_service_instance(self, server):
        pass

    @abstractmethod
    def remove_service_instance(self, server):
        pass

    @abstractmethod
    def get_next_service_instance(self):
        pass

    @abstractmethod
    def health_check_all_instances(self):
        pass