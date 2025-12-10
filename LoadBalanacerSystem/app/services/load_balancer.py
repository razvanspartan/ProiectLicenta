from app.interfaces.load_balancer_interface import LoadBalancerInterface


class LoadBalancer(LoadBalancerInterface):
    def __init__(self):
        self.service_instances = []
        self.current_index = -1

    def add_service_instance(self, server):
        self.service_instances.append(server)

    def remove_service_instance(self, server):
        self.service_instances.remove(server)
        print(f"Removed dead service instance: {server}")

    def get_next_service_instance(self):
        if not self.service_instances:
            return None
        instance = self.service_instances[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.service_instances)
        return instance

    def health_check_all_instances(self):
        for instance in self.service_instances:
            try:
                response = instance.health_check()
                if response.status_code != 200:
                    instance.failed_health_checks += 1
                if instance.failed_health_checks >= 3:
                    self.remove_service_instance(instance)
            except Exception:
                self.remove_service_instance(instance)