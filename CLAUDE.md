# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

文言文实词虚词记忆工具 - 基于**错误驱动**和**艾宾浩斯遗忘曲线**的 Web 应用。

核心机制：用户答题错误时记录"薄弱义项"，根据遗忘曲线算法（`services/spaced_repetition.py`）计算下次复习时间，在复习列表中针对性展示。

## 常用命令

**Python 版本：** 3.11+

### 后端

```bash
cd backend

# 开发
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m wenyanwen          # 启动服务（默认 http://localhost:8000）

# 代码质量
ruff check .                 # Lint 检查
ruff format .                # 格式化
mypy src/                    # 类型检查（严格模式）
pre-commit run --all-files   # 运行 pre-commit hooks

# 测试
pytest                       # 全部测试
pytest tests/test_api/       # 特定目录
pytest -k "health"           # 匹配名称的测试
pytest --cov                # 覆盖率报告
```

### 前端

```bash
cd frontend

npm install
npm run dev                  # 启动开发服务器（默认 http://localhost:5173）
npm run build                # 生产构建
npm run lint                 # ESLint 检查
npm run lint:fix             # 自动修复
npm run format               # Prettier 格式化
npm run test                 # Vitest 测试
```

## 架构概览

### 后端架构

```
main.py (create_app)
    ├── api/v1/
    │   ├── quiz.py      # 答题 API（出题、提交答案）
    │   └── review.py    # 复习 API（获取复习列表）
    ├── services/
    │   ├── word_loader.py         # 从 JSON 加载词库
    │   └── spaced_repetition.py   # 艾宾浩斯间隔重复算法
    ├── models.py       # SQLModel 表定义（User, QuizRecord, WeakMeaning）
    ├── schemas.py      # Pydantic API 请求/响应模型
    ├── database.py     # SQLite 引擎
    └── config.py       # pydantic-settings 配置
```

**核心数据流：**
1. `word_loader` 从 `data/words.json` 加载词库
2. `quiz.py` 生成选择题，用户提交答案后记录到 `QuizRecord` 和 `WeakMeaning`
3. `spaced_repetition.calculate_next_review()` 根据对错计算下次复习时间
4. `review.py` 查询 `WeakMeaning` 表，返回到期的复习项

**间隔重复算法：**
- 6 个等级，答对升级，答错重置为等级 1
- 间隔：5分钟 → 1小时 → 6小时 → 1天 → 2天 → 4天

### 前端架构

```
App.vue
    ├── router/
    │   └── index.ts    # 路由：/ (练习) → QuizView, /review (复习) → ReviewView
    ├── stores/
    │   ├── quiz.ts     # 答题状态管理
    │   └── user.ts     # 用户复习状态
    ├── api/
    │   └── client.ts   # Axios 封装，代理 /api/v1 → 后端
    └── views/
        ├── QuizView.vue    # 答题页面
        └── ReviewView.vue  # 复习列表页面
```

**Vite 代理配置：** 前端 `/api/v1/*` 请求代理到 `http://localhost:8000`

## 词库格式

`backend/data/words.json`：

```json
{
  "words": [
    {
      "word": "之",
      "type": "虚词",
      "meanings": [
        {
          "meaning": "代词：代人、代事、代物",
          "examples": ["例句..."]
        }
      ],
      "level": "common"
    }
  ]
}
```

## 配置说明

- **后端配置：** `backend/.env` （从 `.env.example` 复制）
- **前端代理：** `frontend/vite.config.js`
- **TypeScript 严格模式**已启用
- **MyPy 严格模式**已启用
