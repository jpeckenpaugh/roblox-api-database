#!/usr/bin/env python3
import sys
import os

# Resolve path to the base script inside tools/
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_SCRIPT = os.path.join(SCRIPT_DIR, "tools", "query_api_base.py")

if not os.path.exists(BASE_SCRIPT):
    print(f"Error: Base query script missing at {BASE_SCRIPT}", file=sys.stderr)
    sys.exit(1)

# Forward execution to the base script
os.execv(sys.executable, [sys.executable, BASE_SCRIPT] + sys.argv[1:])
