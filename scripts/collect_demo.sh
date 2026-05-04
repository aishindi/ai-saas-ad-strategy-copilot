#!/usr/bin/env bash
# simple demo script to call backend and save response
mkdir -p demos
curl -s -X POST "http://127.0.0.1:8000/ask" -H "Content-Type: application/json" \
  -d '{"query":"We have a $50,000 Q3 budget for a B2B SaaS launch. How should we allocate it across platforms?","model_name":"mistral"}' \
  | jq '.' > demos/demo_response.json
echo "Saved demos/demo_response.json"