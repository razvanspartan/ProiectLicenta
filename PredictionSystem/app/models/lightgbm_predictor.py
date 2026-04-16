import os

import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
import pickle
from pathlib import Path


class LightGBMPredictor:
    def __init__(self, name: str, horizon: int = 2, n_lags: int = 3):
        self.model = None
        self.name = name
        self.horizon = horizon
        self.n_lags = n_lags
        self.target_col = "cpu_avg"
        self.feature_columns = None
        self._window = pd.DataFrame()
        self._min_rows_required = self.n_lags + self.horizon + 2

    def start_model(self):
        csv_path = Path(f"training_data_{self.name}.csv")
        if not csv_path.is_file():
            return False
        try:
            df = pd.read_csv(csv_path)
        except Exception:
            return False

        if df.empty or len(df) < self._min_rows_required:
            return False

        self.train_model(df)
        return True

    def transform_for_lgbm(self, df, target_col="cpu_avg", horizon=5, n_lags=3, with_target: bool = True):
        df = df.copy()
        cols_to_lag = ["cpu_avg", "memory_sum", "requests_per_second", "instance_count"]

        if "cpu_avg" not in df.columns:
            raise ValueError("Missing required column: cpu_avg")
        if with_target and target_col not in df.columns:
            raise ValueError(f"Missing target column: {target_col}")

        for col in cols_to_lag:
            if col in df.columns:
                for lag in range(1, n_lags + 1):
                    df[f"{col}_lag_{lag}"] = df[col].shift(lag)

        df["cpu_rolling_mean"] = df["cpu_avg"].rolling(window=n_lags).mean()
        df["cpu_rolling_std"] = df["cpu_avg"].rolling(window=n_lags).std()

        if with_target:
            df["target"] = df[target_col].shift(-horizon)

        df = df.dropna().reset_index(drop=True)
        if "timestamp" in df.columns:
            df = df.drop(columns=["timestamp"])

        return df

    def train_model(self, df, target_col="cpu_avg", horizon=None, n_lags=None):
        if horizon is None:
            horizon = self.horizon
        if n_lags is None:
            n_lags = self.n_lags

        processed_df = self.transform_for_lgbm(
            df,
            target_col=target_col,
            horizon=horizon,
            n_lags=n_lags,
            with_target=True,
        )

        if processed_df.empty:
            raise ValueError("No rows left after feature engineering (check horizon/n_lags and data length).")

        X = processed_df.drop(columns=["target"])
        y = processed_df["target"]

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, shuffle=False)

        self.model = lgb.LGBMRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            verbose = -1,
        )

        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)],
        )

        self.feature_columns = list(X.columns)
        self.horizon = int(horizon)
        self.n_lags = int(n_lags)
        self.target_col = target_col

    def _append_to_window(self, point):
        if isinstance(point, pd.DataFrame):
            new_df = point.copy()
        elif isinstance(point, pd.Series):
            new_df = point.to_frame().T
        elif isinstance(point, dict):
            new_df = pd.DataFrame([point])
        else:
            raise TypeError("predict() expects a dict, pandas Series, or pandas DataFrame for the new point(s).")

        self._window = pd.concat([self._window, new_df], ignore_index=True)

        keep_cols = ["cpu_avg", "memory_sum", "requests_per_second", "instance_count", "timestamp"]
        existing = [c for c in keep_cols if c in self._window.columns]
        self._window = self._window[existing]

        if "timestamp" in self._window.columns:
            self._window = self._window.sort_values("timestamp").reset_index(drop=True)

        max_rows = max(self.n_lags + 5, self.n_lags + 1)
        if len(self._window) > max_rows:
            self._window = self._window.tail(max_rows).reset_index(drop=True)

    def predict(self, X):
        if self.model is None:
            raise RuntimeError("Model is not trained/loaded.")
        if not self.feature_columns:
            raise RuntimeError("Missing feature_columns; train or load a model bundle first.")

        self._append_to_window(X)
        if len(self._window) < self.n_lags:
            return None

        feats = self.transform_for_lgbm(
            self._window,
            target_col=self.target_col,
            horizon=self.horizon,
            n_lags=self.n_lags,
            with_target=False,
        )

        if feats.empty:
            return None

        last_row = feats.tail(1)
        pred = self.model.predict(last_row[self.feature_columns])
        return float(pred[0])

    def save_model(self):
        if self.model is None:
            raise RuntimeError("Nothing to save (model is not trained/loaded).")
        os.makedirs("model", exist_ok=True)
        path = f"model/{self.name}_lightgbm.pkl"

        payload = {
            "model": self.model,
            "feature_columns": self.feature_columns,
            "horizon": self.horizon,
            "n_lags": self.n_lags,
            "target_col": self.target_col,
        }

        with open(path,"wb") as f:
            pickle.dump(payload, f)

    def load_model(self):
        path = f"model/{self.name}_lightgbm.pkl"
        if not os.path.isfile(path):
            self.start_model()
            return None
        with open(path, "rb") as f:
            payload = pickle.load(f)
        if isinstance(payload, dict) and "model" in payload:
            self.model = payload["model"]
            self.feature_columns = payload.get("feature_columns")
            self.horizon = int(payload.get("horizon", self.horizon))
            self.n_lags = int(payload.get("n_lags", self.n_lags))
            self.target_col = payload.get("target_col", self.target_col)
        else:
            self.model = payload
            self.feature_columns = None
        return None