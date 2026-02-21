# Design: Fix Quiz Options

## Context

**当前问题根因：**

1. **选项不打乱** - `LearnView.vue` 直接使用 `card.back.meanings` 作为选项，没有打乱顺序
2. **单释义无干扰** - 前端没有访问其他词释义的途径，无法生成干扰项
3. **剩余数计算** - `learnStore.remainingCount` 返回的是当前 session 的 `remaining_count`，不是全局剩余

**后端已有的能力：**
- `quiz.py:generate_multiple_choice()` 已实现选项打乱和干扰项生成逻辑

## Goals / Non-Goals

**Goals:**
- 选项随机打乱（简单：前端 shuffle）
- 单释义生成干扰项（需要：后端提供或前端获取词库数据）
- 剩余词数正确显示（需要：检查后端 API 返回）

**Non-Goals:**
- 不重构整个学习流程
- 不改变答题反馈逻辑

## Decisions

### Decision 1: 选项打乱 - 前端处理

在 `LearnView.vue` 中生成测试题时，使用 Fisher-Yates shuffle 打乱选项顺序。

**理由：**
- 简单快速，无需后端改动
- 前端生成测试题是临时方案，打乱逻辑也放前端即可

**注意：** 打乱后需要保持 `correct_answer` 的值不变，只是改变选项数组的顺序。

### Decision 2: 单释义干扰项 - 后端 API 支持

**方案 A：前端获取全部词库**
- 优点：简单，前端直接用
- 缺点：传输全部词库数据，浪费带宽

**方案 B：后端提供干扰项生成 API**
- 优点：后端已有逻辑，复用
- 缺点：需要新 API 或修改现有 API

**选择方案 A（前端获取词库）：**
- 词库只有150个词，数据量不大
- 可以在后端 `/quiz/learn` API 返回时附带部分其他词数据
- 或者前端启动时预加载词库

**实际实现：** 简化方案 - 如果释义少于3个，从其他学习的词中随机选取释义作为干扰项（因为用户刚学过这些词，有一定记忆基础）。

### Decision 3: 剩余词数 - 检查后端返回

需要检查 `GET /progress` API 返回的数据结构，确认 `remaining_words` 是全局还是 session 级别。

如果是全局：前端直接用
如果是 session：需要前端累计计算

## Implementation Plan

1. **选项打乱** - `LearnView.vue` 添加 shuffle 函数
2. **单释义处理** - 从本次学习的其他词中随机抽取释义
3. **剩余词数** - 检查并使用正确的数据源
