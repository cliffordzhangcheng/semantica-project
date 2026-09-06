# Semantica Pipeline GitHub 更新清单

---
created: 2026-09-06
updated: 2026-09-06
tags:
  - semantica
  - AKOS
  - GitHub
  - commit
---

## 当前仓库状态

**本地仓库**: `/var/minis/workspace/semantica-project-clean/`
**远程**: origin/main (需推送)
**最新提交**: `d6eeee7 v0.3: RE enhancement (27→93 edges) + UI overhaul + diagnosis engine + market truth table`

---

## 未提交文件

### 修改的文件 (Modified)
```
M audit_log.jsonl       # 审计日志更新
M gold_set.py           # Gold set 扩展（新增实体/关系）
M webui/index.html      # UI 界面更新
```

### 新增文件 (Untracked)
```
?? 04b_entity_resolution.py    # 实体解析模块（新增）
?? akos_projection.py          # AKOS 投影脚本（新增）
?? review_queue.py             # 审查队列管理（新增）
?? config/akos_domain_ontology.yaml   # 领域本体配置
?? config/ontology_aliases.yaml       # 本体别名映射
?? akos_projection/
   ├── entities.jsonl              # 抽取实体
   ├── evidence.jsonl              # 证据链
   ├── graph_projection.json      # 图投影
   ├── lineage.jsonl              # 血缘追踪
   ├── manifest.yaml              # 包清单
   ├── metrics.json               # 评估指标
   ├── ontology.yaml              # 本体定义
   ├── ontology_aliases.yaml      # 本体别名
   ├── relations.jsonl            # 关系抽取
   └── review_queue.jsonl         # 待审查队列
```

---

## 可更新的 Obsidian 笔记

### 新增/更新的语料笔记

| 笔记文件 | 内容 | 来源 |
|---------|------|------|
| `COSMOS WHALES ONEWAY Leasing 沟通.md` | Maersk/Hapag-Lloyd ONEWAY 合作时间线、可用走廊表格 | COSMOS WHALES 邮箱 |
| `越南 Container Sales 谈判记录.md` | ONE Line GCAM 越南业务谈判、SOC Update Issue | COSMOS WHALES 邮箱 |
| `ONEWAY Project 2022.md` | 项目框架文档（已有，需更新） | Obsidian Vault |
| `Hapag-Lloyd ONEWAY 合作.md` | HL 周度报价流程、评估标准 | COSMOS WHALES 邮箱 |

---

## GitHub 访问问题

**链接**: https://github.com/copilot/share/c01b1180-4a40-8e14-8110-984344016943

**状态**: 需要登录才能查看

**解决方案**:
1. 在系统 Chrome 中打开链接并登录 GitHub
2. 或者将本地仓库推送到 GitHub
3. 或者导出为 ZIP 分享

---

## 下一步行动

### 立即执行
- [ ] 推送当前修改到 GitHub (`git push`)
- [ ] 提交新文件 (`git add .` + `git commit`)

### 待用户确认
- [ ] GitHub 账号信息（如需我推送）
- [ ] 是否需要更新某个特定分支
- [ ] 是否需要创建 release tag

### 后续任务
- [ ] 继续从邮箱提取语料（NYK Total Loss 邮件）
- [ ] 更新 Semantica 领域本体（CI-ONT + Logistics）
- [ ] 运行 entity resolution 验证

---

## 技术栈备注

**Semantica 版本**: 0.6.5
**AKOS 适配器**: P0 契约已实现
**评估结果**: NER F1=0.9091, RE F1=0.8000
**图谱规模**: 696 entities / 93 relations (enhanced from 27)
