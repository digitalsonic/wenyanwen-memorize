# 文言文实词虚词记忆工具

基于错误驱动和艾宾浩斯遗忘曲线的 Web 记忆辅助工具。

## 项目结构

```
wenyanwen-memorize/
├── backend/          # FastAPI 后端
│   ├── src/
│   │   └── wenyanwen/
│   ├── data/         # 词库数据
│   └── tests/
└── frontend/         # Vue.js 前端
    └── src/
```

## 技术栈

### 后端
- Python 3.11+
- FastAPI
- SQLModel (SQLite)
- Pydantic Settings

### 前端
- Vue 3
- TypeScript
- Vite
- Pinia
- Vue Router
- Axios

## 快速开始

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 安装依赖（包含开发依赖）
pip install -e ".[dev]"

# 安装 pre-commit hooks
pre-commit install

# 复制环境变量配置
cp .env.example .env

# 运行开发服务器
python -m wenyanwen
# 或使用 uvicorn 直接运行
uvicorn wenyanwen.main:create_app --reload
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test
```

## 开发工具

### 后端
- **ruff**: 代码格式化和 lint
- **mypy**: 类型检查
- **pytest**: 单元测试

```bash
cd backend
ruff check .           # 检查代码
ruff format .          # 格式化代码
mypy src/              # 类型检查
pytest                 # 运行测试
```

### 前端
- **ESLint**: 代码检查
- **Prettier**: 代码格式化
- **Vitest**: 单元测试

```bash
cd frontend
npm run lint           # 检查代码
npm run lint:fix       # 修复 lint 问题
npm run format         # 格式化代码
npm run test           # 运行测试
```

## 词库格式

词库文件位于 `backend/data/words.json`，格式如下：

```json
{
  "words": [
    {
      "word": "之",
      "type": "虚词",
      "meanings": [
        {
          "meaning": "代词：代人、代事、代物",
          "examples": ["例句1", "例句2"]
        }
      ],
      "level": "common"
    }
  ]
}
```

## API 文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

## 许可证

MIT
