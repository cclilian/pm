# PM - 软件集成项目管理平台

基于 Vue3 + FastAPI + MySQL 的软件集成项目管理软件。

## 功能概览

- **需求管理**：核心/非核心业务需求分类、拆解为任务、支持取消
- **任务管理**：多来源任务（需求拆解、项目内、项目外、临时任务）、工时与状态追踪
- **产品规划**：版本路线图，规划各版本需完成的需求
- **迭代管理**：版本拆分为多个迭代，迭代关联需求与任务
- **统计报表**：任务总览、迭代进度、人员工作量

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Vite + TypeScript + Element Plus + Pinia |
| 后端 | FastAPI + SQLAlchemy 2.0 + Alembic + Pydantic v2 |
| 数据库 | MySQL 8.x |

## 项目结构

```
pm/
├── frontend/          # Vue3 前端
├── backend/           # FastAPI 后端
├── docker-compose.yml # MySQL（可选）
└── .cursor/           # Cursor 规则与计划
```

## 快速开始

### 1. 数据库

使用本地 MySQL（默认 `root/123456`）或 Docker：

```bash
docker compose up -d
```

创建数据库（若尚未创建）：

```sql
CREATE DATABASE pm DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

## 详细规划

参见 [.cursor/plans/pm系统模块规划_0c172c03.plan.md](.cursor/plans/pm系统模块规划_0c172c03.plan.md)
