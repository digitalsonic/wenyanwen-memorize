## 1. 数据模型更新

- [x] 1.1 更新 `models.py`：新增 `QuizType` 枚举（card, flashcard, multiple_choice, true_false）
- [x] 1.2 更新 `models.py`：新增 `LearningProgress` 模型（替代原 QuizRecord/WeakMeaning）
- [x] 1.3 更新 `schemas.py`：新增 LearningProgress 相关的请求/响应模型
- [x] 1.4 更新 `schemas.py`：扩展 Quiz 支持多题型（question_type, options, is_correct）

## 2. 词库数据

- [x] 2.1 更新 `words.json` 格式（按新数据结构）
- [x] 2.2 添加示例词语：比、鄙、兵、病、乘

## 3. 后端核心逻辑

- [x] 3.1 重写 `spaced_repetition.py`：实现天级间隔算法（1/2/4/7/15/30天）
- [x] 3.2 实现 `word_loader.py`：加载新格式的 words.json
- [x] 3.3 实现 `quiz.py`：学新词 API（卡片模式，顺序/随机，数量可配置）
- [x] 3.4 实现 `quiz.py`：多题型出题 API（根据级别返回对应题型）
- [x] 3.5 实现 `quiz.py`：答题提交 API（记录结果，处理答错重做）
- [x] 3.6 实现 `review.py`：复习列表 API（查询到期词，按级别分组）
- [x] 3.7 实现 `progress.py`：学习进度 API（当前轮次，完成百分比）

## 4. 前端路由和状态管理

- [x] 4.1 更新 `router/index.ts`：新增 /learn 和 /progress 路由
- [x] 4.2 更新 `quiz.ts` store：支持多题型状态管理
- [x] 4.3 新增 `learn.ts` store：学新词状态管理
- [x] 4.4 新增 `progress.ts` store：学习进度状态管理

## 5. 前端组件

- [x] 5.1 新增 `LearnView.vue`：学新词页面（卡片模式）
- [x] 5.2 新增 `CardView.vue`：卡片组件（正面/背面翻转）
- [x] 5.3 新增 `FlashcardView.vue`：闪卡组件
- [x] 5.4 更新 `QuizView.vue`：支持单选题和判断题
- [x] 5.5 更新 `ReviewView.vue`：按级别分组显示复习列表
- [x] 5.6 新增 `ProgressView.vue`：学习进度页面

## 6. 测试

- [x] 6.1 后端单元测试：间隔重复算法（30个测试通过）
- [x] 6.2 后端单元测试：多题型出题逻辑（已包含在6.1中）
- [ ] 6.3 后端集成测试：完整学习流程（需更复杂的mock设置，暂跳过）
- [ ] 6.4 前端组件测试：卡片翻转交互（需配置vitest组件测试，暂跳过）
