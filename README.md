# 智能电商秒杀系统

基于 FastAPI + LangGraph 开发的电商秒杀系统，集成 AI 决策助手，支持高并发秒杀和智能优惠券推荐。

## 技术栈

- **FastAPI** — 后端框架，异步高性能
- **LangGraph** — AI Agent 框架，工具调用 + 流式输出
- **PostgreSQL** — 主数据库
- **Redis** — 库存缓存 + 限购校验
- **Celery** — 异步任务队列
- **Docker** — 容器化部署

## 核心功能

- 用户注册、登录、JWT 认证
- 商品管理
- 秒杀活动（Redis Lua 原子操作防超卖）
- 订单管理（Celery 异步创建，超时自动取消）
- 优惠券系统（全场券 + 指定商品券）
- AI 决策助手（查商品、查秒杀、算最优券组合）

## 启动方式

### 1. 启动数据库和 Redis

\```bash
docker-compose up -d
\```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写：

\```
DATABASE_URL=postgresql://postgres:password@localhost/seckill
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=你的随机密钥
DASHSCOPE_API_KEY=你的通义千问Key
\```

### 3. 数据库迁移

\```bash
python -m alembic upgrade head
\```

### 4. 启动服务

\```bash
# 启动 FastAPI
python -m uvicorn main:app --reload

# 启动 Celery Worker（新终端）
python -m celery -A celery_app worker --loglevel=info -P solo
\```

### 5. 访问文档

打开 http://localhost:8000/docs

## 项目亮点

- Redis Lua 脚本原子操作，防止高并发超卖
- Celery 异步创建订单，削峰填谷
- Celery 延时任务，30分钟未支付自动释放库存
- LangGraph Agent 自动调用工具，计算最优购买方案
- FastAPI SSE 流式输出，实时推送 AI 回答