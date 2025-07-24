#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the uv virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Change to the project directory
cd "$SCRIPT_DIR"

# Run pytest
python -m pytest -v "$@"