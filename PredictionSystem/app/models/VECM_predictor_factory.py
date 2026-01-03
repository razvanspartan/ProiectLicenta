from app.models import VECM_predictor
from app.models.VECM_predictor import VECMPredictor


class VECMPredictorFactory:
    def __init__(self):
        self.vecm_predictors = {}

    def get_vecm_predictor(self, service_name: str) -> VECM_predictor:
        if service_name not in self.vecm_predictors:
            self.vecm_predictors[service_name] = VECMPredictor(service_name)
        return self.vecm_predictors[service_name]

    def remove_vecm_predictor(self, service_name: str):
        if service_name in self.vecm_predictors:
            del self.vecm_predictors[service_name]