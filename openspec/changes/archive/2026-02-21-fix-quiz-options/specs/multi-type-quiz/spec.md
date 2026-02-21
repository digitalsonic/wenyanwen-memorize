# Spec: Multi-Type Quiz - Fix Options

## MODIFIED Requirements

### Requirement: 初学测试选项随机打乱

初学测试的选择题，选项顺序必须随机打乱，确保正确答案不会固定在某个位置。

#### Scenario: 生成测试题时选项被打乱

- **WHEN** 用户完成初学进入测试阶段
- **THEN** 每道题的选项顺序是随机打乱的
- **AND** 正确答案在 A/B/C/D 位置的概率大致相等

### Requirement: 单释义词条目生成干扰项

当词条只有1个释义时，需要从其他词条随机选取释义作为干扰选项。

#### Scenario: 单释义词生成4个选项

- **WHEN** 生成测试题的词条只有1个释义
- **THEN** 从其他词的释义中随机选取3个作为干扰项
- **AND** 最终生成4个选项（1个正确 + 3个错误）
- **AND** 选项顺序随机打乱

#### Scenario: 多释义词正常生成选项

- **WHEN** 词条有多个释义（≥2个）
- **THEN** 使用该词的其他释义作为干扰项
- **AND** 不足3个干扰项时，从其他词补充
- **AND** 最终至少生成3个选项
- **AND** 选项顺序随机打乱

## MODIFIED Requirements

### Requirement: 剩余词数量显示全局进度

初学完成后显示的剩余词数量应反映全局剩余量，而非当前 session 剩余量。

#### Scenario: 完成初学后显示正确剩余词数

- **WHEN** 用户完成一批词的初学（如20个词）
- **THEN** 汇总页面显示的剩余词数量 = 总词库 - 所有已学词数
- **NOT** 显示当前 session 的剩余量

#### Scenario: 累计学习进度更新

- **WHEN** 用户提交初学完成
- **THEN** 全局已学词数增加本次学习的词数
- **AND** 后续获取的 session 中 remaining_count 正确反映全局剩余
