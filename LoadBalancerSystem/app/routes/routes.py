import threading
import time

from flask import request
import requests

from app.services.load_balancer_factory import LoadBalancerFactory

from app.models.service_instance import ServiceInstance
load_balancer_factory = LoadBalancerFactory()
def register_routes(app):
    @app.route('/api/v1/loadbalancer/register', methods=['POST'])
    def register_service():
        data = request.get_json()
        service_name = data['service_name']
        service_ip = data['service_ip']
        service_port = data['service_port']
        service_instance = ServiceInstance(ip=service_ip, port=service_port, service_name=service_name)
        load_balancer = load_balancer_factory.get_load_balancer(service_name=service_name)
        if service_instance not in load_balancer.service_instances:
            load_balancer.add_service_instance(service_instance)
            return {"message": "Service instance registered successfully."}, 201
        return {"message": "Service instance already registered."}, 200

    @app.route('/api/v1/loadbalancer/unregister', methods=['POST'])
    def unregister_service():
        data = request.get_json()
        service_name = data['service_name']
        service_ip = data['service_ip']
        service_port = data['service_port']
        service_instance = ServiceInstance(service_name=service_name, service_ip=service_ip, service_port=service_port)
        load_balancer = load_balancer_factory.get_load_balancer()
        if service_instance in load_balancer.service_instances:
            load_balancer.remove_service_instance(service_instance)
            return {"message": "Service instance unregistered successfully."}, 200
        return {"message": "Service instance not found."}, 404

    def health_check_services(interval=10):
        while True:
            for load_balancer in load_balancer_factory.load_balancers.values():
                print(load_balancer.service_instances)
                load_balancer.health_check_all_instances()
            time.sleep(interval)

    @app.route('/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
    def send_request(path):
        segments = path.split('/')
        service_name = segments[0]
        forward_path = "/".join(segments[1:])
        load_balancer = load_balancer_factory.get_load_balancer(service_name=service_name)
        service_instance = load_balancer.get_next_service_instance()
        if not service_instance:
            return {"message": "No available service instances."}, 503
        url = f"http://{service_instance.ip}:{service_instance.port}/api/v1/{service_name}/{forward_path}"
        method = request.method
        headers = {key: value for key, value in request.headers.items() if key.islower() != 'Host'}
        data = request.get_data()
        resp = requests.request(method, url, headers=headers, data=data, params=request.args)
        print("Sent request to:", url)
        load_balancer.count_request()
        response = app.response_class(
            response=resp.content,
            status=resp.status_code,
            headers=dict(resp.headers)
        )
        return response
    @app.route('/api/v1/loadbalancer/test', methods=['GET'])
    def test_load_balancer():
        return {"message": "Load Balancer is operational."}, 200

    @app.route("/api/v1/loadbalancer/metrics/<string:service_name>", methods=['GET'])
    def metrics(service_name):
        load_balancer = load_balancer_factory.get_load_balancer(service_name=service_name)
        return {
            "requests_per_second" : load_balancer.get_requests_per_second(),
        }


    threading.Thread(target=health_check_services, daemon=True).start()