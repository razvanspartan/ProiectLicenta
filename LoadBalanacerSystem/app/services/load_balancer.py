from app.interfaces.load_balancer_interface import LoadBalancerInterface


class LoadBalancer(LoadBalancerInterface):
    def __init__(self):
        self.service_instances = []
        self.current_index = -1

    def add_service_instance(self, server):
        self.service_instances.append(server)

    def remove_service_instance(self, server):
        self.service_instances.remove(server)

    def get_next_service_instance(self):
        if not self.service_instances:
            return None
        instance = self.service_instances[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.service_instances)
        return instance