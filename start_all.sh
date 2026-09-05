#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== 运行知识图谱管线 ==="
./run_all.sh

echo "=== 启动 Web UI 服务器 ==="
# 如果已有服务器在运行，先停止
if [ -f server.pid ] && kill -0 $(cat server.pid) 2>/dev/null; then
    echo "停止旧服务器..."
    kill $(cat server.pid)
    rm -f server.pid server.log
fi

# 启动新服务器
nohup python3 -m http.server 8080 > server.log 2>&1 &
echo $! > server.pid
echo "服务器已启动，PID=$(cat server.pid)"
echo "日志写入 server.log"
echo ""
echo "请在浏览器中打开以下任意地址查看 UI："
echo "  http://localhost:8080/webui/index.html"
echo "  或在同一网络的其他设备上使用："
echo "    http://<Minis设备IP>:8080/webui/index.html"
echo ""
echo "提示："
echo "  - 更新语料后重新运行 ./run_all.sh，然后点击页面的 'Reload Data' 按钮即可查看最新结果"
echo "  - 停止服务器：kill \$(cat server.pid) && rm -f server.pid server.log"