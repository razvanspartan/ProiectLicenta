#!/usr/bin/env python3
# Script: PredictionSystem/evaluate_model.py
# Usage: python evaluate_model.py --service bookservice [--csv path/to.csv] [--retrain]

import argparse
from pathlib import Path
import sys
import pandas as pd

from app.models.lightgbm_predictor import LightGBMPredictor


def main():
    p = argparse.ArgumentParser(
        description="Evaluate LightGBM model for a service using its training CSV."
    )

    p.add_argument(
        "--service",
        required=True,
        help="Service name (used to locate model and default CSV)",
    )

    p.add_argument(
        "--csv",
        help="Path to CSV file to evaluate (defaults to training_data_<service>.csv)",
    )

    p.add_argument(
        "--retrain",
        action="store_true",
        help="If provided, train model from CSV before evaluation",
    )

    p.add_argument(
        "--horizon", type=int, help="Prediction horizon (number of steps ahead)"
    )

    args = p.parse_args()

    svc = args.service

    candidates = []

    if args.csv:
        candidates.append(Path(args.csv))
    else:
        candidates.append(Path.cwd() / f"training_data_{svc}.csv")
        candidates.append(Path(__file__).resolve().parent / f"training_data_{svc}.csv")
        candidates.append(
            Path(__file__).resolve().parent.parent / f"training_data_{svc}.csv"
        )

    csv_path = None
    tried = []

    for c in candidates:
        tried.append(str(c))

        if c.is_file():
            csv_path = c
            break

    if csv_path is None:
        print(f"CSV file not found for service '{svc}'. Tried:")

        for t in tried:
            print(f"  - {t}")

        sys.exit(2)

    try:
        df = pd.read_csv(csv_path)

    except Exception as e:
        print(f"Failed to read CSV {csv_path}: {e}")
        sys.exit(3)

    if args.horizon is not None:
        predictor = LightGBMPredictor(svc, horizon=int(args.horizon))
    else:
        predictor = LightGBMPredictor(svc)

    if args.retrain:
        try:
            print("Training model from CSV...")
            predictor.train_model(df)
            print("Training completed.")

        except Exception as e:
            print(f"Training failed: {e}")
            sys.exit(4)

    else:
        try:
            predictor.load_model()

        except Exception:
            pass

        if (
            predictor.model is not None
            and args.horizon is not None
            and predictor.horizon != args.horizon
        ):
            print(
                f"Loaded model horizon={predictor.horizon} "
                f"does not match requested horizon={args.horizon}. "
                f"Re-training temporarily for evaluation."
            )
            try:
                predictor.train_model(df)
                print("Temporary retraining completed.")

            except Exception as e:
                print(f"Retraining failed: {e}")
                sys.exit(4)

        if predictor.model is None:
            try:
                print("No saved model found — training temporarily for evaluation...")
                predictor.train_model(df)
                print("Temporary training completed.")

            except Exception as e:
                print(f"Auto-training failed: {e}")
                sys.exit(4)

    try:
        res = predictor.evaluate(df)

    except Exception as e:
        print(f"Evaluation failed: {e}")
        sys.exit(5)

    print("Evaluation results:")
    print(f"  MSE : {res['mse']}")
    print(f"  MAE : {res['mae']}")
    print(f"  RMSE: {res['rmse']}")
    print(f"  R2  : {res['r2']}")

    out_csv = Path(f"pred_vs_actual_{svc}.csv")

    try:
        res["comparison"].to_csv(out_csv, index=False)
        print(f"Saved predicted vs actual to {out_csv}")

    except Exception as e:
        print(f"Failed to save comparison CSV: {e}")


if __name__ == "__main__":
    main()
