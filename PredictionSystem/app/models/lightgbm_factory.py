
from app.models.lightgbm_predictor import LightGBMPredictor


class LightgbmFactory:
    def __init__(self):
        self.lightgbm_predictors = {}

    def get_lightgbm_predictor(self, service_name: str) -> LightGBMPredictor:
        if service_name not in self.lightgbm_predictors:
            predictor = LightGBMPredictor(service_name)
            predictor.load_model()
            self.lightgbm_predictors[service_name] = predictor
        return self.lightgbm_predictors[service_name]

    def remove_lightgbm_predictor(self, service_name: str):
        if service_name in self.lightgbm_predictors:
            del self.lightgbm_predictors[service_name]