# 简历项目描述

## Project Init Orchestrator

**Codex Skill / AI Agent 工程**

项目简介：设计并开源面向 Codex 的项目初始化与多 Agent 治理 Skill，将需求澄清、Spec-first、Goal/Loop、角色边界、持久化工作状态和完成审计组织为可执行工作流，减少 Agent 在复杂项目中的需求漂移、越界修改和上下文丢失。

技术栈：Codex Skills、Python、Bash、JSONL、Markdown、Pytest、GitHub Actions

技术亮点：

- 可执行工作流：使用标准库 Python 实现项目扫描、幂等初始化、阶段状态机、证据门禁和结构化事件日志，支持项目中断后的状态恢复与持续执行。
- 多 Agent 边界治理：为子 Agent 建立独立目标、Brief、允许/禁止路径和工作日志，通过文件哈希基线与变更审计识别禁止路径及职责范围外修改。
- 持久化上下文：以 `state.json + events.jsonl + snapshot.md` 保存目标、阶段、决策、阻塞和验证证据，在保留完整事件流的同时生成紧凑上下文快照。
- 工程质量：提供安全备份安装、可恢复卸载、21 个 Pytest 自动化测试、93% 执行层覆盖率、GitHub Actions CI 和 10 个可重复行为评测场景。

## 使用数字的规则

可以写入“10 个行为评测场景全部通过”，因为该结果可由 `python3 scripts/run_evaluations.py` 复现。不要把本地确定性场景扩写为模型准确率、生产可用性或真实并发 Agent 成功率。

只有在新增对照实验后，才能写“降低人工干预”“提升任务准确率”“降低 Token 成本”等效果型结论。
