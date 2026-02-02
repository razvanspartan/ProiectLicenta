from app.models import smoothing_predictor
from app.models.smoothing_predictor import SmoothingPredictor


class SmoothingPredictorFactory:
    def __init__(self):
        self.smoothing_predictors = {}

    def get_smoothing_predictor(self, service_name: str) -> SmoothingPredictor:
        if service_name not in self.smoothing_predictors:
            predictor = SmoothingPredictor(service_name)
            print(predictor.load_model_if_exists())
            self.smoothing_predictors[service_name] = predictor
        return self.smoothing_predictors[service_name]

    def remove_smoothing_predictor(self, service_name: str):
        if service_name in self.smoothing_predictors:
            del self.smoothing_predictors[service_name]