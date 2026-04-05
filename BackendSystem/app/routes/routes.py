import docker

try:
    docker_client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    print("Docker client created successfully")
except Exception as e:
    print(f"Warning: couldn't create docker client: {e}")
    docker_client = None

def register_routes(app):
    @app.route('/api/v1/backend/containers', methods=['GET'])
    def get_containers():
        if docker_client is None:
            return {"error": "Docker client not available"}, 503

        try:
            containers = docker_client.containers.list()
            container_info = []
            for container in containers:
                container_info.append({
                    "id": container.id,
                    "name": container.name,
                    "image": container.image.tags,
                    "status": container.status
                })
            print(f"Retrieved {len(container_info)} containers")
            return {"containers": container_info}, 200
        except Exception as e:
            print(f"Error listing containers: {e}")
            return {"error": "Failed to retrieve containers"}, 500

    @app.route('/api/v1/backend/metrics/<service_name>', methods=['GET'])
    def get_metrics(service_name):
        if docker_client is None:
            return {"error": "Docker client not available"}, 503

        try:
            containers = docker_client.containers.list()
            metrics_info = []
            for container in containers:
                if service_name in container.name:
                    metrics_info.append({
                        "id": container.id,
                        "name": container.name,
                        "metrics": extract_metrics_from_container(container)
                    })
            return {"containers": metrics_info}, 200
        except Exception as e:
            print(f"Error retrieving metrics for service {service_name}: {e}")
            return {"error": "Failed to retrieve metrics"}, 500

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
