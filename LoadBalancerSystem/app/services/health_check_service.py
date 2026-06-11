import time

from app.services.load_balancer_factory import LoadBalancerFactory


def health_check_services(load_balancer_factory: LoadBalancerFactory, interval=10):
    while True:
        for load_balancer in load_balancer_factory.load_balancers.values():
            load_balancer.health_check_all_instances()
        time.sleep(interval)
