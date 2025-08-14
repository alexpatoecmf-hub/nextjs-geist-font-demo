#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY="/usr/bin/python3"
HOST="$SCRIPT_DIR/zoe_native_host.py"
"$PY" "$HOST" "$@"
