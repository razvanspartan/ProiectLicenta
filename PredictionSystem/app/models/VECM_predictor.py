from typing import Any

from statsmodels.tsa.vector_ar.vecm import VECM
import pickle

class VECMPredictor:
    def __init__(self):
        self.model = None
        self.name = None
        self.training_window = []
        self.prediction_window = []
        self.training_window_size = 100
        self.k_arr_diff_order = 1
        self.cointegration_rank = 1
        self.prediction_window_size = self.k_arr_diff_order+2
    def predict(self, input_data: list, steps: int) -> Any | None:
        if self.model is None:
            predictions = self.model.predict(input_data, steps=steps)
            return predictions
        else:
            return None

    def train_model(self) -> None:
        if len(self.training_window) >= self.training_window_size:
            self.model = VECM(self.training_window, k_ar_diff=self.k_arr_diff_order, coint_rank=self.cointegration_rank).fit()
            with open(f'models/{self.name}_vecm_model.pkl', 'wb') as f:
                pickle.dump(self.model, f)

    def add_data(self, data_point: dict) -> None:
        self.training_window.append(data_point)
        if len(self.training_window) > self.training_window_size:
            self.training_window.pop(0)
        self.prediction_window.append(data_point)
        if len(self.prediction_window) > self.prediction_window_size:
            self.prediction_window.pop(0)
