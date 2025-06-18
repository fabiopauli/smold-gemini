#!/bin/bash
# Wrapper script for running SmolD tool tests

# Ensure the project directory is in the Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Change to the smold directory
cd smold || { echo "Error: smold directory not found"; exit 1; }

# Run the tests with any provided arguments
python run_tool_tests.py "$@"