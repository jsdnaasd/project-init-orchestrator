# Project Init Orchestrator 发布文案

## 一句话介绍

让 Codex 在写代码前先建立目标、规格、边界和证据，并用可执行检查守住这些规则。

## 正式介绍

`Project Init Orchestrator` 是一个面向 Codex 的项目初始化与多 Agent 治理 Skill。

很多 AI 编程项目的问题不是 Agent 不会写代码，而是项目启动和执行过程缺少约束：需求没问清楚就开工，目标只存在聊天记录里，子 Agent 修改了职责外文件，最后又在缺少测试证据时宣布完成。

这个项目把上述问题组织成一套可持续执行的工程流程：

- 先检查仓库并澄清需求。
- 先审批设计，再完成 `AGENTS.md`、Spec 和任务计划。
- 用 Goal + Loop 状态机持续推进。
- 为每个子 Agent 建立目标、Brief、允许路径和禁止路径。
- 用文件哈希基线审计子 Agent 的实际变更。
- 用 `state.json + events.jsonl + snapshot.md` 保存可恢复的项目上下文。
- 用结构、就绪和完成三类验证门禁阻止过早实现或虚假完成。

它不是只靠提示词要求 Agent “自觉遵守”。v0.2 增加了标准库 Python 执行层，把初始化、状态迁移、日志、上下文快照、路径审计和验收检查变成可运行命令。

## 已验证结果

- 21 个 Pytest 测试覆盖核心 CLI、错误路径、安全安装器和审计防绕过行为，执行层覆盖率达到 93%。
- 10 个确定性行为评测场景覆盖初始化、幂等保护、状态机、路径审计、就绪门禁和上下文恢复。
- 支持 Python 3.10、3.12、3.14 的 GitHub Actions CI。
- 安装更新前自动备份，卸载可恢复。

这些数字只描述仓库中可复现的确定性执行层测试，不扩展为模型准确率或生产可靠性声明。

## 社交平台短文案

我开源了一个 Codex Skill：`Project Init Orchestrator`。

它解决的是 AI 编程项目很容易失控的问题：Agent 太快开始写代码，项目目标、Spec、子 Agent 边界和验收证据却还没准备好。

安装后，Codex 会先检查仓库、追问需求、建立 `AGENTS.md` 和 Spec，再进入 Goal + Loop。每个子 Agent 都有独立 Brief 和路径权限，工作前记录文件基线，返回后自动检查是否修改了禁止路径或职责范围外文件。

项目还会持续保存状态、事件日志和紧凑上下文快照，让长任务换会话后仍能恢复。完成前必须经过结构、就绪和完成三类验证门禁。

GitHub：https://github.com/jsdnaasd/project-init-orchestrator

## 英文短版

Project Init Orchestrator is a Codex-only Skill with an executable governance layer for spec-first project startup, persistent goal/loop state, bounded subagent policies, changed-file audits, context snapshots, and evidence-based completion.

## 推荐标签

`#Codex` `#AIAgent` `#AgenticCoding` `#MultiAgent` `#Python` `#OpenSource`
