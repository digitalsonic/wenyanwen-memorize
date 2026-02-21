# Proposal: Fix Quiz Options Issues

## Why

初学测试阶段的选择题存在三个问题：
1. **正确答案总是 A** - 选项没有随机打乱
2. **单释义词只有1个选项** - 没有生成干扰项，无法真正测试
3. **剩余词数量显示错误** - 显示的是 session 剩余量，不是全局剩余量

这些问题降低了测试的有效性，用户体验不佳。

## What Changes

1. **前端测试题生成改进** - 打乱选项顺序，确保正确答案随机分布
2. **单释义处理** - 当词只有1个释义时，从其他词随机抽取干扰项
3. **剩余词数修正** - 使用全局进度统计，而非 session 剩余量

## Capabilities

### Modified Capabilities
- `learning-progress-management`: 修复剩余词数量计算逻辑
- `multi-type-quiz`: 改进初学测试的选择题生成质量

## Impact

- `frontend/src/views/LearnView.vue`: 测试题生成逻辑修改
- `frontend/src/stores/learn.ts`: 可能需要添加获取其他词释义的方法
