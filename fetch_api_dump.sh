#!/bin/bash
# Wrapper to invoke python fetch and comparison script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/tools/fetch_api_dump.py"
