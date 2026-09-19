# Semantica Ontology Project

**物流现实本体知识库平台**

## 📁 项目结构

```
semantica-project/
├── src/semantica_workbench/    # 正式工程代码
│   ├── cli.py                 # 统一CLI入口
│   ├── pipeline/              # 管道编排
│   ├── evaluation/            # 闸门、指标、证据
│   ├── adapters/              # legacy适配
│   └── projection/            # 投影生成
├── scripts/                   # 兼容入口（薄包装）
├── tests/                     # 自动化测试
├── schemas/                   # 契约定义
├── docs/                      # 文档
├── data/                      # 原始语料
│   ├── raw/                   # 未处理数据
│   └── processed/             # 清洗后数据
├── outputs/                   # 生成物（gitignored）
│   ├── graphs/                # 图数据
│   ├── reports/               # 报告
│   └── metrics/               # 指标
├── research/archive/          # 历史研究归档
├── pyproject.toml            # 唯一依赖源
└── README.md
```

## 🚀 快速开始

### 安装
```bash
pip install -e .
```

### 运行
```bash
# 正式入口
python -m semantica_workbench.cli

# 兼容入口
python scripts/run_gates.py
```

## 📊 门禁状态

| 闸门 | 验证内容 | 状态 |
|------|----------|------|
| G0 | Corpus目录存在 | 必填 |
| G1 | Schema文件存在 | 必填 |
| G2 | Ontology文件存在 | 必填 |
| G3 | Evidence文件存在 | 必填 |
| G4 | Claims文件存在 | 必填 |
| G5 | 测试全部通过 | 必填 |
| G6 | 无BOOKED状态 | 必填 |
| G7 | Founder决策 | 最终 |

## 🧪 测试
```bash
pytest tests/ -v
```

## 📝 依赖管理

- **主依赖**: `pyproject.toml`
- **分组**: runtime / dev / optional(research)
- **禁止**: requirements.txt（已删除）

## 🔒 安全与合规

- 研究产物归档在 `research/archive/`
- 生成物在 `outputs/`（gitignored）
- 凭证和环境变量不在仓库中