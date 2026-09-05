# Semantica Knowledge Graph Pipeline on Minis

在 Android + Minis (Alpine Linux) 环境下跑通「数据摄入 → 清洗 → NER → 关系抽取 → 建图 → 存储 → 导出」全链路。

## 📁 项目结构

```
semantica-project/
├── data/              # 原始语料 (PDF/Word/HTML/JSON/TXT...)
├── scripts/           # 6 步核心脚本
│   ├── 01_ingest.py
│   ├── 02_normalize.py
│   ├── 03_ner.py
│   ├── 04_relation.py
│   ├── 05_build_and_store.py
│   └── 06_export.py
├── outputs/           # 所有中间产物与最终导出
├── config/
│   ├── backend.yaml   # 存储后端切换
│   └── ontology.yaml  # 本体定义
├── .env.example       # 环境变量模板
├── requirements.txt   # Python 依赖
├── run_all.sh         # 一键执行
└── .gitignore
```

## 🚀 快速开始

### macOS 笔记本环境

项目原始依赖清单面向 Minis/Alpine Linux。macOS 请使用已验证的 Python 3.11
环境，并把 Semantica 0.6.x 的运行时指向项目脚本：

```bash
cd ~/projects/semantica-project
source /Users/mac/.venvs/semantica/bin/activate
python -m unittest discover -s tests -v
./run_all.sh
```

`scripts/pipeline_compat.py` 负责适配 Semantica 0.6.x 的新模块路径和记录格式。
默认保留原始实体，不自动启用新版模糊去重，避免稀疏元数据导致不相关实体被合并。

### 1. 准备语料
```bash
# 放入 PDF/Word/HTML/JSON 等文件
cp /var/minis/attachments/*.pdf data/
# 或下载测试文件
cd data
curl -sLO "https://www.w3.org/WAI/WCAG21/Techniques/working-examples/PDF/table-example.pdf"
```

### 2. 安装依赖
```bash
# 系统依赖
apk add --no-cache \
  python3 py3-pip \
  py3-numpy py3-pandas py3-scipy py3-networkx \
  py3-matplotlib py3-pillow py3-lxml py3-beautifulsoup4 \
  py3-requests py3-tqdm py3-yaml py3-click

# Python 包
pip install --no-cache-dir -r requirements.txt

# spaCy 中文模型
python3 -m spacy download zh_core_web_sm
```

### 3. 配置环境变量（可选，用于 LLM 模式）
```bash
cp .env.example .env
vi .env  # 填入 DEEPSEEK_API_KEY 等
```

### 4. 一键跑通
```bash
chmod +x run_all.sh
./run_all.sh
```

## ⚙️ 关键配置

### 存储后端切换 (`config/backend.yaml`)
```yaml
# 开发环境：NetworkX (默认，无外部依赖)
backend: "networkx"

# 生产环境：Neo4j
# backend: "neo4j"
# options:
#   uri: "bolt://host:7687"
#   user: "neo4j"
#   password: "$NEO4J_PASSWORD"
```

### NER/Relation 模式选择
通过环境变量控制：
```bash
export NER_MODE=hybrid          # pattern | llm | hybrid
export RELATION_MODE=llm        # pattern | llm | hybrid
export DEEPSEEK_API_KEY=sk-xxx  # LLM 模式必需
```

## 📦 导出格式与下游

| 格式 | 文件 | 适用场景 |
|------|------|----------|
| JSON | `06_graph.json` | 程序处理、API 返回 |
| GraphML | `06_graph.graphml` | Gephi、Cytoscape、NetworkX 读取 |
| GEXF | `06_graph.gexf` | Gephi 可视化 |
| Turtle | `06_graph.ttl` | 语义网、SPARQL 端点 |
| SIF | `06_graph.sif` | Neo4j `LOAD CSV` 批量导入 |
| CSV | `06_nodes.csv` / `06_edges.csv` | 表格分析、Excel、Pandas |

## 🔄 双端同步 (Minis ↔ 笔记本)

使用 Git 同步代码与配置：

```bash
# 笔记本端
cd ~/projects
git clone git@github.com:<你>/semantica-project.git

# Minis 端
cd /var/minis/workspace
git clone git@github.com:<你>/semantica-project.git

# 日常同步别名 (加入 ~/.bashrc)
alias kg-sync='cd ~/projects/semantica-project && git pull --rebase && git add -A && git commit -m "sync $(date +%F_%H:%M)" && git push'
```

## 🛠 常见问题

| 问题 | 解决 |
|------|------|
| `torch` 安装失败 | `apk add py3-torch` |
| `faiss` 缺 `libgomp` | `apk add libgomp` |
| spaCy 模型下载慢 | `pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple` |
| LLM 401 报错 | 检查 `.env` 中 Key 名称大小写 |
| Neo4j 连不上 | 确保宿主机/云端部署，防火墙放行 7687 |

## 📚 参考资料

- Deliverable 1: [Capability Inventory](minis://workspace/deliverable1_capability_inventory.md)
- Deliverable 2: [六大工程实践指南](minis://workspace/deliverable2_semantica_on_minis.md)
- Semantica 官方文档: `https://github.com/semantica-ai/semantica`
- 视频号教程: `https://www.vee.com/video/semantica-intro-series-1`

---

**License:** MIT — 可自由用于学习、研究与商业项目
