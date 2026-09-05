# CONTAINER-INVESTMENT-ONT Core v0.1

> **定位**：集装箱资产投资与租赁业务语义契约——覆盖资产采购、持有、出租/出售、回款、对账全闭环。
> **v0.2 新增**：单程租赁（ONEWAY）业务模型、SOC 箱东机制、PUC 中间人收费、PLA 协议运量、空箱调运经济、二手箱处置渠道
> **状态**：Candidate v0.2

## 0. 一句话

**集装箱资产投资 = 产权（谁的箱）× 现金流（钱从哪来、到哪去）× 风险（违约/残值/调运）三者平衡的资本密集型经营活动**

**三种业务模式**：
1. **长期租赁**（Long-term Lease）：3-10 年，大客户 $0.70/day，低风险低回报
2. **单程租赁**（ONEWAY Lease）：30-180 天，PUC $50-150/箱，中间人撮合模式
3. **买卖箱**（Container Trade）：30-180 天，新箱/二手箱价差，资产周转模式

## ONEWAY / 箱贸 v0.2 新增实体

| Entity | 说明 |
|--------|------|
| OneWayContract | 起运港/目的港、PUC费率、免箱期、还箱点、单程条款、Off-hire条件 |
| SOCContainer | SOC标识、箱东主体、箱龄、产权状态、可用港口列表 |
| WishList | 承运商、箱型、起运地、目的地、数量、频率、有效期 |
| PLAContract | 协议运量、箱型、港口对、最低箱量、奖惩条款 |
| ContainerOwner | 箱东（SOC 箱产权方） |
| ContainerAgent | 箱代/中间人（撮合ONEWAY交易） |
| PUCMargin | PUC差价（$50-150/箱） |
| OffHireCondition | 单程还箱条件（箱况/地点/时间） |
| EmptyStockPosition | 港口/区域、空箱数量、箱型、可用性、调箱成本 |
| DisposalChannel | 类型（二手市场/拆解/翻新/报废）、渠道方、价格区间、最小起订量 |

## ONEWAY / 箱贸 v0.2 新增关系

| From | Relationship | To | 说明 |
|------|-------------|-----|------|
| ContainerAgent | intermediates | OneWayContract | 箱代撮合箱东与承运商 |
| ContainerOwner | provides | SOCContainer | SOC 箱产权方提供箱子 |
| Carrier | publishes | WishList | 承运商发布箱型/港口需求 |
| Carrier | charters_under | OneWayContract | 承运商按单程协议用箱 |
| OneWayContract | specifies | TradeLane | 单程合同指定起运/目的港对 |
| ContainerAgent | earns | PUCMargin | 箱代赚取 PUC 差价（$50-150/箱） |
| ContainerAsset | off_hires_at | Depot | 单程还箱到指定堆场 |
| ContainerAsset | disposes_via | DisposalChannel | 二手箱通过指定渠道处置 |
| PLAContract | guarantees | MinimumVolume | 协议保证最低箱量 |
| EmptyStockPosition | feeds | RepositionTask | 空箱位置触发调运任务 |
| ContainerOwner | sells_to | ContainerAgent | 箱东将 SOC 箱卖给/委托给箱代 |
| OneWayContract | subject_to | OffHireCondition | 单程合同受还箱条件约束 |

## ONEWAY / 箱贸 v0.2 新增规则

| Rule | Condition → Action |
|------|-------------------|
| PUCMarginFloor | PUC 差价 < $50/箱 → 不建议撮合 |
| SOCRegistration | SOC 箱未经箱东书面登记 → 禁止对外出租/出售 |
| WishListFreshness | WishList 超过 30 天未更新 → 重新索取 |
| OneWayRedelivery | 单程还箱条件不满足 → 触发 Off-hire 违约链 |
| PLAMinVolume | PLA 实际箱量 < 协议最低量 → 触发罚则/重新谈判 |
| EmptyStockRebalancing | 目的港空箱积压 > 90天 → 触发调运/就地处置决策 |
| DisposalChannelApproval | 二手箱处置渠道/价格需 Decision Card + Founder 批准 |
| CarrierKYC | 新承运商需完成制裁筛查+信用评估+历史合作记录 |

## ONEWAY / 箱贸 v0.2 新增函数

| 函数 | 说明 |
|------|------|
| calc_puc_margin | PUCBuy, PUCSell → Margin (USD/箱) |
| calc_oneway_economics | OneWayContract, RepositionCost, OffHireRisk → Net Revenue |
| calc_reposition_cost | OriginPort, DestPort, ContainerType, Distance → Cost |
| calc_pla_economics | PLAContract, ActualVolume, PenaltyClause → Net Revenue |
| calc_disposal_net | DisposalChannel, ContainerAge, MarketPrice → Net Proceeds |
| calc_empty_stock_value | EmptyStockPosition, ContainerType, LocalRent → Opportunity Cost |

## ONEWAY / 箱贸 v0.2 新增事件

| Event | 触发条件 |
|-------|---------|
| WishListReceived | 承运商发布 wish list |
| OneWayContractSigned | 单程租赁合同签署 |
| PUCSettled | PUC 费用结算 |
| SOCBoxTransferred | SOC 箱产权转移 |
| OffHired | 单程还箱完成（Off-hire） |
| PLAVolumeMet | PLA 协议运量达标 |
| DisposalExecuted | 二手箱处置执行 |
| EmptyStockUpdated | 空箱库存位置更新 |

## ONEWAY / 箱贸 v0.2 新增单据

| Document | 说明 |
|----------|------|
| OneWayContract | 单程租赁合同（含起运/目的港/PUC/免箱期/还箱点/Off-hire条件） |
| PLAContract | 协议运量合同（含最低箱量/港口对/奖惩条款） |
| WishList | 承运商箱型需求清单（箱型/港口/数量/频率） |
| PUCSettlementSheet | PUC 结算单（箱代→箱东/承运商） |
| SOCRegistry | SOC 箱产权登记册 |

## ONEWAY / 箱贸 v0.2 新增角色

| Actor | 说明 |
|-------|------|
| ContainerOwner | 箱东（SOC 箱产权方） |
| Carrier | 承运商/班轮公司（马士基/ONE/CMA等） |
| ContainerAgent | 箱代/中间人（撮合ONEWAY交易） |

## 关键实证数据

| 数据 | 值 | 来源 |
|------|-----|------|
| HL ONEWAY PUC (20') | $1.00/天 | Hapag-Lloyd ONEWAY 合作 (E1) |
| HL ONEWAY PUC (40') | $1.80/天 | Hapag-Lloyd ONEWAY 合作 (E1) |
| HL 免箱期 | 90-100 天 | Hapag-Lloyd ONEWAY 合作 (E1) |
| PUC 差价区间 | $50-150/箱 | WorkBuddy 箱贸调研 (E1) |
| 马士基案例1 | 26×20'HC 上海→格但斯克 | ONEWAY Project 2022 (E1) |
| 马士基案例2 | 30×20'HC 尖沙咀→布里斯班 | ONEWAY Project 2022 (E1) |
| 美国接收条件 | 仅 Chicago 收 40' oneway | ONEWAY Project 2022 (E1) |