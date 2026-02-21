# Tasks: Fix Quiz Options

## 1. 选项随机打乱

- [x] 1.1 在 `LearnView.vue` 中添加 Fisher-Yates shuffle 函数
- [x] 1.2 生成测试题时对选项进行打乱
- [x] 1.3 确保打乱后 `correct_answer` 仍然匹配正确选项

## 2. 单释义干扰项生成

- [x] 2.1 检测单释义词条目（meanings.length === 1）
- [x] 2.2 从本次学习的其他词中随机选取释义作为干扰项
- [x] 2.3 确保干扰项与正确答案不重复

## 3. 剩余词数修复

- [x] 3.1 检查 `learnStore.remainingCount` 的数据来源
- [x] 3.2 检查后端 `/quiz/learn` API 返回的 `remaining_count` 定义
- [x] 3.3 修复剩余词数显示逻辑（使用全局剩余量）

## 4. 测试验证

- [ ] 4.1 测试多义词选项是否随机分布
- [ ] 4.2 测试单释义词是否生成4个选项
- [ ] 4.3 测试剩余词数显示是否正确
