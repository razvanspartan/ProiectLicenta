import threading
import time

import requests
from app.models.metric_collector_factory import MetricCollectorFactory
from app.models.smoothing_predictor_factory import SmoothingPredictorFactory
import docker

from app.models.SGDRegressor_factory import SGDRegressorPredictorFactory

metric_collector_factory = MetricCollectorFactory()
smoothing_predictor_factory = SmoothingPredictorFactory()
sgd_regressor_factory = SGDRegressorPredictorFactory()
try:
    docker_client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    print("Docker client created successfully")
except Exception as e:
    print(f"Warning: couldn't create docker client: {e}")
    docker_client = None

avg_cpus=[]
def register_routes(app):

    def collect_metrics(interval=5):
        while True:
            if docker_client is None:
                time.sleep(interval)
                continue

            try:
                containers = docker_client.containers.list()
            except Exception as e:
                print(f"Error listing containers: {e}")
                time.sleep(interval)
                continue
            for container in containers:
                try:
                    service_name = container.labels.get("service_name")
                    if service_name == "loadbalancer":
                        continue
                    metric_collector = metric_collector_factory.get_metric_collector(service_name)
                    response = requests.get(f"http://0.0.0.0:7000/api/v1/loadbalancer/metrics/{service_name}")
                    metrics = extract_metrics_from_container(container)
                    metrics['requests_per_second'] = response.json().get('requests_per_second', 0)
                    print("metrics for container:", container.name, " are", metrics)
                    metric_collector.collect_metrics(container.name, metrics)
                except Exception as e:
                    print(f"Error collecting metrics for container {container.name}: {e}")
            if len(containers) > 0:
                aggregate_metrics_for_smoothing()
            time.sleep(interval)

    def aggregate_metrics_for_smoothing():
        for metric_collector_name, metric_collector in metric_collector_factory.metric_collectors.items():
            smoothing_predictor = smoothing_predictor_factory.get_smoothing_predictor(metric_collector_name)
            #sgd_predictor = sgd_regressor_factory.get_sgd_regressor_predictor(metric_collector_name)
            data_point = metric_collector.aggregate_metrics()
            avg_cpus.append(data_point['cpu_avg'])
            smoothing_predictor.update_model(data_point)
            #sgd_predictor.update_model(data_point)
            prediction = smoothing_predictor.predict(steps=3)
            #prediction_sgd = sgd_predictor.predict()
            if prediction is None:
                print("No prediction available")
                return
            print(f"Predicted CPU usage for {metric_collector_name} in 3(5s) steps: {prediction}, SGD: {prediction_sgd}")

    def extract_metrics_from_container(container) -> dict:
        stats = container.stats(stream=False)
        cpu_stats = stats["cpu_stats"]
        precpu_stats = stats.get("precpu_stats", {})
        cpu_delta = (
                cpu_stats["cpu_usage"]["total_usage"]
                - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
        )
        system_delta = (
                cpu_stats.get("system_cpu_usage", 0)
                - precpu_stats.get("system_cpu_usage", 0)
        )
        online_cpus = cpu_stats.get(
            "online_cpus",
            len(cpu_stats["cpu_usage"].get("percpu_usage", [])) or 1
        )
        cpu_percent = 0.0
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * online_cpus * 100
        mem_usage = stats["memory_stats"]["usage"]
        mem_limit = stats["memory_stats"]["limit"]
        mem_percent = (
            (mem_usage / mem_limit) * 100 if mem_limit > 0 else 0.0
        )
        return {
            "cpu": round(cpu_percent, 2),
            "memory": round(mem_percent, 2),
        }
    threading.Thread(target=collect_metrics, daemon=True).start()