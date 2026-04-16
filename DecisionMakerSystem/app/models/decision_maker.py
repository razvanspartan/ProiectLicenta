import time
from collections import deque

import docker
import subprocess
CONSTANTS={
    "SERVICE_CPU": 25.0
}

class DecisionMaker:
    def __init__(self, service_name, min_instances=1, max_instances=5, cooldown_seconds=30, scale_up_threshold=0.7, scale_down_threshold=0.2, scale_down_consideration_length=3, scale_up_consideration_length=3):
        self.service_name = service_name
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.last_decision_time_seconds = 0
        self.cooldown_seconds = cooldown_seconds
        self.prediction_window_size_max = 30
        self.instance_count = 1
        self.prediction_window = deque(maxlen=self.prediction_window_size_max)
        self.scale_up_threshold = scale_up_threshold * CONSTANTS["SERVICE_CPU"]
        self.scale_down_threshold = scale_down_threshold * CONSTANTS["SERVICE_CPU"]
        self.scale_down_consideration_length = scale_down_consideration_length
        self.scale_up_consideration_length = scale_up_consideration_length

    def add_prediction_point(self, prediction):
        self.prediction_window.append(prediction)
    def scale_down(self):
        try:
            compose_file = "/home/razvanspartan/PycharmProjects/ProiectLicenta/BookService/compose.yaml"
            target_count = self.instance_count - 1
            cmd = [
                "docker", "compose","-f", compose_file, "up", "-d",
                "--scale", f"{self.service_name}={target_count}"
            ]

            subprocess.run(cmd, check=True)

            self.last_decision_time_seconds = time.time()
            self.instance_count = target_count
            print(f"Scale down triggered via Compose. Now at {target_count} nodes.")

        except subprocess.CalledProcessError as e:
            print(f"Error scaling down via Docker Compose: {e}")
    def scale_up(self):
        try:
            compose_file = "/home/razvanspartan/PycharmProjects/ProiectLicenta/BookService/compose.yaml"
            target_count = self.instance_count + 1
            cmd = [
                "docker", "compose","-f", compose_file, "up", "-d",
                "--scale", f"{self.service_name}={target_count}"
            ]

            subprocess.run(cmd, check=True)

            self.last_decision_time_seconds = time.time()
            self.instance_count = target_count
            print(f"Scale up triggered via Compose. Now at {target_count} nodes.")

        except subprocess.CalledProcessError as e:
            print(f"Error scaling up via Docker Compose: {e}")

    def make_decision(self):
        if time.time() - self.last_decision_time_seconds < self.cooldown_seconds:
            print(f"In cooldown period, holding decision.{time.time() - self.last_decision_time_seconds} seconds. against cooldown of {self.cooldown_seconds} seconds.")
            return "Hold"
        if len(self.prediction_window) >= self.scale_up_consideration_length:
            recent_predictions = list(self.prediction_window)[-self.scale_up_consideration_length:]
            if all(pred > self.scale_up_threshold for pred in recent_predictions):
                if self.instance_count < self.max_instances:
                    self.scale_up()
        if len(self.prediction_window) >= self.scale_down_consideration_length:
            recent_predictions = list(self.prediction_window)[-self.scale_down_consideration_length:]
            if all(pred < self.scale_down_threshold for pred in recent_predictions):
                if self.instance_count > self.min_instances:
                    self.scale_down()
        return "Hold"

    def increase_instance_count(self):
        self.instance_count += 1

    def decrease_instance_count(self):
        self.instance_count -= 1