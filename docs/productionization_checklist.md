# 生产化改造 Checklist + 分阶段 PR 计划

## 目标
将当前“可运行”链路升级为“可观测、可恢复、安全可控、可持续迭代”的生产化系统。

## 总体 Checklist

### 编排与状态
- [x] 会话上下文接入主链路（带 recent history）
- [ ] 多轮上下文摘要（压缩历史，控制 token）
- [ ] Planner/Executor 增加 step 级循环（plan -> execute -> observe -> replan）
- [x] 幂等键（session_id + idempotency_key）防重复执行（进程内缓存版）

### 执行可靠性
- [x] 脚本执行重试策略（可配置重试次数 + 退避）
- [ ] 统一超时策略（planner/executor/script 分层）
- [ ] 失败补偿策略（回滚或补偿动作）
- [ ] 执行队列与并发上限

### 安全治理
- [x] action 格式白名单校验（已完成）
- [x] scripts 路径边界校验（已完成）
- [ ] 进程资源限制（CPU/内存）
- [ ] 不同 skill 的权限沙箱配置

### API 与错误契约
- [x] response type 兜底映射（非法 type 自动降级 JSON）
- [x] 统一 trace_id 透传到响应
- [x] 全局异常中间件（标准 error schema）
- [ ] 对外错误码文档

### 可观测性
- [x] trace_id 基础打点
- [x] 结构化日志（plan/execution/latency）
- [ ] 指标埋点（成功率、超时率、平均耗时）
- [ ] 审计日志（脚本执行输入输出摘要）

### 测试与发布
- [ ] 真实 LLM + 真实技能脚本的冒烟回归
- [ ] 回放测试集（固定输入、断言稳定输出结构）
- [ ] 灰度发布与回滚开关

## 分阶段落地 PR 计划

## P0（本周，止血与稳定）
**目标：** 保障主链路稳定、出问题可定位。

**PR-1: 会话上下文与 trace 链路**
- 编排层接收 `context`，透传 `trace_id`
- API 层加载 recent history 并传给 orchestrator
- 响应结构回传 `trace_id`

**PR-2: API 错误兜底**
- MessageType 非法值兜底到 JSON
- 统一错误内容最小契约（status/message/error_code）

> 本次已开始执行并完成 PR-1/PR-2 的首批改造。

## P1（1~2 周，可靠性增强）
**目标：** 提升复杂任务成功率与执行稳定性。

**PR-3: Planner 循环编排**
- 增加多步规划状态机
- 支持中间观察结果驱动 replan

**PR-4: Executor 可靠性策略**
- 重试 + 退避
- 并发限制与队列
- 任务幂等去重

**PR-5: 可观测性接入**
- 结构化日志
- 分层耗时指标

## P2（2~4 周，安全与规模化）
**目标：** 满足生产安全和规模化治理要求。

**PR-6: 脚本沙箱与资源控制**
- skill 级权限模型
- 资源配额（CPU/内存）

**PR-7: 发布与治理**
- 灰度/回滚
- 错误码与 runbook 文档
- 端到端回放测试体系

