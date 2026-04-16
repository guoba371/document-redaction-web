#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
URL="http://127.0.0.1:5000"

cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "未找到 python3，请先安装 Python 3。"
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "正在创建虚拟环境..."
  python3 -m venv "$VENV_DIR"
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "虚拟环境创建失败，请检查本机 Python 配置。"
  exit 1
fi

echo "正在安装或校验依赖..."
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r "$ROOT_DIR/requirements.txt"

echo "正在启动 Web 脱敏工具..."
echo "访问地址: $URL"

if command -v open >/dev/null 2>&1; then
  (
    sleep 2
    open "$URL" >/dev/null 2>&1 || true
  ) &
fi

exec "$PYTHON_BIN" "$ROOT_DIR/app.py"
