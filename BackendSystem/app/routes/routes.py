from flask import request
import requests

from app.services.docker_service import docker_client, extract_metrics_from_container


def register_routes(app):
    @app.route("/api/v1/backend/containers", methods=["GET"])
    def get_containers():
        if docker_client is None:
            return {"error": "Docker client not available"}, 503

        try:
            containers = docker_client.containers.list()
            container_info = []
            for container in containers:
                container_info.append(
                    {
                        "id": container.id,
                        "name": container.name,
                        "image": container.image.tags,
                        "status": container.status,
                    }
                )
            print(f"Retrieved {len(container_info)} containers")
            return {"containers": container_info}, 200
        except Exception as e:
            print(f"Error listing containers: {e}")
            return {"error": "Failed to retrieve containers"}, 500

    @app.route("/api/v1/backend/metrics/<service_name>", methods=["GET"])
    def get_metrics(service_name):
        if docker_client is None:
            return {"error": "Docker client not available"}, 503

        try:
            containers = docker_client.containers.list()
            metrics_info = []
            for container in containers:
                if service_name in container.name:
                    metrics_info.append(
                        {
                            "id": container.id,
                            "name": container.name,
                            "metrics": extract_metrics_from_container(container),
                        }
                    )
            return {"containers": metrics_info}, 200
        except Exception as e:
            print(f"Error retrieving metrics for service {service_name}: {e}")
            return {"error": "Failed to retrieve metrics"}, 500

    @app.route("/api/v1/backend/settings/<service_name>", methods=["POST"])
    def post_settings(service_name):
        data = request.get_json()
        response = requests.post(
            f"http://localhost:5000/api/v1/decisionmaker/update_settings/{service_name}",
            json=data,
        )
        return response.json(), 200

    @app.route("/api/v1/backend/settings/<service_name>", methods=["GET"])
    def get_settings(service_name):
        response = requests.get(
            f"http://localhost:5000/api/v1/decisionmaker/settings/{service_name}"
        )
        settings = response.json().get("settings")
        if not settings:
            return {"error": "Failed to retrieve settings"}, 500
        print(f"Retrieved settings for {service_name}: {settings}")
        data_to_send = {
            "cooldownPeriod": settings.get("cooldown_period"),
            "scaleUpThreshold": settings.get("scale_up_threshold"),
            "scaleDownThreshold": settings.get("scale_down_threshold"),
            "minInstances": settings.get("minimum_instances"),
            "maxInstances": settings.get("maximum_instances"),
        }
        return data_to_send, 200
