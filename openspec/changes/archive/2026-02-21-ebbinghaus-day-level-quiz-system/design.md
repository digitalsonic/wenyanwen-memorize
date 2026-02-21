## Context

现有系统使用分钟级间隔重复算法（5分钟→1小时→6小时→1天→2天→4天），不适合中学生"每天学一点"的使用模式。需要重构为天级系统（1/2/4/7/15/30天），并支持多种题型。

**当前状态：**
- 后端框架已搭建（FastAPI + SQLModel + SQLite）
- 前端框架已搭建（Vue 3 + Pinia + TypeScript）
- 词库数据文件存在但只有示例数据
- API 骨架存在但核心逻辑未实现

**约束条件：**
- H5 场景，无推送能力，用户主动触发
- 约150个词，每轮循环需全部学完
- 词库数据为静态 JSON，后期由教师补充

## Goals / Non-Goals

**Goals:**
- 实现天级间隔重复算法（1/2/4/7/15/30天）
- 支持四种题型：卡片、闪卡、单选题、判断题
- 支持多轮学习循环，每轮独立追踪进度
- 记录错误次数供后续强化功能使用
- 答错题目当场重做直到答对

**Non-Goals:**
- 用户认证系统（暂使用 user_id=1）
- 基于错误次数的智能题目生成（错误次数仅记录）
- 完整的150词词库（先用示例词实现功能）
- 社交功能、排行榜等

## Decisions

### Decision 1: 数据库模型设计

使用 `LearningProgress` 表替代原有的 `QuizRecord` 和 `WeakMeaning`，新增 `cycle` 字段支持多轮循环。

```python
class LearningProgress(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int
    word_id: str              # 对应 words.json 中的 word.id
    cycle: int                # 第几轮循环（1, 2, 3...）

    current_level: int        # 0=初学, 1-6=对应各复习级别
    error_count: int          # 当前级别累计错误次数
    is_mastered: bool         # 本轮是否已通关

    last_review_at: datetime | None
    next_review_at: datetime | None

    created_at: datetime
    updated_at: datetime
```

**理由：** 用户+词+周期三元组唯一标识一条学习记录，支持多轮独立追踪。

### Decision 2: 题型与级别映射

| current_level | 题型 | quiz_type |
|---------------|------|-----------|
| 0 | 卡片 | card |
| 1 | 单选 | multiple_choice |
| 2 | 判断 | true_false |
| 3 | 单选 | multiple_choice |
| 4 | 判断 | true_false |
| 5 | 单选 | multiple_choice |
| 6 | 闪卡+单选 | flashcard + multiple_choice |

**理由：** 简化逻辑，题型由级别固定决定，无需额外配置。

### Decision 3: 词库 JSON 结构

```json
{
  "words": [
    {
      "id": "word_001",
      "word": "顾",
      "type": "实词",
      "pinyin": "gù",
      "meanings": [
        {
          "id": "m_001_01",
          "definition": "回头看",
          "examples": [
            {"sentence": "元方入门不顾", "source": "世说新语•陈太丘与友期行", "level": "core"}
          ]
        }
      ],
      "mnemonics": "元方回头顾，刘备三顾庐"
    }
  ]
}
```

**理由：** 扁平化结构，易于读取和编辑；每个义项有独立 id 便于后续扩展义项级追踪；例句如果出自非考试篇目，则level为secondary，可以更多地关注考试篇目里的释义。

### Decision 4: 答错重做机制

答题流程：
1. 用户提交所有答案
2. 系统判断对错，记录结果
3. 如果有错题，单独返回错题列表
4. 用户逐题重做，直到全对
5. 错题重做只更新正确记录，不重复计算复习间隔

**理由：** 保持复习时间计算的简洁性，重做只是为了强化记忆。

### Decision 5: 前端路由设计

| 路径 | 组件 | 功能 |
|------|------|------|
| / | QuizView | 答题入口，引导学新词或复习 |
| /learn | LearnView | 学新词（卡片模式） |
| /review | ReviewView | 今日复习（多题型） |
| /progress | ProgressView | 学习进度 |

**理由：** 分离学新词和复习的流程，体验更清晰。

### Decision 6: 间隔时间计算

使用固定间隔表，级别1-6对应1/2/4/7/15/30天：

```python
INTERVALS: dict[int, timedelta] = {
    1: timedelta(days=1),
    2: timedelta(days=2),
    3: timedelta(days=4),
    4: timedelta(days=7),
    5: timedelta(days=15),
    6: timedelta(days=30),
}
```

**理由：** 固定间隔简单可靠，符合艾宾浩斯曲线的核心思想。

## Risks / Trade-offs

**Risk:** 用户可能连续多天不使用，导致大量词积压到期
**Mitigation:** 复习列表不限制数量，但按级别分组展示，用户可分批完成

**Risk:** 一轮150词，30天周期意味着几个月才能完成一轮
**Mitigation:** 显示进度百分比，让用户有成就感；支持调整每日新词数量

**Trade-off:** 词级别追踪（而非义项级别）简化了实现，但无法精准定位薄弱义项
**Acceptance:** 当前阶段以词级别追踪为主，后续可扩展

## Migration Plan

1. **后端：**
   - 更新 `models.py`：新增 `LearningProgress`，`QuizType` 枚举
   - 更新 `spaced_repetition.py`：修改间隔为天级
   - 实现 `quiz.py` 和 `review.py` 的核心逻辑
   - 更新 `schemas.py`：支持新题型

2. **前端：**
   - 新增 `LearnView.vue`（学新词）
   - 新增 `CardView.vue` 和 `FlashcardView.vue` 组件
   - 更新 `ReviewView.vue` 支持多题型
   - 更新 `quiz.ts` store 支持新流程

3. **数据：**
   - 更新 `words.json` 格式
   - 添加示例词语（比、鄙、兵、病、乘）

## Open Questions

1. **新词学习是否需要"跳过"功能？** 用户可能不想学某个词
   - 倾向：暂不实现，保持简单

2. **复习列表是否需要优先级排序？** 错误次数多的优先显示
   - 倾向：暂不实现，按到期时间排序即可

3. **是否需要学习统计页面？** 如"连续学习天数"、"正确率"等
   - 倾向：非本变更范围，后续添加
