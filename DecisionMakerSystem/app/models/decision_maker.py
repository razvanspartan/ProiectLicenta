import time
from collections import deque

import docker

try:
    docker_client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    print("Docker client created successfully")
except Exception as e:
    print(f"Warning: couldn't create docker client: {e}")
    docker_client = None

class DecisionMaker:
    def __init__(self, service_name, min_instances=1, max_instances=4, cooldown_seconds=120, scale_up_threshold=0.7, scale_down_threshold=0.2, scale_down_consideration_length=10, scale_up_consideration_length=5):
        self.service_name = service_name
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.last_decision_time_seconds = 0
        self.cooldown_seconds = cooldown_seconds
        self.prediction_window_size_max = 30
        self.instance_count = 0
        self.is_scaling = False
        self.prediction_window = deque(maxlen=self.prediction_window_size_max)
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.scale_down_consideration_length = scale_down_consideration_length
        self.scale_up_consideration_length = scale_up_consideration_length

    def add_prediction_point(self, prediction):
        self.prediction_window.append(prediction)

    def make_decision(self):
        if self.is_scaling:
            return None
        if time.time() - self.last_decision_time_seconds < self.cooldown_seconds:
            return None
        if len(self.prediction_window) >= self.scale_up_consideration_length:
            recent_predictions = list(self.prediction_window)[-self.scale_up_consideration_length:]
            if all(pred > self.scale_up_threshold for pred in recent_predictions):
                if self.instance_count < self.max_instances:
                    self.last_decision_time_seconds = time.time()
                    self.is_scaling = True
                    return "scale_up"
        if len(self.prediction_window) >= self.scale_down_consideration_length:
            recent_predictions = list(self.prediction_window)[-self.scale_down_consideration_length:]
            if all(pred < self.scale_down_threshold for pred in recent_predictions):
                if self.instance_count > self.min_instances:
                    self.last_decision_time_seconds = time.time()
                    self.is_scaling = True
                    return "scale_down"
        return None

    def increase_instance_count(self):
        self.instance_count += 1
        self.is_scaling = False

    def decrease_instance_count(self):
        self.instance_count -= 1
        self.is_scaling = False