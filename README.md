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
├── docker-compose.yml # MySQL（在 WSL2 中 docker compose up -d）
└── .cursor/           # Cursor 规则与计划
```

## 快速开始

### 1. 数据库（WSL2 Docker）

MySQL 在 **WSL2 里用 Docker** 启动，不在 Windows 本机跑 Docker。

**在 WSL2 终端中启动：**

```bash
# 进入项目目录（Windows 路径挂载示例）
cd /mnt/d/congchen-study/cursor-test/pm
docker compose up -d
```

确认容器运行：

```bash
docker ps   # 应看到 mysql，端口 0.0.0.0:3306->3306
```

数据库名：`agile_pm`（连接串见 `backend/.env.example`）

**Windows 后端连 WSL2 里的 MySQL**

后端在 Windows 跑、MySQL 在 WSL2 Docker 跑时，需让 Windows 能访问 `3306`：

1. **推荐**：启用 WSL 镜像网络（Windows 11），编辑 `%USERPROFILE%\.wslconfig`：

   ```ini
   [wsl2]
   networkingMode=mirrored
   localhostForwarding=true
   ```

   保存后执行 `wsl --shutdown`，再重新打开 WSL。之后 Windows 可用 `localhost:3306` 连接。

2. **备选**：在 `backend/.env` 里把主机改为 WSL IP（重启 WSL 后可能变化）：

   ```bash
   wsl hostname -I   # 取第一个 IP
   ```

   ```env
   DATABASE_URL=mysql+pymysql://root:123456@<WSL_IP>:3306/agile_pm
   ```

创建数据库（若容器内尚未创建）：

```sql
CREATE DATABASE agile_pm DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

在 WSL 内可验证连通：

```bash
docker exec mysql mysql -uroot -p123456 -e "SHOW DATABASES;"
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
