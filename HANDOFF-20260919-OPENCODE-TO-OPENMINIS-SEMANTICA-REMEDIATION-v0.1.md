---
title: "HANDOFF — Semantica 工程可信度整改 v1.0 由 OpenMinis 执行"
document_id: HANDOFF-20260919-OPENCODE-TO-OPENMINIS-SEMANTICA-REMEDIATION-v0.1
type: handoff
status: draft
version: v0.1
privacy: internal
owner: Founder
producer: opencode
from_agent: opencode
to_agent: OpenMinis
task_id: SPEC-20260919-SEMANTICA-ENGINEERING-REMEDIATION-v1.0
source: "_agent-inbox/chatgpt-inbox/SPEC-20260919-SEMANTICA-ENGINEERING-REMEDIATION-v1.0.md"
evidence: "_agent-inbox/evidence/semantica-remediation/PR0-BASELINE-RECON-v0.1.json"
next_step: "OpenMinis 执行 PR-0 基线核对；PR-1..PR-5 按 SPEC 依赖顺序推进"
created: 2026-09-19
updated: 2026-09-19
---

# HANDOFF — Semantica 工程可信度整改 v1.0（OpenMinis 执行）

日期：2026-09-19（Asia/Shanghai）
发起：opencode（仅做交接准备，**未修改上游代码**）
接收：OpenMinis（SPEC `proposed_executor`）
范围：把 SPEC `SPEC-20260919-SEMANTICA-ENGINEERING-REMEDIATION-v1.0` 交给 OpenMinis 执行；本文件提供已核对的地面事实、获取代码的路径、环境要求与 PR-0 清单。

---

## 1. 一句话状态

- SPEC 审阅基线 commit 已确认：`35d2a231b992ca1e23c185ace098ded1640f91b6` = 仓库当前 `main` HEAD。
- opencode 已克隆到隔离工作区并**实测复现了 F03**、静态确认了 **F01/F02/F04/F05/F06/F07/F08/F09/F10/F11**。
- 上游代码**零改动**；本地工作树干净；未做任何生产/发布动作。
- 交接物：源码包 + 基线证据 + 本文件 + ACK。

---

## 2. 执行方获取代码（三条路径，任选）

**路径 A — 便携源码包（推荐给 iPad 侧）**
- 文件：`_agent-inbox/artifacts/semantica-remediation/semantica-project-35d2a231.tar.gz`
- sha256：`b2e93354c6a00ef00883cd2a25c01e4a5d4c6fbbc9b4c070ede313a30ef77b18`（见同目录 `SHA256SUMS.txt`）
- 解包后根目录名：`semantica-project-35d2a231/`
- 校验：`shasum -a 256 semantica-project-35d2a231.tar.gz`

**路径 B — Mac 上的固定 checkout（gateway 只读可访问）**
- 路径：`/Users/mac/AKOS/semantica-remediation/v0.1/repo`（位于 gateway `AKOS_RUNTIME_ROOT` 下）
- 注意：gateway 对 AKOS 根的写白名单仅 `config/{intake,dispatcher,runtime}` + `mcporter.json`，**代码目录不在白名单**，不能经 gateway 回写代码。

**路径 C — 执行方自行克隆**
```bash
NO_PROXY="github.com,api.github.com" \
  git clone --depth 1 https://github.com/cliffordzhangcheng/semantica-project
git -C semantica-project rev-parse HEAD   # 必须 == 35d2a231b992ca1e23c185ace098ded1640f91b6
```

> 三选一后请先跑第 3 节校验，再进入 PR-0。

---

## 3. 基线核对（PR-0 第一步，必须先做）

仓库元数据（opencode 已核对）：

| 项 | 值 |
|---|---|
| commit | `35d2a231b992ca1e23c185ace098ded1640f91b6` |
| tree | `526a992c7ef1ba303cee952f37fb31ec46a171a9` |
| author | `dsh-web <dsh-web@minis.local>` |
| date | `2026-09-17 17:17:02 +0800` |
| message | `fix: remediate v0.2 reality grounding defects` |
| tracked files | 107 |
| CI | 无 `.github/**` |

校验命令：
```bash
git rev-parse HEAD          # 35d2a231b992ca1e23c185ace098ded1640f91b6
git rev-parse HEAD^{tree}   # 526a992c7ef1ba303cee952f37fb31ec46a171a9
git ls-files | wc -l        # 107
```
关键文件 sha256 见 `_agent-inbox/evidence/semantica-remediation/PR0-BASELINE-RECON-v0.1.json` 的 `key_file_sha256`。

---

## 4. 环境现状与要求（重要）

opencode 本机实测：

| 组件 | 状态 |
|---|---|
| macOS | 26.6.2 (25G83), x86_64 |
| Python | 3.11.15（system `python3`） |
| uv | 已装（`/Users/mac/.local/bin/uv`） |
| git / gh | 2.54.0 / 已登录 `cliffordzhangcheng` |
| pytest | 9.1.1 |
| **`semantica`（上游包）** | **未安装**（`ModuleNotFoundError`） |
| `faiss-cpu` | 未安装 |
| `torch` | **导入失败**（NumPy 1.x/2.x ABI 不兼容） |

结论：
- **F03 的复现不需要上游依赖**（`akos_projection.py` 纯 stdlib）——已由 opencode 完成。
- **F04 的动态复现、以及任何 E2E，必须先装上游 `semantica` 及其传递依赖**。上游包与 torch/faiss 的可得性本身就是 SPEC §R06 要治理的问题：先单独记录"从全新环境按锁安装"是否可行，不要用降级测试来声称支持。
- SPEC §R06 要求：Python 3.11 为首个基线候选；macOS 与 Minis/Alpine 的 OS/架构/libc/安装路径**分别记录**；不假定 CPU wheel 兼容 Alpine musl。

---

## 5. PR-0 交付清单（映射到已核实的 F 编号）

SPEC §8 PR-0：*确认 HEAD 与运行基线；复现 F02/F03/F04；核对研究缺项*。交付物 = `baseline.md` + 平台清单 + 失败探针 + 交付索引差异。

| 项 | opencode 已给 | 执行方仍需补 |
|---|---|---|
| HEAD / tree / 107 files | ✅ 已核对 | 在目标环境复跑一条命令留证 |
| 平台清单 | ✅ 本机已记 | Minis/Alpine 侧 OS/arch/libc/path 记录 |
| **F02** 契约不一致 | ✅ 静态定位（`run_akos_pipeline.py` 写 `nodes/edges`；`akos_projection.py` 只读 `nodes/edges`；`tests/test_pipeline_compat.py` 断言 `entities/relationships`；`05_build_and_store.py` 打印 `entities/relationships`） | 用 fixture 跑通"同一 06_graph.json 两种读取"的对照 |
| **F03** 假 PASS | ✅ **已实测复现**：喂 `{"entities":[],"relationships":[]}` → `entity_count=0` 仍 `gate_result=PASS`、`ner_f1=0.9091`、`re_f1=0.8`（硬编码在 `akos_projection.py:44-45,74,141-143`） | 保留原始输出为证据（含已生成的 `manifest.yaml`/`metrics.json` 片段） |
| **F04** 导出失败不传播 | ✅ 静态定位（`scripts/06_export.py` 逐格式 try/except，`main()` 无返回，进程恒 0） | 装上游后注入"7 种导出全失败"，证明 `main` 返回 `None`/退出码 0 |
| **F09** 研究缺项 | ✅ 已核：README 声称的 `02,05,06,08,09` 未被跟踪；`baseline-manifest.json` 含仓库外路径（`qdrant_config.yaml`、`deliverable1_*`、`akos-ontology-portal/**`、`semantica-project-clean/**`、mojibake `shared-attachments/<surrogate>/...`）且写 `integrity_check:"PASS"` | 逐条裁定：未提交 / 外部交付 / 不再适用；**禁止造占位文件过完整性门禁** |

其余已核实事实（F01/F05/F06/F07/F08/F10/F11）与代码行号详见证据 JSON，可直接引用为 `baseline.md` 素材。

---

## 6. 执行护栏（来自 SPEC + 治理规则，务必遵守）

- 保留 `source_of_truth=false`；**候选投影不得升为 AKOS 权威事实**；测试通过 ≠ 业务审批。
- 本轮**不引入**图数据库/向量库/模型供应商/微服务/工作流平台；**不重定义领域本体**。
- `04b_entity_resolution.py` 延续 `merge_entities=False` 默认；不许无依据合并同名实体。
- 不得为过门禁删研究证据、造占位文件、改 golden 迎合输出；规则修复导致基线变化须提交**逐例差异**。
- 每个 PR 报告必须含：base/head commit、变更文件、实际命令与退出码、测试结果、未验证项、样例 run manifest、已知限制、回滚方法。
- **写 Obsidian 落点**（治理）：报告 → `_agent-inbox/artifacts/reports/`；ACK → `_agent-inbox/chatgpt-inbox/`；证据 → `_agent-inbox/evidence/<主题>/`；交接 → `_agent-inbox/handoffs/`；日志 → `daily-logs/YYYY-MM-DD/`；登记 → `registry/`。
- 状态机 `draft → review → verified → approved → archived`；**晋升前一律 draft**；不得直接写 `AKOS/` 正式资产（须经 Reviewer + Registry 或 Change Request）。
- 日期用**本地日期（Asia/Shanghai）**；机器时间戳（`generated_at`）可留 UTC。

---

## 7. 已知开放问题（需 Founder/执行方先定）

1. **OpenMinis 如何获取并执行该 checkout？** 三条路径见第 2 节；gateway 的 AKOS 写白名单**不含**本代码目录，因此"经 gateway 回写代码"不可行。若需在 Mac 上落代码，请明确由谁执行 git/文件写。
2. **上游 `semantica` + torch/faiss 从何而来？** 本机未装且 torch 当前 ABI 不兼容；这直接决定 PR-0 F04 与 PR-2/3 E2E 能否跑。
3. **权威目标环境**：macOS 26 x86_64（本机）还是 Minis/Alpine musl？SPEC §R06 要求两者分别记录。

---

## 8. 交接物索引

| 类型 | 路径 |
|---|---|
| 本交接 | `_agent-inbox/handoffs/HANDOFF-20260919-OPENCODE-TO-OPENMINIS-SEMANTICA-REMEDIATION-v0.1.md` |
| 基线证据 | `_agent-inbox/evidence/semantica-remediation/PR0-BASELINE-RECON-v0.1.json` |
| 便携源码包 | `_agent-inbox/artifacts/semantica-remediation/semantica-project-35d2a231.tar.gz` |
| 源码包校验 | `_agent-inbox/artifacts/semantica-remediation/SHA256SUMS.txt` |
| ACK | `_agent-inbox/chatgpt-inbox/ACK-20260919-OPENCODE-SEMANTICA-ENGINEERING-REMEDIATION-TRANSFER-v0.1.md` |
| 本地 checkout | `/Users/mac/AKOS/semantica-remediation/v0.1/repo` |
| daily-log | `_agent-inbox/daily-logs/2026-09-19/opencode.md` |

---

## 9. 交接边界声明

- opencode **只做**：clone/checkout、静态核对、F03 隔离探针、环境盘点、文书落盘。
- opencode **未做**：修改仓库任何跟踪文件、安装/降级依赖、跑上游流水线、建 CI、改 schema、动 UI、改研究目录。
- opencode **未越权**：未新增平行队列/状态机/审批面/Skill 注册表；未把 Semantica 结果写入 AKOS 正式资产。
