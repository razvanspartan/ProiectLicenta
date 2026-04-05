#!/bin/bash
set -e  # stop on error

echo "Stopping services..."
docker compose down --remove-orphans

echo "Building services..."
docker compose build

echo "Starting services..."
docker compose up -d bookservice loadbalancer

# Start services and track PIDs
echo "Starting predictor service..."
(cd PredictionSystem && python run.py) &
PREDICTOR_PID=$!

echo "Starting backend..."
(cd BackendSystem && python run.py) &
BACKEND_PID=$!

echo "Starting decision maker..."
(cd DecisionMaker && python run.py) &

echo "Starting UI..."
(cd UI && python3 -m http.server 8005) &
UI_PID=$!

echo "UI available at http://localhost:8005"

cleanup() {
  echo "Stopping everything..."
  kill $PREDICTOR_PID $BACKEND_PID $UI_PID 2>/dev/null
  docker kill $(docker ps -q)
}
trap cleanup EXIT

wait