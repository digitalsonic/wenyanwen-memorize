# 文言文实词虚词记忆工具 - 后端服务

FastAPI 后端服务，提供答题和复习 API。

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 运行

```bash
python -m wenyanwen
```

API 文档: http://localhost:8000/docs

## 开发工具

- `ruff check .` - 代码检查
- `ruff format .` - 代码格式化
- `mypy src/` - 类型检查
- `pytest` - 运行测试
