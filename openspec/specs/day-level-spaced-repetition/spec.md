## ADDED Requirements

### Requirement: 天级间隔重复算法
系统 SHALL 实现基于天级的艾宾浩斯遗忘曲线算法，支持 6 个复习级别，间隔分别为 1/2/4/7/15/30 天。

#### Scenario: 初学完成设置首次复习时间
- **WHEN** 用户完成一个词的初次学习
- **THEN** 系统设置 `current_level = 1`，`next_review_at = 当前时间 + 1天`

#### Scenario: 答对升级到下一级别
- **WHEN** 用户在当前级别答对题目
- **THEN** 系统将 `current_level` 加 1，按间隔表计算 `next_review_at`

#### Scenario: 最高级别答对完成本轮
- **WHEN** 用户在第 30 天级别（level=6）答对题目
- **THEN** 系统标记 `is_mastered = true`，该词在本轮学习中完成

#### Scenario: 答错保持当前级别
- **WHEN** 用户答错题目
- **THEN** 系统将 `error_count` 加 1，`current_level` 保持不变

#### Scenario: 间隔时间计算
- **WHEN** 系统需要计算下次复习时间
- **THEN** 使用以下间隔表：
  - level 1: +1天
  - level 2: +2天
  - level 3: +4天
  - level 4: +7天
  - level 5: +15天
  - level 6: +30天

---

### Requirement: 多轮学习循环
系统 SHALL 支持用户完成一轮学习后开始新一轮循环，每轮包含所有词的完整学习过程。

#### Scenario: 新用户开始第一轮学习
- **WHEN** 新用户首次使用系统
- **THEN** 系统创建 `cycle = 1` 的学习进度记录

#### Scenario: 本轮100%完成后开启新一轮
- **WHEN** 当前轮次所有词都标记为 `is_mastered = true`
- **THEN** 系统创建新的 `cycle + 1` 轮次记录，所有词进度重置

#### Scenario: 查询当前学习进度
- **WHEN** 用户查看学习进度
- **THEN** 系统显示当前轮次、已学词数、总词数、完成百分比

---

### Requirement: 到期复习查询
系统 SHALL 查询所有 `next_review_at <= 当前时间` 且属于当前轮次的词。

#### Scenario: 获取今日复习列表
- **WHEN** 用户请求今日复习列表
- **THEN** 系统返回所有到期的词，按复习级别分组显示

#### Scenario: 无到期复习时
- **WHEN** 用户请求复习列表但无到期词
- **THEN** 系统返回空列表，提示"暂无到期复习"

---

### Requirement: 答错当场重做
系统 SHALL 在一轮答题结束后，将答错的题目重新出题，直到用户答对。

#### Scenario: 答错题目重做
- **WHEN** 用户一轮答题中有错题
- **THEN** 系统在正常题目结束后，单独展示错题让用户重做

#### Scenario: 错题连续重做直到答对
- **WHEN** 用户重做错题时仍答错
- **THEN** 系统继续展示该题，直到用户答对为止

#### Scenario: 错题不计入新进度
- **WHEN** 用户重做错题
- **THEN** 系统只记录答对结果，不重复计算复习间隔时间
