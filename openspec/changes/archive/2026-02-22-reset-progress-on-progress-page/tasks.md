# Tasks: Reset Progress on Progress Page

## 1. Backend

- [x] 1.1 在 `review.py` 中添加 `POST /reset-progress` 端点
  - 接收 `user_id` 参数（默认 1）
  - 查询当前用户的当前轮次（cycle）
  - 删除所有 `LearningProgress` 记录 WHERE `user_id = ? AND cycle = ?`
  - 返回删除的记录数量
- [x] 1.2 注册新端点到 API router（router 已在 API 入口文件中注册）

## 2. Frontend API Client

- [x] 2.1 在 `client.ts` 中添加 `resetProgress()` 方法
  - 发送 POST 请求到 `/api/v1/review/reset-progress`
  - 返回类型包含 `deleted_count`

## 3. Frontend Progress View

- [x] 3.1 移除现有的"学新词"和"今日复习"按钮
- [x] 3.2 添加"重置学习进度"按钮
  - 使用警告样式（红色）
  - 点击时显示确认对话框
- [x] 3.3 实现重置逻辑
  - 确认后调用 API
  - 成功后显示提示并刷新进度数据
  - 错误处理

## 4. Verify

- [x] 4.1 后端测试：手动测试 API 端点返回正确的删除数量
- [x] 4.2 前端测试：点击重置按钮，确认后进度归零
- [x] 4.3 取消测试：点击取消不执行任何操作
