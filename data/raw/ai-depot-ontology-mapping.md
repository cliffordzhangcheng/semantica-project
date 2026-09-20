---
created: 2026-08-08
document_id: ONTO-AI-DEPOT-001
domain: Container Depot / Yard Operations
owner: Founder
project: AI-Depot
status: Candidate
title: AI-Depot Ontology Mapping v0.1
type: ontology_mapping
version: v0.1
---

# AI-Depot Ontology Mapping v0.1

## Objective

建立集装箱场站行业的最小可用 Ontology，为 AI Agent、Industry
Intelligence 和 AI Transformation Opportunity Mapping 提供语义基础。

目标：

Industry Ontology → Business Process Model → AI Agent Opportunity →
Pilot Use Case

------------------------------------------------------------------------

# 1. Core Entities

## Business Actors

  Entity              Description
  ------------------- -------------
  Depot               集装箱堆场
  Customer            客户
  Shipping Line       船公司
  Freight Forwarder   货运代理
  Carrier             承运商
  Driver              司机
  Staff               场站人员

## Physical Resources

  Entity           Description
  ---------------- -------------
  Container        集装箱
  Container Type   箱型
  Yard Slot        堆位
  Truck            卡车
  Equipment        设备

## Business Objects

  Entity             Description
  ------------------ -------------
  Booking            预约
  Order              订单
  Gate Transaction   进出场交易
  Inspection         验箱
  Invoice            账单
  Damage Claim       损坏索赔

------------------------------------------------------------------------

# 2. Relationships

Container located_at Depot

Container stored_at Yard Slot

Truck transports Container

Customer owns Container

Shipping Line manages Container

------------------------------------------------------------------------

# 3. Business Events

事件是 AI Agent 理解业务动态的基础。

## Container Lifecycle

Empty Container Released → Gate In → Inspection → Stored → Booked → Gate
Out → Returned

Key Events:

-   Gate In
-   Gate Out
-   Inspection Completed
-   Damage Reported
-   Storage Expired
-   Billing Triggered

------------------------------------------------------------------------

# 4. Business Rules

Example:

## Free Time Expired

Condition: Container stays longer than allowed free days.

Action: Calculate storage fee and notify customer.

## Damage Detected

Condition: Inspection result indicates damage.

Action: Create damage claim workflow.

------------------------------------------------------------------------

# 5. AI Agent Opportunity Mapping

  Business Area      Agent Opportunity
  ------------------ ----------------------------
  Container Status   Container Tracking Agent
  Gate Transaction   Yard Operation Agent
  Yard Slot          Yard Optimization Agent
  Inspection         Damage Assessment Agent
  Invoice Rules      Billing Agent
  Customer History   Service Intelligence Agent

------------------------------------------------------------------------

# 6. Data Requirements

Potential sources:

-   Depot Management System
-   Yard Management System
-   ERP
-   Billing System
-   Booking System
-   Gate System
-   IoT Data

------------------------------------------------------------------------

# 7. Governance

Status:

Candidate

Rules:

-   不作为正式 AKOS Knowledge Object。
-   等待真实业务验证。
-   不把推断当事实。
-   保留 Evidence 来源。

------------------------------------------------------------------------

# 8. Next Actions

1.  与 Forwarder 行业 Ontology 对比。
2.  建立 Logistics Ecosystem Ontology。
3.  映射 AI Agent Opportunity。
4.  结合真实场站流程验证。
5.  后续通过 Obsidian MCP 接入治理。
