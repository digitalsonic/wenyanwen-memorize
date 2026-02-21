## ADDED Requirements

### Requirement: 词库数据结构
系统 SHALL 使用 JSON 格式存储词库，每个词包含：id、word、type、pinyin、meanings（义项列表）、mnemonics（助记口诀）。

#### Scenario: 读取词库数据
- **WHEN** 系统启动或需要词库数据
- **THEN** 系统从 `data/words.json` 加载所有词语

#### Scenario: 单词结构验证
- **WHEN** 系统加载词库
- **THEN** 每个词必须包含：id（唯一）、word（字）、type（实词/虚词）、meanings（至少一个义项）

---

### Requirement: 义项数据结构
每个义项 SHALL 包含：id（唯一）、definition（释义）、examples（例句列表）。

#### Scenario: 义项唯一标识
- **WHEN** 系统加载词库
- **THEN** 每个义项的 id 在全局范围内唯一

#### Scenario: 例句结构
- **WHEN** 系统读取例句
- **THEN** 每个例句包含：sentence（原文）、source（完整出处，如"满江红•小住京华 （九下）（非考试篇目）"）

---

### Requirement: 词库扩展示例
系统 SHALL 包含示例词语：比、鄙、兵、病、乘（最终扩展至约150个词）。

#### Scenario: 示例词"比"
- **WHEN** 用户学习"比"字
- **THEN** 系统显示3个义项：①靠近 ②及，等到 ③比较，各自配有例句

#### Scenario: 示例词"鄙"
- **WHEN** 用户学习"鄙"字
- **THEN** 系统显示1个义项：浅陋，目光短浅

#### Scenario: 示例词"兵"
- **WHEN** 用户学习"兵"字
- **THEN** 系统显示4个义项：①兵器 ②军队 ③士兵 ④战争

#### Scenario: 示例词"病"
- **WHEN** 用户学习"病"字
- **THEN** 系统显示2个义项：①生病 ②枯萎

#### Scenario: 示例词"乘"
- **WHEN** 用户学习"乘"字
- **THEN** 系统显示3个义项：①坐、驾（车） ②趁着，冒着 ③辆（量词）
