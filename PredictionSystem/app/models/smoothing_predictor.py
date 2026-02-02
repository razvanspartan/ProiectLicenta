from collections import deque
import numpy as np
import os
import pickle
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class SmoothingPredictor:
    def __init__(self, name, dt_seconds=1):
        self.name = name
        self.dt = dt_seconds
        self.window_size = 760
        self.data = deque(maxlen=self.window_size)
        self.min_window_length = 80
        self.model = None
        self.fitted = None

    def update_model(self, data_point: dict):
        cpu = float(data_point["cpu_avg"])
        if cpu < 0.2:
            cpu = 0.0
        self.data.append(cpu)
        if len(self.data) < self.min_window_length:
            return

        self.model = ExponentialSmoothing(
            np.array(self.data),
            trend='add',
            seasonal=None,
            initialization_method="estimated",
        )

        self.fitted = self.model.fit(
            smoothing_level=0.3,
            smoothing_trend=0.1,
            optimized=False,
        )
        self.save()

    def predict(self, steps: int = 1):
        if self.fitted is None:
            return None

        cpu_pred = float(self.fitted.forecast(steps)[-1])

        return max(0.0, min(cpu_pred, 25.0))

    def save(self):
        os.makedirs("model", exist_ok=True)
        with open(f"model/{self.name}_hw.pkl", "wb") as f:
            pickle.dump(list(self.data), f)

    def load_model_if_exists(self):
        path = f"model/{self.name}_hw.pkl"
        if not os.path.isfile(path):
            return False

        with open(path, "rb") as f:
            self.data = deque(pickle.load(f), maxlen=self.window_size)

        return True
