
class ServiceInstance:
    def __init__(self, ip, port, service_name, failed_health_check_count=0):
        self.ip = ip
        self.port = port
        self.service_name = service_name
        self.failed_health_check_count = failed_health_check_count

    def __repr__(self):
        return f"<{self.service_name} Instance of address {self.ip}:{self.port} failed={self.failed_health_check_count}>"