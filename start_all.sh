#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

./run_all.sh "$@"

if [ -f server.pid ] && kill -0 "$(cat server.pid)" 2>/dev/null; then
    kill "$(cat server.pid)"
fi
nohup python3 -m http.server 8080 > server.log 2>&1 &
echo $! > server.pid
echo "Web UI: http://localhost:8080/webui/index.html"
