## Why

现有系统的间隔重复算法基于分钟级（5分钟→1小时→6小时→1天→2天→4天），不符合中学生"每天学10-15词，周末集中复习"的实际使用场景。需要将复习周期改为天级（1/2/4/7/15/30天），并增加多种题型（卡片、闪卡、选择、判断）以适应不同复习阶段的需求。

## What Changes

- **间隔重复算法重构**：从6级分钟级改为6级天级（1/2/4/7/15/30天）
- **题型系统扩展**：新增卡片、闪卡、判断题三种题型，原有单选题保留
- **数据库模型扩展**：增加题型字段、复习级别字段、一词多义项追踪
- **一词多义聚焦**：每个词记录2-3个核心义项的掌握情况，错误次数驱动复习策略
- **词库扩充**：新增表格中的5个词语（比、鄙、兵、病、乘），每个词含完整义项和例句
- **前端界面新增**：卡片视图、闪卡视图组件

## Capabilities

### New Capabilities

- `day-level-spaced-repetition`: 基于天级的艾宾浩斯遗忘曲线算法
- `multi-type-quiz`: 支持卡片、闪卡、单选、判断四种题型的出题和答题
- `multi-meaning-tracking`: 一词多义项的独立追踪和错误驱动复习
- `word-library-expansion`: 按课程标准扩充词库数据

### Modified Capabilities

- `quiz-generation`: 原有单选题生成逻辑，需支持多种题型
- `review-scheduling`: 原有复习列表查询，需按天级周期和题型筛选

## Impact

**后端：**
- `backend/src/wenyanwen/models.py`: 新增 `QuizType` 枚举，`QuizRecord` 和 `WeakMeaning` 增加题型字段
- `backend/src/wenyanwen/services/spaced_repetition.py`: `INTERVALS` 改为天级，级别1-6对应1/2/4/7/15/30天
- `backend/src/wenyanwen/api/v1/quiz.py`: 实现多题型出题逻辑
- `backend/src/wenyanwen/api/v1/review.py`: 实现按题型和天级周期的复习查询
- `backend/src/wenyanwen/schemas.py`: 扩展请求/响应模型支持新题型
- `backend/data/words.json`: 新增比、鄙、兵、病、乘五个词的数据

**前端：**
- `frontend/src/views/QuizView.vue`: 支持多题型显示
- `frontend/src/views/ReviewView.vue`: 按题型分组显示复习项
- `frontend/src/views/`: 新增 `CardView.vue`（卡片）、`FlashcardView.vue`（闪卡）
- `frontend/src/stores/quiz.ts`: 扩展状态管理支持新题型
- `frontend/src/api/client.ts`: API 调用适配新响应格式

**API 变更：**
- `GET /api/v1/quiz/start`: 返回 `quiz_type` 字段，不同题型数据结构不同
- `POST /api/v1/quiz/submit`: 接收不同题型的答案
- `GET /api/v1/review/list`: 返回按题型分组的复习项
