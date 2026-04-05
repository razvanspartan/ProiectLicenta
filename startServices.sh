#!/bin/bash
set -euo pipefail


cleanup() {
  echo "Stopping everything..."

  kill "${PREDICTOR_PID:-}" "${BACKEND_PID:-}" "${DECISION_PID:-}" "${UI_PID:-}" 2>/dev/null || true

  (cd BookService && docker compose down --remove-orphans) || true
  (cd LoadBalancerSystem && docker compose down --remove-orphans) || true
}
trap cleanup EXIT

echo "Starting containerized services..."

echo "Stopping bookservice..."
(cd BookService && docker compose down --remove-orphans)

echo "Building bookservice..."
(cd BookService && docker compose build)

echo "Starting bookservice..."
(cd BookService && docker compose up -d)

echo "Stopping LoadBalancerSystem..."
(cd LoadBalancerSystem && docker compose down --remove-orphans)

echo "Building LoadBalancerSystem..."
(cd LoadBalancerSystem && docker compose build)

echo "Starting LoadBalancerSystem..."
(cd LoadBalancerSystem && docker compose up -d)

echo "Starting predictor service..."
(cd PredictionSystem && python run.py) &
PREDICTOR_PID=$!

echo "Starting backend..."
(cd BackendSystem && python run.py) &
BACKEND_PID=$!

echo "Starting decision maker..."
(cd DecisionMakerSystem && python run.py) &
DECISION_PID=$!

echo "Starting UI..."
(cd UI && python3 -m http.server 8005) &
UI_PID=$!

echo "UI available at http://localhost:8005"

wait