class VECM_predictor:
    def __init__(self, model):
        self.model = model

    def predict(self, input_data, steps):
        """
        Generate predictions using the VECM model.

        Parameters:
        input_data (array-like): The input data for prediction.
        steps (int): The number of steps to predict.

        Returns:
        array-like: The predicted values.
        """
        try:
            predictions = self.model.predict(input_data, steps=steps)
            return predictions
        except Exception as e:
            print(f"An error occurred during prediction: {e}")
            return None