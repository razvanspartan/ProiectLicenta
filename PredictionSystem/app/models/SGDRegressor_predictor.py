from collections import deque
import numpy as np
import os
import pickle

from sklearn.linear_model import SGDRegressor
from sklearn.preprocessing import StandardScaler
class SGDRegressorPredictor:
    def __init__(self, name):
        self.scaler=StandardScaler()
        self.name = name
        self.window_size = 600
        self.data = deque(maxlen=self.window_size)
        self.min_feature_batch = 30
        self.model = SGDRegressor(
            loss='squared_error',
            penalty='l2',
            alpha=0.001,
            learning_rate='adaptive',
            eta0=0.02,
            warm_start=True,
            max_iter=1,
            tol=None
        )
        self.window=deque(maxlen=self.window_size)
        self.is_fitted = False
        self.feature_batch = deque(maxlen=self.min_feature_batch+1)

    def create_features_from_window(self, window):
        cpu = np.array(window)
        if len(cpu)<30:
            return None
        features = [
            cpu[-1],
            cpu[-2],
            cpu[-5],
            cpu[-10],
            cpu[-20],
            np.mean(cpu[-5:]),
            np.mean(cpu[-10:]),
            np.std(cpu[-5:]),
            cpu[-1] - cpu[-5],
            cpu[-5] - cpu[-10],
            (cpu[-1] - cpu[-10]) / 10,
            (cpu[-1] - cpu[-5]) - (cpu[-5] - cpu[-10]),
            np.max(cpu[-20:]),
            np.min(cpu[-20:]),
        ]
        return np.array(features)

    def update_model(self, data_point: dict):
        new_cpu = float(data_point["cpu_avg"])
        self.window.append(new_cpu)

        if len(self.window) < 31:
            return

        prev_window = list(self.window)[:-1]
        feature = self.create_features_from_window(prev_window)

        if feature is None:
            return

        self.feature_batch.append((feature, new_cpu))

        if not self.is_fitted:
            if len(self.feature_batch) > self.min_feature_batch:
                X = np.array([f for f, _ in self.feature_batch])
                y = np.array([t for _, t in self.feature_batch])

                self.scaler.fit(X)
                X_scaled = self.scaler.transform(X)

                self.model.fit(X_scaled, y)
                self.save()
                self.is_fitted = True
        else:
            X_scaled = self.scaler.transform([feature])
            self.model.partial_fit(X_scaled, [new_cpu])
            self.save()

    def predict(self):
        if not self.is_fitted or len(self.window) < 31:
            return None

        features = self.create_features_from_window(list(self.window))
        if features is None:
            return None

        X_scaled = self.scaler.transform([features])
        return float(self.model.predict(X_scaled)[0])

    def save(self):
        os.makedirs("model", exist_ok=True)
        with open(f"model/{self.name}_sgd.pkl", "wb") as f:
            pickle.dump(self.model, f)

    def load_model_if_exists(self):
        path = f"model/bookservice_sgd.pkl"
        if not os.path.isfile(path):
            print("was false path")
            return False
        else:
            with open(path, "rb") as f:
                self.model= pickle.load(f)
        return SGDRegressor(
            loss='squared_error',
            penalty='l2',
            alpha=0.001,
            learning_rate='adaptive',
            eta0=0.02,
            warm_start=True,
            max_iter=1,
            tol=None
        )
