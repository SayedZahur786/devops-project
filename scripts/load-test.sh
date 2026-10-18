#!/usr/bin/env bash
# Generate CPU load against the backend to demonstrate HPA scale-out.
# Usage: ./scripts/load-test.sh http://localhost:8000
URL="${1:-http://localhost:8000}"
echo "Generating load against $URL (Ctrl+C to stop). Watch: kubectl get hpa -n hackboard -w"
while true; do
  for i in $(seq 1 50); do
    curl -s "$URL/api/projects" > /dev/null &
  done
  wait
done
