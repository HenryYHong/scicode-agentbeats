#!/bin/bash
# Script to run the SciCode green agent with the correct Python environment

cd "$(dirname "$0")"
source agentbeats_env_311/bin/activate

echo "🚀 Starting SciCode Green Agent..."
echo "Python version: $(python --version)"
echo ""

python scicode_green_agent.py --host localhost --port 9001 --agent-name tau_green_scicode

