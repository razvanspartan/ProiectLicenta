
from app.models.SGDRegressor_predictor import SGDRegressorPredictor


class SGDRegressorPredictorFactory:
    def __init__(self):
        self.sgd_regressor_predictors = {}

    def get_sgd_regressor_predictor(self, service_name: str) -> SGDRegressorPredictor:
        if service_name not in self.sgd_regressor_predictors:
            predictor = SGDRegressorPredictor(service_name)
            print(predictor.load_model_if_exists())
            self.sgd_regressor_predictors[service_name] = predictor
        return self.sgd_regressor_predictors[service_name]

    def remove_sgd_regressor_predictor(self, service_name: str):
        if service_name in self.sgd_regressor_predictors:
            del self.sgd_regressor_predictors[service_name]