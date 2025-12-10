from app.interfaces.load_balancer_interface import LoadBalancerInterface


class LoadBalancer(LoadBalancerInterface):
    def __init__(self):
        self.service_instances = []
        self.current_index = -1

    def add_service_instance(self, server):
        self.service_instances.append(server)
