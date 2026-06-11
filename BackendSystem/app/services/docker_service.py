import docker

try:
    docker_client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
    print("Docker client created successfully")
except Exception as e:
    print(f"Warning: couldn't create docker client: {e}")
    docker_client = None


def extract_metrics_from_container(container) -> dict:
    stats = container.stats(stream=False)
    cpu_stats = stats["cpu_stats"]
    precpu_stats = stats.get("precpu_stats", {})
    cpu_delta = cpu_stats["cpu_usage"]["total_usage"] - precpu_stats.get(
        "cpu_usage", {}
    ).get("total_usage", 0)
    system_delta = cpu_stats.get("system_cpu_usage", 0) - precpu_stats.get(
        "system_cpu_usage", 0
    )
    online_cpus = cpu_stats.get(
        "online_cpus", len(cpu_stats["cpu_usage"].get("percpu_usage", [])) or 1
    )
    cpu_percent = 0.0
    if system_delta > 0 and cpu_delta > 0:
        cpu_percent = (cpu_delta / system_delta) * online_cpus * 100
    mem_usage = stats["memory_stats"]["usage"]
    mem_limit = stats["memory_stats"]["limit"]
    mem_percent = (mem_usage / mem_limit) * 100 if mem_limit > 0 else 0.0
    return {
        "cpu": round(cpu_percent, 2),
        "memory": round(mem_percent, 2),
    }
