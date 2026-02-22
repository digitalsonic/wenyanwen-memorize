# Spec: Reset Learning Progress

## ADDED Requirements

### Requirement: 重置当前轮次的学习进度

系统 MUST 允许用户通过进度页面重置当前轮次的所有学习进度，从头开始学习。

#### Scenario: 点击重置按钮显示确认对话框

- **WHEN** 用户在进度页面点击"重置学习进度"按钮
- **THEN** 系统 SHALL 显示确认对话框，提示用户此操作将删除当前轮次的所有学习记录
- **AND** 对话框 MUST 包含"取消"和"确认重置"两个选项

#### Scenario: 确认重置删除所有当前轮次进度

- **WHEN** 用户在确认对话框中点击"确认重置"
- **THEN** 系统 SHALL 发送 POST 请求到 `/api/v1/review/reset-progress`
- **AND** 后端 MUST 删除当前用户当前轮次的所有 `LearningProgress` 记录
- **AND** 系统 MUST 返回成功响应
- **AND** 前端 SHALL 显示成功提示并刷新进度数据

#### Scenario: 取消重置不执行任何操作

- **WHEN** 用户在确认对话框中点击"取消"
- **THEN** 系统 SHALL 关闭对话框
- **AND** 系统 MUST NOT 执行任何删除操作
- **AND** 学习进度 MUST 保持不变

#### Scenario: 重置后进度归零

- **WHEN** 重置操作完成
- **THEN** 已学词语数量 SHALL 变为 0
- **AND** 已掌握数量 SHALL 变为 0
- **AND** 完成百分比 SHALL 变为 0%
- **AND** 各阶段词语数量中，只有 level 0 的数量 MUST 等于总词数

## REMOVED Requirements

### Requirement: 进度页面移除重复导航按钮

进度页面 MUST NOT 显示与首页重复的"学新词"和"今日复习"按钮。

#### Scenario: 进度页面不显示学新词和今日复习按钮

- **WHEN** 用户访问 `/progress` 页面
- **THEN** 页面底部 MUST NOT 显示"学新词"按钮
- **AND** 页面底部 MUST NOT 显示"今日复习"按钮
- **AND** 系统 MUST 显示"重置学习进度"按钮
