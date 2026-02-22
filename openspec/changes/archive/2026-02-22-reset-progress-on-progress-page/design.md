# Design: Reset Progress on Progress Page

## Context

当前 `ProgressView.vue` 在页面底部有两个按钮：
- "学新词" → 跳转到 `/learn`
- "今日复习" → 跳转到 `/`（首页）

这两个按钮在 `HomeView.vue` 中已经存在，造成 UI 冗余。

用户想要通过界面重置学习进度，目前只能通过手动操作数据库实现。

## Goals / Non-Goals

**Goals:**
- 移除进度页面中与首页重复的导航按钮
- 添加重置学习进度功能，允许用户重新开始当前轮次的学习
- 提供确认对话框，防止误操作
- 重置后自动刷新进度显示

**Non-Goals:**
- 不支持选择性重置（如只重置某些等级的词）
- 不影响已完成的历史轮次数据
- 不需要用户认证（当前使用硬编码 user_id = 1）

## Decisions

### Decision 1: 重置操作的实现方式

选择删除当前轮次的所有 `LearningProgress` 记录，而不是将记录的 `current_level` 设为 0。

**理由：**
- 删除记录更干净，不会留下累积的错误计数等无用数据
- 当用户再次学习这些词时，会创建新的进度记录
- 代码更简单，不需要更新多个字段

**实现：**
```python
DELETE FROM learning_progress
WHERE user_id = ? AND cycle = ?
```

### Decision 2: 前端确认对话框

使用浏览器原生 `confirm()` 对话框，而不是自定义模态框组件。

**理由：**
- 当前项目中没有模态框组件
- 原生 `confirm()` 足够简单且可用
- 对于这个低频操作，不需要精美的 UI

未来可以升级为自定义模态框。

### Decision 3: 重置后的用户反馈

重置成功后：
1. 显示 toast 提示"学习进度已重置"
2. 自动调用 `progressStore.fetchProgress()` 刷新数据
3. 用户可以看到进度归零的状态

### Decision 4: API 端点设计

```
POST /api/v1/review/reset-progress
```

返回格式：
```json
{
  "success": true,
  "message": "学习进度已重置",
  "data": {
    "deleted_count": 42  // 删除的记录数
  }
}
```

使用 `APIResponse` schema 保持一致性。

### Decision 5: 按钮样式

"重置学习进度"按钮使用警告色（红色/橙色），与其他操作按钮区分开。

CSS：
```css
background: #f5576c;
color: white;
```
