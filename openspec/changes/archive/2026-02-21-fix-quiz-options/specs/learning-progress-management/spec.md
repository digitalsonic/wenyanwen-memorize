# Spec: Learning Progress - Fix Remaining Count

## MODIFIED Requirements

### Requirement: 初学完成后剩余词数量正确显示

汇总页面显示的剩余词数量应反映全局剩余量（总词库 - 所有已学词数），而非仅当前 session 的剩余量。

#### Scenario: 多次初学后剩余词数递减

- **GIVEN** 词库共有150个词，用户已学20个
- **WHEN** 用户再次学习10个词
- **THEN** 汇总页面显示剩余词数为 120（150 - 30）
- **NOT** 显示为 140 或其他错误值
