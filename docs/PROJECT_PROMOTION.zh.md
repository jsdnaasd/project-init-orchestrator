# Project Init Orchestrator 宣传文案

## 一句话介绍

`Project Init Orchestrator` 是一套面向 Codex、Claude Code 和多 Agent 编程场景的项目启动工作流，让 AI Agent 在写代码之前，先把目标、范围、规范、协作边界和工作日志建立好。

## 项目定位

很多 AI 编程项目不是失败在代码能力，而是失败在启动阶段：

- 需求还没问清楚，Agent 就开始写代码。
- 没有 `AGENTS.md`，每个 Agent 都按自己的理解行动。
- 没有 spec，验收标准只能靠聊天记录回忆。
- 子 Agent 职责不清，互相覆盖、重复劳动、越界修改。
- 工作日志缺失，项目进展不可追踪。
- 用户每一步都要手动催促，Agent 没有持续推进的 loop。

`Project Init Orchestrator` 要解决的就是这些问题。它不是一个普通模板，而是一套让 Agent 先建立秩序、再开始执行的工作流。

## 它能做什么

安装后，使用者可以在 Codex 或 Claude Code 中直接触发项目初始化流程：

```text
Use $project-init-orchestrator to initialize this project.
```

或：

```text
/project-init-orchestrator initialize this project
```

触发后，主 Agent 会按顺序完成：

1. 建立项目 goal。
2. 启用持续 loop。
3. 调用或模拟 brainstorming 流程，追问项目细节。
4. 创建 `AGENTS.md`。
5. 创建项目 spec。
6. 创建任务计划。
7. 创建主 Agent 和子 Agent 工作日志。
8. 为每个子 Agent 写清楚 brief 和边界。
9. 通过日志和任务表协调多个 Agent。
10. 在完成前做逐项 completion audit。

## 适合谁

这个项目适合：

- 经常用 Codex 或 Claude Code 开新项目的人。
- 希望 Agent 更自主推进，而不是每一步都等用户指挥的人。
- 想让多个子 Agent 协作，但又担心它们越界的人。
- 想把 AI 项目的需求、决策、任务和验收标准沉淀成文档的人。
- 想建立一套可复用 AI 项目启动规范的团队或个人开发者。

## 核心亮点

### 1. 先规范，再开发

工作流强制要求 Agent 在实现前先完成 goal、`AGENTS.md`、spec、任务计划和边界定义。这样项目不会一开始就失控。

### 2. 主 Agent 负责编排

主 Agent 不只是写代码，而是负责调度、拆解、检查、整合和验收。它会管理子 Agent 的任务边界，避免多个 Agent 各干各的。

### 3. 子 Agent 不再越界

每个子 Agent 都必须有自己的 brief，里面写明：

- 目标是什么。
- 可以改哪些文件。
- 不能碰哪些文件。
- 要输出什么。
- 要怎么验证。
- 要把工作记录到哪里。

### 4. 工作日志让协作可追踪

主 Agent 和子 Agent 都必须写 work log。项目进展、关键决策、阻塞、交接和验证证据都会被记录下来，不再散落在聊天上下文里。

### 5. Goal + Loop 让项目持续推进

工作流会要求 Agent 建立 goal，并进入循环执行模型：

```text
clarify -> design -> document -> plan -> execute -> verify -> review -> continue
```

这意味着项目细节收集完成后，Agent 不应该每一步都等用户推一下，而是持续推进，直到完成或遇到真正需要用户决策的阻塞。

### 6. 双平台支持

第一版同时支持：

- Codex Skill
- Claude Code command
- 共享项目模板
- 一键安装脚本

未来也可以扩展到更多 Agent 编程环境。

## 推荐宣传语

### 中文短版

让 Codex 和 Claude Code 在写代码前先学会“立规矩”。

### 中文正式版

`Project Init Orchestrator` 是一套面向 AI 编程项目的初始化工作流。它让主 Agent 在正式开发前自动建立 goal、`AGENTS.md`、spec、任务计划、子 Agent 边界和工作日志，从而让多 Agent 协作更清晰、更可控、更可追踪。

### 英文短版

Start every AI coding project with goals, specs, boundaries, logs, and proof.

### GitHub About

A dual-platform Codex Skill and Claude Code command for disciplined AI project initialization, bounded subagent collaboration, work logs, and goal-driven execution loops.

## 示例发布文案

我做了一个小工具：`Project Init Orchestrator`。

它解决的是 AI 编程里很常见的问题：Agent 太快开始写代码，但项目目标、边界、spec、子 Agent 分工和验收标准都还没建好。

这个项目提供一套可复用工作流，支持 Codex Skill 和 Claude Code command。触发后，主 Agent 会先帮项目创建 `AGENTS.md`、spec、任务计划、工作日志和子 Agent brief，然后再进入持续 loop，负责调度、检查、整合和验收。

简单说，它让 AI Agent 在动手之前先建立项目秩序。

适合经常用 Codex / Claude Code 开项目、希望多 Agent 协作更稳定、希望项目过程可追踪的人。

## 项目价值

`Project Init Orchestrator` 的价值不在于替代 Agent 写代码，而在于让 Agent 写代码之前先具备工程组织能力。

它把“项目启动”变成一个标准化流程：

- 目标明确。
- 需求可追踪。
- 边界清晰。
- 职责可控。
- 过程有日志。
- 完成有证据。

这会让 AI 编程项目更适合长期维护，也更适合多人、多 Agent、复杂需求的场景。
