#!/bin/bash

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

chmod +x "$ROOT_DIR/start.sh"
exec "$ROOT_DIR/start.sh"
