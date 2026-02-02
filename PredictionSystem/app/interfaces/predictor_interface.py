from abc import ABC, abstractmethod

class PredictorInterface(ABC):

    @abstractmethod
    def predict(self, data):
        pass

    @abstractmethod
    def update_model(self, data):
        pass

    @abstractmethod
    def save_model(self, filepath: str):
        pass

    @abstractmethod
    def load_model(self, filepath: str):
        pass