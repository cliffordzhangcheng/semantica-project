#!/usr/bin/env bash
# run_all.sh — 一键跑通 Semantica 全链路
# 用法: ./run_all.sh

set -euo pipefail

# 进入项目根目录（脚本所在目录的父目录）
cd "$(dirname "$0")"

echo "========================================"
echo "  Semantica Knowledge Graph Pipeline"
echo "========================================"
echo ""

# 加载 .env（如果存在）
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "🔐 已加载 .env 环境变量"
fi

# 检查数据目录
if [ ! -d "data" ] || [ -z "$(ls -A data)" ]; then
    echo "⚠️  data/ 目录为空，请先放入语料文件 (PDF/Word/HTML/JSON/...)"
    echo "   示例: cp /var/minis/attachments/*.pdf data/"
    exit 1
fi

# 依次执行 6 步
steps=(
    "1/6 数据摄取与解析:scripts/01_ingest.py"
    "2/6 数据规范化:scripts/02_normalize.py"
    "3/6 实体抽取:scripts/03_ner.py"
    "4/6 关系抽取:scripts/04_relation.py"
    "5/6 构建图谱 & 存储后端:scripts/05_build_and_store.py"
    "6/6 导出闭环:scripts/06_export.py"
)

for step in "${steps[@]}"; do
    label="${step%%:*}"
    script="${step##*:}"
    echo ""
    echo "=== $label ==="
    python3 "$script"
done

echo ""
echo "========================================"
echo "🎉 全链路执行完成！"
echo "========================================"
echo ""
echo "📦 产物位于 ./outputs/:"
ls -lh outputs/
echo ""
echo "🔍 下一步建议:"
echo "  - 用 Gephi 打开 outputs/06_graph.gexf 做可视化"
echo "  - 用 Neo4j Desktop 导入 outputs/06_graph.sif"
echo "  - 查看 outputs/06_graph.ttl 理解语义结构"